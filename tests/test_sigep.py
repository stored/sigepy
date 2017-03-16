# coding: utf-8

import pytest
import httpretty


dev = {
    'contract': '0042',
    'cnpj': '0000.0000/0000-00',
    'user': 'sigepy', 'password': 'sigepy@pass',
    'origin_zipcode': '14020273',
    'card': '0001', 'admin_code': '0001', 'regional_code': 60,
    'sender_info': {
        'name': 'Sigepy',
        'street': 'Av Presidente Vargas',
        'number': '1265',
        'complement': 'Cj 401',
        'neighborhood': '',
        'zipcode': '14020273',
        'city': u'Ribeirão Preto',
        'state': 'SP',
        'phone': '',
        'fax': '',
        'email': 'dev@stored.com.br',
    }
}


def fake_body(content='OK', tag='ID'):
    return """
        <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cli="http://cliente.bean.master.sigep.bsb.correios.com.br/">
            <x:Body>
                <cli:verificaDisponibilidadeServico>
                    <x:{tag}>{content}</x:{tag}>
                </cli:verificaDisponibilidadeServico>
            </x:Body>
        </x:Envelope>
        """.format(content=str(content), tag=tag)

SOAP_URL = 'https://apps.correios.com.br/SigepMasterJPA/AtendeClienteService/AtendeCliente'


class TestSigep:
    @pytest.fixture
    def client(self):
        from sigep.sigep_client import Sigep
        client = Sigep(**dev)
        return client

    def test_available_services(self, client):
        httpretty.enable()
        data = """
               <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cli="http://cliente.bean.master.sigep.bsb.correios.com.br/">
                    <x:Header/>
                    <x:Body>
                        <cli:buscaServicos>
                            <idContrato>{contract}</idContrato>
                            <idCartaoPostagem>{card}</idCartaoPostagem>
                            <usuario>{user}</usuario>
                            <senha>{password}</senha>
                        </cli:buscaServicos>
                    </x:Body>
                </x:Envelope>
               """.format(contract=client.contract, card=client.card, user=client.user, password=client.password)
        body = """
        <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cli="http://cliente.bean.master.sigep.bsb.correios.com.br/">
            <x:Body>
                <cli:buscaServicos>
                    <x:ID>SEDEX</x:ID>
                    <x:ID>PAC</x:ID>
                </cli:buscaServicos>
            </x:Body>
        </x:Envelope>
        """
        httpretty.register_uri(httpretty.POST, SOAP_URL, data=data, body=body)

        data = client.search_service()
        assert data == ['SEDEX', 'PAC']

    def test_service_is_available(self, client):
        httpretty.disable()
        data = client.check_service_available(code='1', zip_code='37902000')
        assert data is False

        httpretty.enable()
        data = """
               <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cli="http://cliente.bean.master.sigep.bsb.correios.com.br/">
                    <x:Header/>
                    <x:Body>
                        <cli:verificaDisponibilidadeServico>
                            <codAdministrativo>{admin_code}</codAdministrativo>
                            <numeroServico>{service_number}</numeroServico>
                            <cepOrigem>{from_zip}</cepOrigem>
                            <cepDestino>{to_zip}</cepDestino>
                            <usuario>{user}</usuario>
                            <senha>{password}</senha>
                        </cli:verificaDisponibilidadeServico>
                    </x:Body>
                </x:Envelope>
               """.format(admin_code=client.admin_code, user=client.user, password=client.password, service_number='1', from_zip='14020273', to_zip='37902000')
        body = fake_body()
        httpretty.register_uri(httpretty.POST, SOAP_URL, data=data, body=body)

        data = client.check_service_available(code='1', zip_code='37902000')
        assert data == 'OK'

    def test_search_client(self, client):
        httpretty.enable()
        data = """
               <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cli="http://cliente.bean.master.sigep.bsb.correios.com.br/">
                    <x:Header/>
                    <x:Body>
                        <cli:buscaCliente>
                            <idContrato>{contract}</idContrato>
                            <idCartaoPostagem>{card}</idCartaoPostagem>
                            <usuario>{user}</usuario>
                            <senha>{password}</senha>
                        </cli:buscaCliente>
                    </x:Body>
                </x:Envelope>
               """.format(contract=client.contract, card=client.card, user=client.user, password=client.password)
        body = fake_body()
        httpretty.register_uri(httpretty.POST, SOAP_URL, data=data, body=body)

        data = client.get_client_data()
        assert data == 'OK'

    def test_request_tracking_codes(self, client):
        httpretty.enable()
        data = """
               <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cli="http://cliente.bean.master.sigep.bsb.correios.com.br/">
                    <x:Header/>
                    <x:Body>
                        <cli:solicitaEtiquetas>
                            <tipoDestinatario>{destination_type}</tipoDestinatario>
                            <identificador>{identifier}</identificador>
                            <idServico>{service_id}</idServico>
                            <qtdEtiquetas>{qty}</qtdEtiquetas>
                            <usuario>{user}</usuario>
                            <senha>{password}</senha>
                        </cli:solicitaEtiquetas>
                    </x:Body>
                </x:Envelope>
               """.format(user=client.user, password=client.password, destination_type='1', identifier='001', service_id=7, qty=1)
        body = fake_body()
        httpretty.register_uri(httpretty.POST, SOAP_URL, data=data, body=body)

        # multiple at once
        data = client.request_tracking_codes(service_id=7)
        assert data == ['OK']

    def test_new_tracking_code(self, client):
        httpretty.enable()
        data = """
                       <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cli="http://cliente.bean.master.sigep.bsb.correios.com.br/">
                            <x:Header/>
                            <x:Body>
                                <cli:buscaCliente>
                                    <idContrato>{contract}</idContrato>
                                    <idCartaoPostagem>{card}</idCartaoPostagem>
                                    <usuario>{user}</usuario>
                                    <senha>{password}</senha>
                                </cli:buscaCliente>
                            </x:Body>
                        </x:Envelope>
                       """.format(contract=client.contract, card=client.card, user=client.user,
                                  password=client.password)
        body = fake_body(42)
        httpretty.register_uri(httpretty.POST, SOAP_URL, data=data, body=body)

        httpretty.enable()
        data = """
                       <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cli="http://cliente.bean.master.sigep.bsb.correios.com.br/">
                            <x:Header/>
                            <x:Body>
                                <cli:solicitaEtiquetas>
                                    <tipoDestinatario>{destination_type}</tipoDestinatario>
                                    <identificador>{identifier}</identificador>
                                    <idServico>{service_id}</idServico>
                                    <qtdEtiquetas>{qty}</qtdEtiquetas>
                                    <usuario>{user}</usuario>
                                    <senha>{password}</senha>
                                </cli:solicitaEtiquetas>
                            </x:Body>
                        </x:Envelope>
                       """.format(user=client.user, password=client.password, destination_type='1', identifier='001',
                                  service_id=7, qty=1)
        body = fake_body()
        httpretty.register_uri(httpretty.POST, SOAP_URL, data=data, body=body)

        data = client.get_new_tracking_code(service_id=7)
        assert data == 'OK'

    def test_verifier_digit(self, client):
        httpretty.enable()
        data = """
               <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cli="http://cliente.bean.master.sigep.bsb.correios.com.br/">
                    <x:Header/>
                    <x:Body>
                        <cli:geraDigitoVerificadorEtiquetas>
                            <etiquetas>{labels}</etiquetas>
                            <usuario>{user}</usuario>
                            <senha>{password}</senha>
                        </cli:geraDigitoVerificadorEtiquetas>
                    </x:Body>
                </x:Envelope>
               """.format(user=client.user, password=client.password, labels='PC0000001HK')
        body = fake_body(1)
        httpretty.register_uri(httpretty.POST, SOAP_URL, data=data, body=body)

        data = client.generate_verification_code(tracking_code='PC0000001HK')
        assert data == 'PC0000001HK'

    def test_create_plp(self, client):
        httpretty.enable()
        data = """
               <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cli="http://cliente.bean.master.sigep.bsb.correios.com.br/">
                    <x:Header/>
                    <x:Body>
                        <cli:fechaPlpVariosServicos>
                            <xml>?</xml>
                            <idPlpCliente>{plp_id}</idPlpCliente>
                            <cartaoPostagem>{post_card}</cartaoPostagem>
                            <listaEtiquetas>{label_list}</listaEtiquetas>
                            <usuario>{user}</usuario>
                            <senha>{password}</senha>
                        </cli:fechaPlpVariosServicos>
                    </x:Body>
                </x:Envelope>
               """.format(user=client.user, password=client.password, plp_id='003', post_card='ABC123', label_list=['PC000001HK', 'PC000002HK'])
        body = fake_body(10)
        httpretty.register_uri(httpretty.POST, SOAP_URL, data=data, body=body)

        obj_list = [
            {
                'tracking_code': 'PC000001HK',
                'service_code': '1',
                'weight': '1',
                'receiver_name': 'Joao Daher',
                'receiver_home_phone': '1122223333',
                'receiver_mobile_phone': '',
                'receiver_email': 'joao@stored.com',
                'receiver_address': 'Rua Galileu Galilei',
                'receiver_complement': '',
                'receiver_number': '1067',
                'receiver_neighborhood': 'Jardim Iraja',
                'receiver_city': 'Passos',
                'receiver_state': 'MG',
                'receiver_zip_code': '37902000',
                'nfe_number': '332323',
                'is_insurance': True,
                'total': '300',
                'dimension_height': '15',
                'dimension_width': '15',
                'dimension_length': '20',
                'dimension_diameter': '5',
            },
            {
                'tracking_code': 'PC000002HK',
                'service_code': '1',
                'weight': '1',
                'receiver_name': 'Joao Daher',
                'receiver_home_phone': '1122223333',
                'receiver_mobile_phone': '',
                'receiver_email': 'joao@stored.com',
                'receiver_address': 'Rua Galileu Galilei',
                'receiver_complement': '',
                'receiver_number': '1067',
                'receiver_neighborhood': 'Jardim Iraja',
                'receiver_city': 'Passos',
                'receiver_state': 'MG',
                'receiver_zip_code': '37902000',
                'nfe_number': '3323323',
                'is_insurance': True,
                'total': '300',
                'dimension_height': '15',
                'dimension_width': '15',
                'dimension_length': '20',
                'dimension_diameter': '5',
            }
        ]
        data = client.create_plp(intern_plp_number='003', object_list=obj_list)
        assert data == {
            'plp_id': 10,
            'tracking_code_list': [client._remove_dv_tracking_code(code) for code in ['PC000001HK', 'PC000002HK']],
        }
