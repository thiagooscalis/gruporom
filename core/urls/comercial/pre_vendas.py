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
    remover_venda,
    # Novas views para extras e pagamentos
    gerenciar_extras_modal,
    adicionar_extra,
    remover_extra,
    gerenciar_pagamentos_modal,
    adicionar_pagamento,
    cancelar_pagamento,
    confirmar_pagamento,
    buscar_pessoas_autocomplete,
    listar_passageiros,
    # Views para cliente
    selecionar_cliente_modal,
    definir_cliente,
    buscar_clientes_autocomplete,
    buscar_por_documento,
    buscar_por_documento_passageiro,
    cadastrar_comprador,
    upload_passaporte_modal,
    upload_passaporte,
)

urlpatterns = [
    path('', pre_vendas_lista, name='pre_vendas_lista'),
    path('<int:venda_id>/', pre_venda_detalhe, name='pre_venda_detalhe'),
    path('iniciar-venda-caravana/<int:caravana_id>/', iniciar_venda_caravana, name='iniciar_venda_caravana'),
    
    # Gerenciamento de passageiros
    path('<int:venda_id>/passageiros/modal/', gerenciar_passageiros_modal, name='gerenciar_passageiros_modal'),
    path('buscar-pessoa/', buscar_pessoa_passageiro, name='buscar_pessoa_passageiro'),
    path('buscar-pessoas-autocomplete/', buscar_pessoas_autocomplete, name='buscar_pessoas_autocomplete'),
    path('selecionar-pessoa/', selecionar_pessoa_passageiro, name='selecionar_pessoa_passageiro'),
    path('limpar-pessoa/', limpar_pessoa_passageiro, name='limpar_pessoa_passageiro'),
    path('<int:venda_id>/passageiros/adicionar/', adicionar_passageiro, name='adicionar_passageiro'),
    path('<int:venda_id>/passageiros/<int:passageiro_id>/remover/', remover_passageiro, name='remover_passageiro'),
    path('<int:venda_id>/passageiros/listar/', listar_passageiros, name='listar_passageiros'),
    
    # Gerenciamento de extras
    path('<int:venda_id>/extras/modal/', gerenciar_extras_modal, name='gerenciar_extras_modal'),
    path('<int:venda_id>/extras/adicionar/', adicionar_extra, name='adicionar_extra'),
    path('<int:venda_id>/extras/<int:extra_id>/remover/', remover_extra, name='remover_extra'),
    
    # Gerenciamento de pagamentos
    path('<int:venda_id>/pagamentos/modal/', gerenciar_pagamentos_modal, name='gerenciar_pagamentos_modal'),
    path('<int:venda_id>/pagamentos/adicionar/', adicionar_pagamento, name='adicionar_pagamento'),
    path('pagamentos/<int:pagamento_id>/cancelar/', cancelar_pagamento, name='cancelar_pagamento'),
    path('pagamentos/<int:pagamento_id>/confirmar/', confirmar_pagamento, name='confirmar_pagamento'),
    path('<int:venda_id>/pagamento/modal/', registrar_pagamento_modal, name='registrar_pagamento_modal'),
    path('<int:venda_id>/pagamento/registrar/', registrar_pagamento, name='registrar_pagamento'),
    
    # Confirmar e cancelar venda
    path('<int:venda_id>/confirmar/modal/', confirmar_venda_modal, name='confirmar_venda_modal'),
    path('<int:venda_id>/confirmar/', confirmar_venda, name='confirmar_venda'),
    path('<int:venda_id>/cancelar/modal/', cancelar_venda_modal, name='cancelar_venda_modal'),
    path('<int:venda_id>/cancelar/', cancelar_venda, name='cancelar_venda'),
    path('<int:venda_id>/remover/', remover_venda, name='remover_venda'),
    
    # Gerenciamento de cliente
    path('<int:venda_id>/cliente/modal/', selecionar_cliente_modal, name='selecionar_cliente_modal'),
    path('<int:venda_id>/cliente/definir/', definir_cliente, name='definir_cliente'),
    path('buscar-clientes-autocomplete/', buscar_clientes_autocomplete, name='buscar_clientes_autocomplete'),
    path('buscar-por-documento/', buscar_por_documento, name='buscar_por_documento'),
    path('buscar-por-documento-passageiro/', buscar_por_documento_passageiro, name='buscar_por_documento_passageiro'),
    path('<int:venda_id>/cadastrar-comprador/', cadastrar_comprador, name='cadastrar_comprador'),
    
    # Upload de passaporte
    path('passaporte/<int:pessoa_id>/modal/', upload_passaporte_modal, name='upload_passaporte_modal'),
    path('passaporte/<int:pessoa_id>/upload/', upload_passaporte, name='upload_passaporte'),
]