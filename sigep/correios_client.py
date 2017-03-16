# coding: utf-8
from suds.client import Client


class CorreiosSROClient(object):
    """
    Tipo:
        L - O servidor fara a consulta individual objeto por objeto
        F - O servidor fara a consulta sequencial do primeiro ultimo objeto

    Resultado:
        T - O servidor fara a consulta retornando todas as
            movimentações do objeto
        U - O servidor fara a consulta retornando a ultima
            movimentação do objeto

    Lingua:
        101 - Os eventos serão retornados no idioma portugues
        102 - Os eventos serão retornados no idioma ingles
    """

    def __init__(self, affiliation_id, password, url='https://webservice.correios.com.br/service/rastro/Rastro.wsdl', timeout=3):
        self.client = Client(url, timeout=timeout)
        self.affiliation_id = affiliation_id
        self.password = password

    def find_by_tracking_code(self, tracking_code, last_result=False):
        if last_result:
            result_type = 'U'
        else:
            result_type = 'T'

        response = self.client.service.buscaEventos(
            usuario=self.affiliation_id,
            senha=self.password,
            tipo='L',
            lingua=101,
            resultado=result_type,
            objetos=tracking_code
        )

        data = []
        objeto = response.objeto[0]

        if hasattr(objeto, 'erro'):
            return {
                'status': False,
                'tracking_code': unicode(getattr(objeto, 'numero', u'')),
                'erro': unicode(getattr(objeto, 'erro', u'')),
            }

        return {
            'status': True,
            'tracking_code': unicode(getattr(objeto, 'numero', u'')),
            'sigla': unicode(getattr(objeto, 'sigla', u'')),
            'name': unicode(getattr(objeto, 'nome', u'')),
            'category': unicode(getattr(objeto, 'categoria', u'')),
            'event_list': self._get_event_list(objeto),
            'current_status': self._get_current_status(objeto),
        }

    def _get_destiny(self, event):
        if hasattr(event, 'destino'):
            destiny = event.destino[0]
            destiny_data = {
                'local': unicode(getattr(destiny, 'local', u'')),
                'codigo': unicode(getattr(destiny, 'codigo', u'')),
                'cidade': unicode(getattr(destiny, 'cidade', u'')),
                'bairro': unicode(getattr(destiny, 'bairro', u'')),
                'uf': unicode(getattr(destiny, 'uf', u'')),
            }
            return destiny_data

        return None

    def _get_current_status(self, obj):
        if hasattr(obj, 'evento'):
            event = obj.evento[0]
            return unicode(getattr(event, 'descricao', u''))
        return None

    def _get_event_list(self, obj):
        event_list = []
        for event in obj.evento:
            event_list.append({
                'status': unicode(getattr(event, 'status', u'')),
                'code': getattr(event, 'codigo', u''),
                'type': unicode(getattr(event, 'tipo', u'')),
                'date': getattr(event, 'data', u''),
                'hour': getattr(event, 'hora', u''),
                'description': unicode(getattr(event, 'descricao', u'')),
                'local': unicode(getattr(event, 'local', u'')),
                'city': unicode(getattr(event, 'cidade', u'')),
                'uf': unicode(getattr(event, 'uf', u'')),
                'destiny': self._get_destiny(event),
            })
        return event_list
