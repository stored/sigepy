# coding: utf-8
SIGEP_SANDBOX_URL = 'https://apphom.correios.com.br/SigepMasterJPA/AtendeClienteService/AtendeCliente?wsdl'
SIGEP_PRODUCTION_URL = 'https://apps.correios.com.br/SigepMasterJPA/AtendeClienteService/AtendeCliente?wsdl'

CREATED, POSTED, SUBMITTED, DELIVERED, ATTEMPTED, WAITING, PROBLEM, EFFECTED = range(1, 9)

SRO_CHOICES = (
    (CREATED, 'Resgistro Criado'),
    (POSTED, 'Pedido postado'),
    (SUBMITTED, 'Encaminhado para entrega'),
    (DELIVERED, 'Saiu para entrega'),
    (ATTEMPTED, 'Tentativa de entrega'),
    (WAITING, 'Aguardando retirada'),
    (PROBLEM, 'Problema com entrega'),
    (EFFECTED, 'Entrega efetuada'),
)

PAC = 41106
PAC_CONTRACT = 41068

SEDEX = 40010
SEDEX_CONTRACT = 40096
ESEDEX_CONTRACT = 81019

SEDEX10 = 40215
SEDEX10_CONTRACT = 40215

SEDEX12 = 40169
SEDEX12_CONTRACT = 40169


CONTRACT_CHOICES = {
    'sedex': SEDEX_CONTRACT,
    'esedex': ESEDEX_CONTRACT,
    'pac': PAC_CONTRACT,
}

NO_CONTRACT_CHOICES = {
    'sedex': SEDEX,
    'pac': PAC,
    'sedex': '40096',
    'esedex': ESEDEX_CONTRACT,
    'pac': PAC_CONTRACT,
}


CHANCELED_OPTIONS = {
    PAC_CONTRACT: 'pac',
    PAC: 'pac',
    SEDEX: 'sedex',
    '40436': 'sedex',
    '40096': 'sedex',
    ESEDEX_CONTRACT: 'esedex',
}
