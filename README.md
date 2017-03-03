# Sigepy

Wrapper do webservice dos correios SIGEP Web para consulta preços e prazos, geração de etiquetas e PLP, e outros.

## Recursos

* Calcular preços e prazos de entrega da encomenda.   
* Obter os dados de rastreamento das encomendas.   
* Verificar se um tipo de serviço é permitido entre dois endereços.   
* Gerar e enviar o XML da pré-lista de postagem (PLP) para o Correios.   
* Gerar novos números de etiquetas de postagem.
* Criar e verificar validade do dígito verificador das etiquetas.   
* Gerar o relatório da PLP no formato PDF.   
* Gerar as etiquetas de postagem no formato PDF.
* Gerar em PDF as chancelas para cada tipo de serviço (logo de cada tipo de serviço). 


## Requisitos

* Python >= 2.7

## Instalação

#### PyPi

_[em breve]_


### Do Repositório

    git clone https://github.com/stored/sigepy.git
    (env) python setup.py develop

## Configuração

    SIGEP_CEP_ORIGIN = '14020273'
    SIGEP_USER = 'sigep'
    SIGEP_PASSWORD = 'senha@123'
    SIGEP_ADMINISTRATION_CODE = '1234567'
    SIGEP_CONTRACT = '123456789'
    SIGEP_CARD = '123456789'
    SIGEP_CEP_ORIGIN = '123456789'
    SIGEP_CNPJ = '123456789'
    SIGEP_SANDBOX = False

    SIGEP_CHANCELA_STATE = 'SPI'

    SIGEP_STORE_INFORMATION = {
        'contract': '{0}/2014-DR/{1}'.format(SIGEP_CONTRACT, SIGEP_CHANCELA_STATE),
        'contract_name': 'Contrato Loja',
        'name': 'Nome da loja ME',
        'short_name': u'nome curto com menos de 50',
        'address': 'Av. Antonio Diederichsen 741',
        'number': '741',
        'street': 'Av. Antonio Diederichsen',
        'area': 'Bairro',
        'zip_code': '14020-250',
        'city': 'Ribeirão Preto',
        'state': 'SP',
        'phone': '16272822282',
        'email': 'email@dominio.com',
    }