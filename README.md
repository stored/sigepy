[![Documentation Status](https://readthedocs.org/projects/sigepy/badge/?version=latest)](http://sigepy.readthedocs.io/en/latest/?badge=latest)
[![Code Climate](https://codeclimate.com/github/stored/sigepy.png)](https://codeclimate.com/github/stored/sigepy)
[![Build Status](https://travis-ci.org/stored/sigepy.png)](https://travis-ci.org/stored/sigepy)
[![Coverage Status](https://coveralls.io/repos/github/stored/sigepy/badge.svg?branch=master)](https://coveralls.io/github/stored/sigepy?branch=master)

# Sigepy

Wrapper do webservice dos correios SIGEP Web para consulta preços e prazos, geração de etiquetas e PLP, e outros.

## Recursos

* Calcular preços e prazos de entrega da encomenda.   
* Obter os dados de rastreamento das encomendas.   
* Verificar se um tipo de serviço é permitido entre dois endereços.   
* Gerar e enviar o XML da pré-lista de postagem (PLP) para o Correios.   
* Gerar novos números de etiquetas de postagem.
* Criar e verificar validade do dígito verificador das etiquetas.   
* Gerar o relatório da PLP.   
* Gerar as etiquetas de postagem.
* Gerar as chancelas para cada tipo de serviço (logo de cada tipo de serviço). 


## Requisitos

* Python >= 2.7

## Instalação

#### PyPi

_[em breve]_


### Do Repositório

    git clone https://github.com/stored/sigepy.git
    (env) python setup.py develop

## Como Usar

    from sigep.sigep_client import Sigep
    
    crendetials = {
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
    
    sigep = Sigep(**crendetials)
    available_services = sigep.search_service()
    