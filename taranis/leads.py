"""Carregamento da base de leads B2B e classificação das objeções comerciais."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd

from taranis.catalog import Produto, buscar_produto

LEADS_PATH = Path(__file__).resolve().parent.parent / "data" / "02_Leads_B2B_Comercial.xlsx"

COLUNAS = {
    "ID Lead": "id",
    "Empresa": "empresa",
    "Segmento": "segmento",
    "Porte (Colabs)": "porte",
    "Decisor (Nome)": "decisor_nome",
    "Decisor (Cargo)": "decisor_cargo",
    "E-mail de Contato": "email",
    "Produtos em Cotação": "produtos",
    "Valor Estimado (R$)": "valor",
    "Dores Registradas no CRM": "dores",
    "Objeção Principal Identificada": "objecao",
    "Status no Funil": "status",
    "Último Contato": "ultimo_contato",
}

PRECO, ORCAMENTO, FORNECEDOR, PRAZO, CUSTOMIZACAO, DRYWALL = (
    "PRECO",
    "ORCAMENTO",
    "FORNECEDOR",
    "PRAZO",
    "CUSTOMIZACAO",
    "DRYWALL",
)

CATEGORIAS = {
    PRECO: {"rotulo": "Preço", "matriz": "OBJ-01"},
    DRYWALL: {"rotulo": "Drywall vs Cabine", "matriz": "OBJ-01"},
    ORCAMENTO: {"rotulo": "Orçamento", "matriz": "OBJ-02"},
    FORNECEDOR: {"rotulo": "Fornecedor Atual", "matriz": "OBJ-03"},
    PRAZO: {"rotulo": "Prazo", "matriz": "OBJ-04"},
    CUSTOMIZACAO: {"rotulo": "Customização", "matriz": "OBJ-05"},
}

MATRIZ_PADRAO = [
    {
        "id": "OBJ-01",
        "objecao": "Preço: 'A cadeira / mesa do concorrente é 30% mais barata.'",
        "argumento_fraco": "'Mas a nossa qualidade é melhor e temos design mais bonito.'",
        "argumento_forte": (
            "Produtos de menor custo têm vida útil média de 14 meses e não possuem laudo NR-17 "
            "integral. A ErgoPro tem garantia estrutural de 5 anos: diluído, o custo por "
            "colaborador fica abaixo de R$ 1,90 por dia, reduzindo em até 40% as queixas posturais."
        ),
        "evidencia": "Garantia de 5 anos; Laudo ABERGO; Estudo de TCO.",
    },
    {
        "id": "OBJ-02",
        "objecao": "Orçamento: 'O orçamento deste semestre já está fechado / congelado pelo CFO.'",
        "argumento_fraco": "'Tudo bem, me ligue no ano que vem quando reabrir.'",
        "argumento_forte": (
            "Substituir mobiliário inadequado é mitigação de risco operacional e de absenteísmo. "
            "Faturamento 30/60/90 dias ou condições customizadas que cabem no OPEX sem "
            "comprometer o CAPEX do semestre."
        ),
        "evidencia": "Faturamento 30/60/90 dias; economia por redução de atestados.",
    },
    {
        "id": "OBJ-03",
        "objecao": "Fornecedor Atual: 'Já compramos de outro fornecedor homologado há anos.'",
        "argumento_fraco": "'Mas o nosso produto é muito mais moderno que o deles.'",
        "argumento_forte": (
            "Não romper a relação atual, mas qualificar o parque com ergonomia ativa. Iniciar com "
            "um projeto-piloto em uma área crítica para comparar laudos e satisfação real."
        ),
        "evidencia": "Piloto sem compromisso de 2 posições por 15 dias; ergonomistas certificados.",
    },
    {
        "id": "OBJ-04",
        "objecao": "Prazo de Entrega: 'O prazo de 20 a 25 dias para nossa cidade é muito longo.'",
        "argumento_fraco": "'Infelizmente a logística no Brasil é complicada e a fábrica fica cheia.'",
        "argumento_forte": (
            "CD em Santa Catarina com estoque regulador dos modelos mais demandados. Entrega "
            "escalonada imediata em 7 dias úteis do lote essencial e saldo na sequência."
        ),
        "evidencia": "CD de Santa Catarina com pronta-entrega; entrega escalonada.",
    },
    {
        "id": "OBJ-05",
        "objecao": "Dúvida de Customização: 'Não sei se os produtos vão combinar com o layout.'",
        "argumento_fraco": "'Só temos o modelo preto padrão que está no site.'",
        "argumento_forte": (
            "Engenharia de aplicação com arquitetura e facilities. Acima de 30 posições, "
            "personalização de mesh e tampos FSC, além de blocos 3D/BIM para a planta baixa."
        ),
        "evidencia": "Biblioteca BIM / Revit / SketchUp gratuita; amostras físicas em 48h.",
    },
]


def _normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return sem_acento.lower()


def classificar_objecao(texto: str) -> str:
    """Classifica a objeção registrada no CRM em uma das categorias do playbook."""
    norm = _normalizar(texto)
    prefixo = norm.split(":", 1)[0]

    if "drywall" in norm or ("cabine" in norm and ("obra" in norm or "reforma" in norm)):
        return DRYWALL
    if "custom" in prefixo:
        return CUSTOMIZACAO
    if "fornecedor" in prefixo:
        return FORNECEDOR
    if "orcamento" in prefixo or "pagamento" in prefixo:
        return ORCAMENTO
    if "prazo" in prefixo:
        return PRAZO
    if "preco" in prefixo:
        return PRECO

    palavras_chave = [
        (CUSTOMIZACAO, ("tecido", "acabamento", "cor ", "pantone", "layout")),
        (FORNECEDOR, ("fornecedor", "contrato", "homolog", "importadora")),
        (ORCAMENTO, ("orcamento", "parcel", "capex", "cfo", "boleto", "carencia")),
        (PRAZO, ("prazo", "entrega", "dias")),
        (PRECO, ("preco", "desconto", "barat", "caro")),
    ]
    for categoria, chaves in palavras_chave:
        if any(chave in norm for chave in chaves):
            return categoria
    return PRECO


def rotulo_categoria(categoria: str) -> str:
    return CATEGORIAS[categoria]["rotulo"]


def mascarar_email(email: str) -> str:
    """Mascara o e-mail para exibição em tabela (LGPD - minimização de dados)."""
    if not isinstance(email, str) or "@" not in email:
        return ""
    usuario, dominio = email.split("@", 1)
    visivel = usuario[:2] if len(usuario) > 2 else usuario[:1]
    return f"{visivel}***@{dominio}"


def interpretar_produtos(texto: str) -> list[tuple[int, Produto]]:
    """Converte '12x ErgoPro Core + 12x SmartDesk Studio' em [(12, Produto), ...]."""
    itens = []
    for parte in str(texto).split("+"):
        match = re.match(r"\s*(\d+)\s*x\s*(.+)", parte.strip(), re.IGNORECASE)
        if not match:
            continue
        produto = buscar_produto(match.group(2))
        if produto:
            itens.append((int(match.group(1)), produto))
    return itens


def carregar_leads(caminho: Path | str = LEADS_PATH) -> pd.DataFrame:
    """Lê a aba de leads da planilha do CRM e adiciona a categoria da objeção."""
    df = pd.read_excel(caminho, sheet_name=0)
    df = df.rename(columns=COLUNAS)[list(COLUNAS.values())]
    df["categoria"] = df["objecao"].map(classificar_objecao)
    df["objecao_tipo"] = df["categoria"].map(rotulo_categoria)
    return df


def carregar_matriz(caminho: Path | str = LEADS_PATH) -> list[dict]:
    """Lê a matriz de objeções; usa a cópia embarcada se a aba não estiver disponível."""
    try:
        df = pd.read_excel(caminho, sheet_name=1)
    except (FileNotFoundError, ValueError, IndexError):
        return MATRIZ_PADRAO
    df.columns = ["id", "objecao", "argumento_fraco", "argumento_forte", "evidencia"]
    return df.to_dict("records")


def matriz_por_categoria(matriz: list[dict], categoria: str) -> dict:
    alvo = CATEGORIAS[categoria]["matriz"]
    return next((linha for linha in matriz if linha["id"] == alvo), {})
