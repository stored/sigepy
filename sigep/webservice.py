# coding: utf-8
import os
import logging
from sigep import choices
# TODO change to zeep Xcode problem
from suds import WebFault
from suds.client import Client

from jinja2 import Template

"""
SIGEP_MAX_RESULTS = 1000
SIGEP_STORE_LOGO = 'https://pr-ahimsa.s3-sa-east-1.amazonaws.com/static/img/logo_footer.png'  # Logo pendente
SIGEP_CHANCELA_STATE = 'SPI'
"""

logger = logging.getLogger('sigep.webservice')


class Sigep(object):
    schematron = None
    validade_xsd = 'templates/commerce_correios_sigep/xml/schema.xsd'

    def __init__(self, contract, cnpj, user, password, card, origin_zipcode,admin_code, reginal_code, store_info, sandbox=False):
        if sandbox:
            self.url = choices.SIGEP_SANDBOX_URL
        else:
            self.url = choices.SIGEP_PRODUCTION_URL

        self.contract = contract
        self.cnpj = cnpj
        self.user = user
        self.password = password
        self.card = card
        self.origin_zipcode = origin_zipcode
        self.admin_code = admin_code
        self.reginal_code = reginal_code
        self.store_info = store_info

        self.client = Client(
            self.url,
            location=self.url.replace('?wsdl', '')
        )

    def get_xml_plp(self, plp_number, trackin_code_list):
        return self.client.service.solicitaPLP(
            numEtiqueta=trackin_code_list,
            idPlpMaster=plp_number,
            usuario=self.user,
            senha=self.password
        )

    # def validate_xml(self, xml):
    #     filename = os.path.join(os.path.dirname(
    #         os.path.abspath(__file__)), self.validade_xsd)
    #     sct_doc = etree.parse(filename)

    #     schema = etree.XMLSchema(etree=sct_doc)

    #     doc = etree.parse(StringIO.StringIO(xml))
    #     schema.assertValid(doc)

    def search_service(self):
        return self.client.service.buscaServicos(
            idContrato=self.contract,
            idCartaoPostagem=self.card,
            usuario=self.user,
            senha=self.password,
        )

    def check_service_available(self, code, zip_code):
        zip_code = zip_code.replace('-', '')
        zip_code = zip_code.rjust(8, '0')

        try:
            response = self.client.service.verificaDisponibilidadeServico(
                codAdministrativo=self.admin_code,
                cepOrigem=self.origin_zipcode,
                usuario=self.user,
                senha=self.password,
                cepDestino=zip_code,
                numeroServico=code,
            )
            logger.info(u'check_service_available for code {0} and zip_code {1}: {2}'.format(
                code,
                zip_code,
                response,
            ))
            return response

        except WebFault as exception:
            logger.info(u'check_service_available WebFault Exception: {0}'.format(code))
            logger.info(u'{0}'.format(exception))
            return False

    def check_client_service(self):
        self.client.service.buscaCliente(
            idContrato=self.contract,
            idCartaoPostagem=self.card,
            usuario=self.user,
            senha=self.password,
        )

    def get_post_code(self, service, qty=1):
        post = self.client.service.solicitaEtiquetas(
            tipoDestinatario='C',
            identificador=self.cnpj,
            idServico=service,
            usuario=self.user,
            senha=self.password,
            qtdEtiquetas=qty,
        )
        code = post.split(',')
        if qty == 1:
            return [code[0]]
        return code

    def get_verification_code(self, code):
        verification = self.client.service.geraDigitoVerificadorEtiquetas(
            usuario=self.user,
            senha=self.password,
            etiquetas=code,
        )
        return code.replace(' ', str(verification[0]))

    def get_tracking_code(self, service):
        code = self.get_post_code(service=service)
        return self.get_verification_code(code[0])

    def _remove_dv_tracking_code(self, tracking_code):
        return '%s%s' % (tracking_code[:-3], tracking_code[-2:])

    def create_plp(self, item_list):
        data = {
            'SIGEP_CARD': self.card,
            'SIGEP_CONTRACT': self.contract,
            'SIGEP_REGIONAL_BOARD_CODE': self.reginal_code,
            'SIGEP_ADMINISTRATION_CODE': self.admin_code,
            'SIGEP_STORE_INFORMATION': self.store_info,
            'item_list': item_list,
        }

        xml = Template('sigep/xml/plp.xml', data)
        # xml = xml.encode('ascii', 'xmlcharrefreplace')
        # xml = xml.replace("  ", "")
        # xml = xml.replace('\n', '')
        # xml = xml.replace('\t', '')
        # xml = xml.replace("> <", "><")

        # self.validate_xml(xml)

        tracking_code_list = []
        for item in item_list:
            tracking_code = self._remove_dv_tracking_code(item.get('tracking_code'))
            tracking_code_list.append(tracking_code)

        logger.info(u'create_plp - xml: {} tracking_code: {}'.format(
            xml,
            ';'.join(tracking_code_list),
        ))

        # plp = Plp(user=user)
        # plp_intern = get_plp_intern()

        plp_number = self.client.service.fechaPlpVariosServicos(
            xml=xml,
            idPlpCliente=long(plp_intern),
            cartaoPostagem=self.card,
            listaEtiquetas=tracking_code_list,
            usuario=self.user,
            senha=self.password,
        )
        # plp.plp = plp_number
        # plp.plp_intern = plp_intern
        # plp.save()

        logger.info(u'RESPONSE create_plp user: {0} tracking_code: {1} plp: {2} plp_intern: {3}'.format(
            user,
            ';'.join(tracking_code_list),
            plp_number,
            plp_intern
        ))

        return plp

    # def consult_tracking_code(self, tracking_code):
    #     return check_tracking_code(tracking_code)
