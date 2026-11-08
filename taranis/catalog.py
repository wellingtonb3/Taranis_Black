"""Catálogo oficial de produtos e políticas comerciais da Taranis Black (AF 2026)."""

from __future__ import annotations

from dataclasses import dataclass, field

GARANTIA_PADRAO_ANOS = 5

LINHAS = {
    "ErgoPro": {
        "categoria": "Cadeiras",
        "titulo": "Linha Taranis ErgoPro",
        "subtitulo": "Cadeiras corporativas para jornadas de 8h a 12h com prevenção de lesões posturais",
    },
    "SmartDesk": {
        "categoria": "Mesas",
        "titulo": "Linha Taranis SmartDesk",
        "subtitulo": "Mesas elevatórias elétricas Sit-Stand para alternância postural inteligente",
    },
    "Silence": {
        "categoria": "Cabines",
        "titulo": "Linha Taranis Silence",
        "subtitulo": "Cabines acústicas com ventilação forçada para chamadas, 1-on-1 e reuniões híbridas",
    },
}


@dataclass(frozen=True)
class Produto:
    sku: str
    nome: str
    linha: str
    preco: float
    publico: str
    destaques: tuple[str, ...]
    especificacoes: str
    certificacoes: str
    garantia_anos: int = GARANTIA_PADRAO_ANOS
    extras: dict = field(default_factory=dict)

    @property
    def categoria(self) -> str:
        return LINHAS[self.linha]["categoria"]


PRODUTOS: tuple[Produto, ...] = (
    Produto(
        sku="ERGO-EXE",
        nome="ErgoPro Executive",
        linha="ErgoPro",
        preco=3490.00,
        publico="C-Level, diretores e postos estratégicos",
        destaques=("Mesh alemão", "Lombar 3D", "Braços 4D", "Synchro-Tilt", "Até 150 kg"),
        especificacoes=(
            "Encosto em mesh termoplástico alemão respirável; apoio lombar 3D com regulagem de "
            "curvatura e profundidade; braços 4D; mecanismo Synchro-Tilt italiano com 5 posições; "
            "pistão Classe 4 cromado (até 150 kg); base em alumínio polido com rodízios PU 65 mm."
        ),
        certificacoes="Laudo de Conformidade Integral NR-17 (ABERGO) e ANSI/BIFMA X5.1",
    ),
    Produto(
        sku="ERGO-SPE",
        nome="ErgoPro Specialist",
        linha="ErgoPro",
        preco=2490.00,
        publico="Times de tecnologia, analistas, financeiro e operações",
        destaques=("Espuma D60 térmica", "Lombar 6 níveis", "Braços 3D", "Até 135 kg"),
        especificacoes=(
            "Encosto em tela mesh de alta densidade; assento em espuma injetada D60 com controle "
            "térmico; suporte lombar com ajuste vertical de 6 níveis; braços 3D em PU macio; "
            "reclinação sincronizada com 3 travas; pistão Classe 4 (até 135 kg)."
        ),
        certificacoes="Laudo de Conformidade NR-17 emitido por ergonomista certificado",
    ),
    Produto(
        sku="ERGO-COR",
        nome="ErgoPro Core",
        linha="ErgoPro",
        preco=1890.00,
        publico="Atendimento, backoffice e compras em grande volume B2B",
        destaques=("Espuma D50", "Braços 2D", "Relax 90°", "Volume corporativo"),
        especificacoes=(
            "Encosto em tela com curvatura fisiológica pré-moldada; assento anatômico em espuma "
            "D50; braços 2D (altura); mecanismo relax com bloqueio na posição ereta (90°); "
            "rodízios de 50 mm para piso duro."
        ),
        certificacoes="Atestado de conformidade com as exigências da NR-17",
    ),
    Produto(
        sku="DESK-PRO160",
        nome="SmartDesk Pro Dual 160",
        linha="SmartDesk",
        preco=4800.00,
        publico="Estações premium, tecnologia e criação",
        destaques=("Motor duplo <43 dB", "4 memórias", "160x80 cm", "125 kg", "Calha de cabos"),
        especificacoes=(
            "Motor duplo alemão sincronizado (<43 dB, 38 mm/s); painel touch LED com 4 memórias; "
            "anticolisão com sensor giroscópico; tampo 160x80 cm em MDF 25 mm FSC; 125 kg; "
            "calha oculta para gerenciamento de cabos."
        ),
        certificacoes="Tampo com certificação FSC sustentável",
    ),
    Produto(
        sku="DESK-STU140",
        nome="SmartDesk Studio 140",
        linha="SmartDesk",
        preco=3600.00,
        publico="Escritórios híbridos e mesas rotativas",
        destaques=("Motor duplo <46 dB", "4 memórias", "140x70 cm", "100 kg"),
        especificacoes=(
            "Motor duplo silencioso (<46 dB, 32 mm/s); controlador com 4 memórias; tampo "
            "ergonômico 140x70 cm; capacidade de 100 kg; sensor anti-impacto; passa-fios embutido."
        ),
        certificacoes="Sensor anti-impacto padrão",
    ),
    Produto(
        sku="DESK-COM120",
        nome="SmartDesk Compact 120",
        linha="SmartDesk",
        preco=2700.00,
        publico="Home office de colaboradores e layouts adensados",
        destaques=("Motor único alto torque", "3 memórias", "120x60 cm", "75 kg"),
        especificacoes=(
            "Motor único de alto torque; painel com 3 memórias; tampo compacto 120x60 cm; "
            "suporta até 75 kg; montagem rápida em 20 minutos."
        ),
        certificacoes="Montagem rápida em 20 minutos",
    ),
    Produto(
        sku="SIL-QUAD",
        nome="Silence Quad (4 lugares)",
        linha="Silence",
        preco=28000.00,
        publico="Reuniões híbridas e apresentações executivas",
        destaques=("32 dB ISO 23351-1", "Vidro duplo 10 mm", "Sensor CO2", "Ar renovado a cada 90 s", "USB-C 65W"),
        especificacoes=(
            "Até 4 pessoas; atenuação certificada de 32 dB (ISO 23351-1); vidro acústico duplo "
            "laminado 10 mm; ventilação inteligente com sensor de CO2 renovando 100% do ar a cada "
            "90 s; LED dimerizável 4000K; mesa em carvalho; 2 tomadas, 2 USB-A, 2 USB-C PD 65W e HDMI. "
            "2.100 x 1.500 x 2.250 mm | 580 kg."
        ),
        certificacoes="Atenuação certificada ISO 23351-1",
    ),
    Produto(
        sku="SIL-DUO",
        nome="Silence Duo (2 lugares)",
        linha="Silence",
        preco=21000.00,
        publico="Feedbacks 1-on-1 e entrevistas confidenciais de RH",
        destaques=("32 dB", "Ventilação <28 dB", "LED por presença", "USB-C"),
        especificacoes=(
            "Projetada para 1-on-1, entrevistas de RH e alinhamentos com clientes; atenuação de "
            "32 dB; ventilação forçada contínua de baixo ruído (<28 dB); LED automático por "
            "presença; duas banquetas e mesa central; tomadas e USB-C. 1.400 x 1.100 x 2.250 mm | 390 kg."
        ),
        certificacoes="Atenuação de 32 dB",
    ),
    Produto(
        sku="SIL-SOLO",
        nome="Silence Solo (Phone Booth)",
        linha="Silence",
        preco=14500.00,
        publico="Chamadas, videoconferências confidenciais e foco profundo",
        destaques=("30 dB", "Carregador por indução", "Sensor de presença", "Bancada em madeira maciça"),
        especificacoes=(
            "Cabine individual compacta; atenuação de 30 dB; sensor de presença para luz e "
            "exaustão; bancada ergonômica em madeira maciça com carregador por indução e tomada "
            "universal. 1.000 x 1.000 x 2.200 mm | 260 kg."
        ),
        certificacoes="Atenuação de 30 dB",
    ),
)

POLITICAS_COMERCIAIS = {
    "Faturamento corporativo": (
        "Faturado 30/60/90 dias via boleto para CNPJ ativo há mais de 2 anos, com aprovação prévia "
        "de crédito. Compras abaixo de R$ 10.000 em 30 dias ou cartão corporativo em até 6x sem juros."
    ),
    "Prazos de entrega": (
        "Sul e Sudeste: 5 a 8 dias úteis (estoque) e 15 dias úteis (customizados). Centro-Oeste, "
        "Nordeste e Norte: 12 a 20 dias úteis. Cabines Silence com montagem técnica agendada (~4 h)."
    ),
    "Frete CIF/FOB": (
        "Frete CIF gratuito acima de R$ 35.000 para capitais do Sul e Sudeste. Demais regiões e "
        "pedidos abaixo dessa faixa: frete compartilhado ou FOB com transportadoras homologadas."
    ),
    "Laudo NR-17": (
        "Toda compra B2B inclui Laudo Ergonômico de Posto de Trabalho individualizado em PDF, "
        "assinado por Engenheiro de Segurança do Trabalho e Ergonomista credenciado."
    ),
    "Customização": (
        "Acima de 30 posições: cores de mesh e acabamentos de madeira personalizados sem custo, "
        "com acréscimo de 5 dias úteis no prazo."
    ),
    "Garantia Taranis": (
        f"Garantia padrão Taranis de {GARANTIA_PADRAO_ANOS} anos em todo o portfólio, reforçando a "
        "confiança do cliente corporativo."
    ),
}

FRETE_CIF_MINIMO = 35000.00


def produtos_por_categoria(categorias: list[str] | None = None) -> list[Produto]:
    """Retorna os produtos filtrados pelas categorias informadas (todas se vazio)."""
    if not categorias:
        return list(PRODUTOS)
    return [p for p in PRODUTOS if p.categoria in categorias]


def ordenar_por_preco(produtos: list[Produto], decrescente: bool = False) -> list[Produto]:
    return sorted(produtos, key=lambda p: p.preco, reverse=decrescente)


def buscar_produto(nome: str) -> Produto | None:
    """Encontra um produto pelo nome (busca parcial, sem diferenciar maiúsculas)."""
    alvo = nome.lower().strip()
    for produto in PRODUTOS:
        base = produto.nome.lower().split(" (")[0]
        if base in alvo or alvo in base:
            return produto
    return None


def ergopro() -> list[Produto]:
    return [p for p in PRODUTOS if p.linha == "ErgoPro"]


def formatar_brl(valor: float) -> str:
    """Formata número no padrão monetário brasileiro (R$ 1.234,56)."""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def formatar_brl_compacto(valor: float) -> str:
    """Formata valores altos de forma curta para métricas (R$ 4,69 mi; R$ 234,7 mil)."""
    if abs(valor) >= 1_000_000:
        return f"R$ {valor / 1_000_000:.2f} mi".replace(".", ",")
    if abs(valor) >= 1_000:
        return f"R$ {valor / 1_000:.1f} mil".replace(".", ",")
    return formatar_brl(valor)
