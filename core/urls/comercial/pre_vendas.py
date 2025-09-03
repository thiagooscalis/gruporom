from django.urls import path
from core.views.comercial.pre_vendas import (
    pre_vendas_lista,
    iniciar_venda_caravana,
    pre_venda_detalhe,
    gerenciar_passageiros_modal,
    buscar_pessoa_passageiro,
    selecionar_pessoa_passageiro,
    limpar_pessoa_passageiro,
    adicionar_passageiro,
    remover_passageiro,
    registrar_pagamento_modal,
    registrar_pagamento,
    confirmar_venda_modal,
    confirmar_venda,
    cancelar_venda_modal,
    cancelar_venda,
)

urlpatterns = [
    path('', pre_vendas_lista, name='pre_vendas_lista'),
    path('<int:venda_id>/', pre_venda_detalhe, name='pre_venda_detalhe'),
    path('iniciar-venda-caravana/<int:caravana_id>/', iniciar_venda_caravana, name='iniciar_venda_caravana'),
    
    # Gerenciamento de passageiros
    path('<int:venda_id>/passageiros/modal/', gerenciar_passageiros_modal, name='gerenciar_passageiros_modal'),
    path('buscar-pessoa/', buscar_pessoa_passageiro, name='buscar_pessoa_passageiro'),
    path('selecionar-pessoa/', selecionar_pessoa_passageiro, name='selecionar_pessoa_passageiro'),
    path('limpar-pessoa/', limpar_pessoa_passageiro, name='limpar_pessoa_passageiro'),
    path('<int:venda_id>/passageiros/adicionar/', adicionar_passageiro, name='adicionar_passageiro'),
    path('<int:venda_id>/passageiros/<int:passageiro_id>/remover/', remover_passageiro, name='remover_passageiro'),
    
    # Gerenciamento de pagamentos
    path('<int:venda_id>/pagamento/modal/', registrar_pagamento_modal, name='registrar_pagamento_modal'),
    path('<int:venda_id>/pagamento/registrar/', registrar_pagamento, name='registrar_pagamento'),
    
    # Confirmar e cancelar venda
    path('<int:venda_id>/confirmar/modal/', confirmar_venda_modal, name='confirmar_venda_modal'),
    path('<int:venda_id>/confirmar/', confirmar_venda, name='confirmar_venda'),
    path('<int:venda_id>/cancelar/modal/', cancelar_venda_modal, name='cancelar_venda_modal'),
    path('<int:venda_id>/cancelar/', cancelar_venda, name='cancelar_venda'),
]