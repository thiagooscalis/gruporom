TIPO_DOC_CHOICES = [
    ("CPF", "CPF"),
    ("CNPJ", "CNPJ"),
    ("Passaporte", "Passaporte"),
]

SEXO_CHOICES = [
    ("Masculino", "Masculino"),
    ("Feminino", "Feminino"),
]

TIPO_EMPRESA_CHOICES = [
    ("Alimentação", "Alimentação"),
    ("Turismo", "Turismo"),
    ("Administração de Bens", "Administração de Bens"),
]

TIPO_CARAVANA_CHOICES = [
    ("Evangélica", "Evangélica"),
    ("Católica", "Católica"),
    ("Lazer", "Lazer"),
    ("Mentoria", "Mentoria"),
]

REPASSE_TIPO_CHOICES = [
    ("Total", "Total"),
    ("Por Passageiro", "Por Passageiro"),
]

MOEDA_CHOICES = [
    ("Dólar", "Dólar"),
    ("Real", "Real"),
]

TIPO_PASSAGEIRO_CHOICES = [
    ("Guia", "Guia"),
    ("VIP", "VIP"),
    ("Free", "Free"),
]

CATEGORIA_TAREFA_CHOICES = [
    ("Aéreo", "Aéreo"),
    ("Terrestre", "Terrestre"),
    ("Passageiro", "Passageiro"),
]

STATUS_VENDA_CHOICES = [
    ('pre-venda', 'Pré-venda'),
    ('confirmada', 'Confirmada'),
    ('concluida', 'Concluída'),
    ('cancelada', 'Cancelada'),
]

FORMA_PAGAMENTO_CHOICES = [
    ('dinheiro', 'Dinheiro'),
    ('pix', 'PIX'),
    ('cartao_credito', 'Cartão de Crédito'),
    ('cartao_debito', 'Cartão de Débito'),
    ('boleto', 'Boleto'),
    ('transferencia', 'Transferência Bancária'),
    ('cheque', 'Cheque'),
    ('deposito', 'Depósito'),
]

STATUS_PAGAMENTO_CHOICES = [
    ('pendente', 'Pendente'),
    ('processando', 'Processando'),
    ('confirmado', 'Confirmado'),
    ('cancelado', 'Cancelado'),
    ('estornado', 'Estornado'),
]
