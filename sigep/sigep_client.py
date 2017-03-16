# coding: utf-8
import StringIO
import logging
import os

from jinja2 import Template
from lxml import etree
from suds import WebFault
from suds.client import Client

logger = logging.getLogger('sigep.webservice')


class Sigep(object):
    SIGEP_SANDBOX_URL = 'https://apphom.correios.com.br/SigepMasterJPA/AtendeClienteService/AtendeCliente?wsdl'
    SIGEP_PRODUCTION_URL = 'https://apps.correios.com.br/SigepMasterJPA/AtendeClienteService/AtendeCliente?wsdl'
    validade_xsd = 'sigepy/xml/schema.xsd'

    def __init__(self, contract, cnpj, user, password, card, origin_zipcode, admin_code, regional_code, sender_info,
                 sandbox=False):
        """
        Cliente para o SIGEP (Sistema de Gerenciamento de Postagens) dos correios

        :param contract:
        :param cnpj: CNPJ do usuário
        :param user: Nome do usuário
        :param password: Senha de acesso
        :param card:
        :param origin_zipcode: CEP de origem
        :param admin_code:
        :param regional_code:
        :param sender_info: (name, street, number, complement, neighborhood, zipcode, city, state, phone, fax, email)
        :param sandbox: Modo sandbox, para testes
        """
        self.url = self.SIGEP_SANDBOX_URL if sandbox else self.SIGEP_PRODUCTION_URL
        self.contract = contract
        self.cnpj = cnpj
        self.user = user
        self.password = password
        self.card = card
        self.origin_zipcode = origin_zipcode
        self.admin_code = admin_code
        self.regional_code = regional_code
        self.sender_info = sender_info

        self.client = Client(self.url, location=self.url.replace('?wsdl', ''))

    def _remove_dv_tracking_code(self, tracking_code):
        """

        :param tracking_code: Código de rastreio com digito a ser removido
        :return: código de rastreio sem digito
        """
        return '%s%s' % (tracking_code[:-3], tracking_code[-2:])

    def _validate_xml(self, xml):
        """
        Valida se o XML da PLP é valido baseado no schema.xsd se for valido não retorna nada

        :param xml: XML que contém a PLP gerada
        :return:
        :raises: AssertException, se inválido
        """
        filename = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), self.validade_xsd)

        parsed_file = etree.parse(filename)
        schema = etree.XMLSchema(etree=parsed_file)

        doc = etree.parse(StringIO.StringIO(xml))
        schema.assertValid(doc)

    def request_xml_plp(self, plp_number, tracking_code_list):
        """
        Consulta PLP já gerada

        :param plp_number: Número da PLP gerada
        :param tracking_code_list: lista de códigos de rastreio
        :return: XML contendo as PLPs geradas para os códigos de rastreio informados
        """
        plp = self.client.service.solicitaPLP(
            numEtiqueta=tracking_code_list,
            idPlpMaster=plp_number,
            usuario=self.user,
            senha=self.password
        )
        logger.info(u'request_xml_plp for PLP {} and tracking_code_list: {}'.format(
            plp_number,
            tracking_code_list,
        ))
        return plp

    def search_service(self):
        """
        Lista os serviços disponíveis para um determinado contrato

        :return: XML com os serviços disponíveis para o contrato
        """
        return self.client.service.buscaServicos(
            idContrato=self.contract,
            idCartaoPostagem=self.card,
            usuario=self.user,
            senha=self.password,
        )

    def check_service_available(self, code, zip_code):
        """
        Consulta a disponibilidade de um serviço para um determinado CEP.

        :param code: Código do serviço
        :param zip_code: CEP
        :return: {'mensagem_erro': 'mensagem do erro'}, ou False, se offline
        """
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

        except WebFault as e:
            logger.error(u'check_service_available WebFault Exception: {} for code {}'.format(e, code))
            return False

    def get_client_data(self):
        """
        Busca dados do usuário no SIGEP

        :return: XML contendo informações dos contratos do cliente
        """
        return self.client.service.buscaCliente(
            idContrato=self.contract,
            idCartaoPostagem=self.card,
            usuario=self.user,
            senha=self.password,
        )

    def request_tracking_codes(self, service_id, amount=1):
        """
        Solicita novos códigos de rastreio para as etiquetas

        :param service_id: ID do serviço (PAC, SEDEX)
        :param amount: Quantidade de etiquetas a serem geradas
        :return: lista com as etiquetas já com o digito verificador.
        """
        post = self.client.service.solicitaEtiquetas(
            tipoDestinatario='C',
            identificador=self.cnpj,
            idServico=service_id,
            usuario=self.user,
            senha=self.password,
            qtdEtiquetas=amount,
        )
        code = post.split(',')
        if amount == 1:
            return [code[0]]
        return code

    def generate_verification_code(self, tracking_code):
        """
        Gera dígito verificador para um determinado código de rastreio

        :param tracking_code: Código de rastreio sem digito verificador
        :return: Código de rastreio com digito verificador
        """
        verification = self.client.service.geraDigitoVerificadorEtiquetas(
            usuario=self.user,
            senha=self.password,
            etiquetas=tracking_code,
        )
        return tracking_code.replace(' ', str(verification[0]))

    def get_new_tracking_code(self, service_id):
        """
        Utiliza os serviços do SIGEP para gerar um código de rastreio com dígito verificador

        :param service_id: ID do serviço (PAC, SEDEX)
        :return: Código de rastreio com dígito verificador
        """
        code = self.request_tracking_codes(service=service_id)
        return self.generate_verification_code(code[0])

    def create_plp(self, intern_plp_number, object_list):
        """
        Gera uma nova PLP (Pré Lista de Postagem)

        :param intern_plp_number: Número de controle interno sequêncial para a geração da PLP
        :param object_list:
        :return:
        """
        data = {
            'card': self.card,
            'contract': self.contract,
            'reginal_code': self.regional_code,
            'admin_code': self.admin_code,
            'sender_info': self.sender_info,
            'object_list': object_list,
        }

        xml = Template('sigep/xml/plp.xml', data)
        xml = xml.encode('ascii', 'xmlcharrefreplace')
        xml = xml.replace("  ", "")
        xml = xml.replace('\n', '')
        xml = xml.replace('\t', '')
        xml = xml.replace("> <", "><")

        self._validate_xml(xml)

        tracking_code_list = []
        for item in object_list:
            tracking_code = self._remove_dv_tracking_code(item.get('tracking_code'))
            tracking_code_list.append(tracking_code)

        logger.info(u'create_plp - xml: {} tracking_code_list: {}'.format(
            xml,
            ', '.join(tracking_code_list),
        ))

        plp_id = self.client.service.fechaPlpVariosServicos(
            xml=xml,
            idPlpCliente=intern_plp_number,
            cartaoPostagem=self.card,
            listaEtiquetas=tracking_code_list,
            usuario=self.user,
            senha=self.password,
        )

        logger.info(u'create_plp - tracking_code_list: {} plp: {}'.format(', '.join(tracking_code_list), plp_id))

        return {
            'plp_id': plp_id,
            'tracking_code_list': tracking_code_list,
        }
