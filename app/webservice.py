# coding: utf-8
import os
from app import choices

"""
SIGEP_SKIP_VALIDATION = True

SIGEP_CEP_ORIGIN = '14401426'  # OK
SIGEP_CARD = '0070490287'  # OK
SIGEP_ADMINISTRATION_CODE = '14502607'  # OK
SIGEP_CONTRACT = '9912366511'  # OK
SIGEP_CNPJ = '20023005000147'  # OK
SIGEP_REGIONAL_BOARD_CODE = '00074'
SIGEP_MAX_RESULTS = 1000

SIGEP_STORE_LOGO = 'https://pr-ahimsa.s3-sa-east-1.amazonaws.com/static/img/logo_footer.png'  # Logo pendente
SIGEP_CHANCELA_STATE = 'SPI'
"""


class Sigep(object):
    schematron = None
    validade_xsd = 'templates/commerce_correios_sigep/xml/schema.xsd'

    def __init__(self, user, password,  sandbox=False):
        if sandbox:
            self.url = choices.SIGEP_SANDBOX_URL
        else:
            self.url = choices.SIGEP_PRODUCTION_URL

        self.user = user
        self.password = password

        self.client = Client(
            self.url,
            location=self.url.replace('?wsdl', '')
        )

    def get_xml_plp(self, plp):
        return self.client.service.solicitaPLP(
            numEtiqueta=[i.tracking_code for i in plp.sigeporderinline_set.all()],
            idPlpMaster=long(plp.plp), usuario=SIGEP_USER, senha=SIGEP_PASSWORD)

    def validate_xml(self, xml):
        filename = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)), self.validade_xsd)
        sct_doc = etree.parse(filename)

        schema = etree.XMLSchema(etree=sct_doc)

        doc = etree.parse(StringIO.StringIO(xml))
        schema.assertValid(doc)

    def get_plp_data(self, qs):
        return {
            'SIGEP_CARD': choices.SIGEP_CARD,
            'SIGEP_CONTRACT': choices.SIGEP_CONTRACT,
            'SIGEP_REGIONAL_BOARD_CODE': choices.SIGEP_REGIONAL_BOARD_CODE,
            'SIGEP_ADMINISTRATION_CODE': choices.SIGEP_ADMINISTRATION_CODE,
            'SIGEP_STORE_INFORMATION': choices.SIGEP_STORE_INFORMATION,
            'object_list': qs,
        }

    def create_plp(self, qs, user):

        from models import Plp, get_plp_intern

        template = 'commerce_correios_sigep/xml/plp.xml'
        data = self.get_plp_data(qs)

        xml = render_to_string(template, data)
        xml = xml.encode('ascii', 'xmlcharrefreplace')

        xml = xml.replace("  ", "")
        xml = xml.replace('\n', '')
        xml = xml.replace('\t', '')
        xml = xml.replace("> <", "><")
        self.validate_xml(xml)

        tracking_code = [i.remove_dv_tracking_code() for i in qs]

        logger.info(u'STARTS create_plp user: {0} xml: {1} tracking_code: {2}'.format(
            user,
            xml,
            ';'.join(tracking_code),
        ))

        plp = Plp(user=user)
        plp_intern = get_plp_intern()

        plp_number = self.client.service.fechaPlpVariosServicos(
            xml=xml,
            idPlpCliente=long(plp_intern),
            cartaoPostagem=SIGEP_CARD,
            listaEtiquetas=tracking_code,
            usuario=self.user,
            senha=self.password,
        )
        plp.plp = plp_number
        plp.plp_intern = plp_intern
        plp.save()

        logger.info(u'RESPONSE create_plp user: {0} tracking_code: {1} plp: {2} plp_intern: {3}'.format(
            user,
            ';'.join(tracking_code),
            plp_number,
            plp_intern
        ))

        return plp

    def consult_tracking_code(self, tracking_code):
        return check_tracking_code(tracking_code)

    def search_service(self):
        return self.client.service.buscaServicos(
            idContrato=SIGEP_CONTRACT,
            idCartaoPostagem=SIGEP_CARD,
            usuario=self.user,
            senha=self.password,
        )

    def check_service_available(self, code, zipCodeDest):
        if SIGEP_SKIP_VALIDATION:
            return True

        zipCodeDest = zipCodeDest.replace('-', '')
        zipCodeDest = zipCodeDest.rjust(8, '0')

        try:
            response = self.client.service.verificaDisponibilidadeServico(
                codAdministrativo=SIGEP_ADMINISTRATION_CODE,
                numeroServico=code,
                cepOrigem=SIGEP_CEP_ORIGIN,
                cepDestino=zipCodeDest,
                usuario=self.user,
                senha=self.password,
            )
            logger.info(u'check_service_available for code {0} and zipCodeDest {1}: {2}'.format(
                code,
                zipCodeDest,
                response,
            ))
            return response
        except WebFault, e:
            logger.info(u'check_service_available WebFault Exception: {0}'.format(code))
            logger.info(u'{0}'.format(e))
            return False

    def check_client_service(self):
        resp = self.client.service.buscaCliente(
            idContrato=SIGEP_CONTRACT,
            idCartaoPostagem=SIGEP_CARD,
            usuario=self.user,
            senha=self.password,
        )

    def get_post_code(self, service, qty=1):
        post = self.client.service.solicitaEtiquetas(
            tipoDestinatario='C',
            identificador=SIGEP_CNPJ,
            idServico=service,
            qtdEtiquetas=qty,
            usuario=self.user,
            senha=self.password,
        )
        code = post.split(',')
        if qty == 1:
            return [code[0]]
        return code

    def get_verification_code(self, code):
        verification = self.client.service.geraDigitoVerificadorEtiquetas(
            etiquetas=code,
            usuario=self.user,
            senha=self.password,
        )
        return code.replace(' ', str(verification[0]))

    def get_tracking_code(self, service):
        code = self.get_post_code(service=service)
        return self.get_verification_code(code[0])
