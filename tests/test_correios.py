# coding: utf-8
import httpretty
import pytest

dev = {
    'affiliation_id': 'sigepy', 'password': 'sigepy@pass',
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


SOAP_URL = 'http://webservice.correios.com.br:80/service/rastro'


class TestSRO:
    @pytest.fixture
    def client(self):
        from sigep.correios_client import CorreiosSROClient
        client = CorreiosSROClient(**dev)
        return client

    def test_find_tracking_code(self, client):
        httpretty.enable()
        data = """
               <x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:res="http://resource.webservice.correios.com.br/">
                    <x:Header/>
                    <x:Body>
                        <res:buscaEventos>
                            <res:usuario>{user}</res:usuario>
                            <res:senha>{password}</res:senha>
                            <res:tipo>{type}</res:tipo>
                            <res:resultado>{result}</res:resultado>
                            <res:lingua>{lang}</res:lingua>
                            <res:objetos>{objects}</res:objetos>
                        </res:buscaEventos>
                    </x:Body>
                </x:Envelope>
               """.format(user=client.affiliation_id, password=client.password, type='L', lang=101, result='',
                          objects='JF598971235BR')
        body = """
                <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
                 <soapenv:Body>
                 <ns2:buscaEventosResponse xmlns:ns2="http://resource.webservice.correios.com.br/">
                 <return>
                 <versao>2.0</versao>
                 <qtd>1</qtd>
                 <objeto>
                 <numero>JF598971235BR</numero>
                 <sigla>JF</sigla>
                 <nome>REMESSA ECONÔMICA C/AR DIGITAL</nome>
                 <categoria>REMESSA ECONÔMICA TALÃO/CARTÃO</categoria>
                 <evento>
                 <tipo>BDE</tipo>
                 <status>23</status>
                 <data>18/03/2014</data>
                 <hora>18:37</hora>
                 <descricao>Objeto devolvido ao remetente</descricao>
                 <detalhe/>
                 <local>CTCE MACEIO</local>
                 <codigo>57060971</codigo>
                 <cidade>MACEIO</cidade>
                 <uf>AL</uf>
                 </evento>
                 </objeto>
                 </return>
                 </ns2:buscaEventosResponse>
                 </soapenv:Body>
                </soapenv:Envelope>
        """
        httpretty.register_uri(httpretty.POST, SOAP_URL, data=data, body=body)
        expected_response = {
            'status': True, 'category': u'REMESSA ECON\xd4MICA TAL\xc3O/CART\xc3O',
            'name': u'REMESSA ECON\xd4MICA C/AR DIGITAL',
            'current_status': u'Objeto devolvido ao remetente',
            'tracking_code': u'JF598971235BR',
            'event_list': [
                {
                    'status': u'23', 'city': u'MACEIO', 'code': 57060971,
                    'description': u'Objeto devolvido ao remetente',
                    'hour': '18:37', 'date': '18/03/2014',
                    'local': u'CTCE MACEIO', 'uf': u'AL',
                    'type': u'BDE', 'destiny': None
                }
            ],
            'sigla': u'JF'
        }

        data = client.find_by_tracking_code(tracking_code='JF598971235BR')
        assert data['status'] == expected_response['status']

        # error
        body = """
                <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
                 <soapenv:Body>
                 <ns2:buscaEventosResponse xmlns:ns2="http://resource.webservice.correios.com.br/">
                 <return>
                 <versao>2.0</versao>
                 <qtd>1</qtd>
                 <objeto>
                 <erro>PROBLEMA</erro>
                 </objeto>
                 </return>
                 </ns2:buscaEventosResponse>
                 </soapenv:Body>
                </soapenv:Envelope>
        """
        httpretty.register_uri(httpretty.POST, SOAP_URL, data=data, body=body)
        data = client.find_by_tracking_code(tracking_code='JF598971235BR')
        assert data['status'] is False
        