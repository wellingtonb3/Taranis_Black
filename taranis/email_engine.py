"""Motor de geração de e-mails de prospecção/follow-up com regras IF/ELSE por objeção."""

from __future__ import annotations

import math
import re

from taranis.catalog import FRETE_CIF_MINIMO, GARANTIA_PADRAO_ANOS, Produto, formatar_brl
from taranis.leads import (
    CUSTOMIZACAO,
    DRYWALL,
    FORNECEDOR,
    ORCAMENTO,
    PRAZO,
    PRECO,
    interpretar_produtos,
    rotulo_categoria,
)
from taranis.llm import LLMClient

MAX_PALAVRAS_ASSUNTO = 6
DIAS_UTEIS_5_ANOS = 22 * 12 * 5
VIDA_UTIL_DESCARTAVEL_MESES = 14
PRECO_CONCORRENTE_PADRAO = 800.0
TIPOS_EMAIL = ("Follow-up", "Prospecção")

ASSUNTOS = {
    PRECO: ("{e}: custo real em 5 anos", "O custo real em 5 anos"),
    DRYWALL: ("{e}: cabine móvel supera o drywall", "Cabine móvel ou drywall? Faça a conta"),
    PRAZO: ("{e}: lote prioritário em 10 dias", "Lote prioritário em até 10 dias"),
    ORCAMENTO: ("{e}: ergonomia sem travar o CAPEX", "Ergonomia sem travar o seu CAPEX"),
    FORNECEDOR: ("Piloto ergonômico sem risco: {e}", "Piloto de 15 dias, sem compromisso"),
    CUSTOMIZACAO: ("{e}: projeto sob medida com laudo", "Projeto sob medida, com laudo NR-17"),
}

PREFIXOS_GENERICOS = {"studio", "rede", "hub", "grupo"}

TITULOS = ("dr.", "dra.", "eng.", "prof.", "profa.")


def limitar_assunto(assunto: str, maximo: int = MAX_PALAVRAS_ASSUNTO) -> str:
    return " ".join(assunto.split()[:maximo])


def saudacao(nome: str) -> str:
    """'Dra. Camila Toledo' -> 'Dra. Camila'; 'Carlos Eduardo Prado' -> 'Carlos'."""
    partes = nome.split()
    if partes and partes[0].lower() in TITULOS and len(partes) > 1:
        return f"{partes[0]} {partes[1]}"
    return partes[0] if partes else nome


def _nome_curto_empresa(empresa: str) -> str:
    partes = empresa.split()
    if len(partes) > 1 and partes[0].lower() in PREFIXOS_GENERICOS:
        return " ".join(partes[:2])
    return partes[0]


def montar_assunto(categoria: str, empresa: str) -> str:
    """Assunto personalizado com a empresa; usa a versão genérica se passar de 6 palavras."""
    com_empresa, generico = ASSUNTOS[categoria]
    assunto = com_empresa.format(e=_nome_curto_empresa(empresa))
    if len(assunto.split()) > MAX_PALAVRAS_ASSUNTO:
        assunto = generico
    return limitar_assunto(assunto)


def _primeira_minuscula(texto: str) -> str:
    texto = str(texto).strip().rstrip(".")
    return texto[:1].lower() + texto[1:] if texto else texto


def _preco_concorrente(objecao: str) -> float:
    match = re.search(r"R\$\s*([\d.]+(?:,\d+)?)", objecao)
    if not match:
        return PRECO_CONCORRENTE_PADRAO
    return float(match.group(1).replace(".", "").replace(",", "."))


def _produto_principal(itens: list[tuple[int, Produto]], linha: str | None = None) -> Produto | None:
    for _, produto in itens:
        if linha is None or produto.linha == linha:
            return produto
    return None


def _bloco_preco(lead: dict, itens: list[tuple[int, Produto]]) -> str:
    cadeira = _produto_principal(itens, "ErgoPro")
    if cadeira:
        concorrente = _preco_concorrente(lead["objecao"])
        trocas = math.ceil(60 / VIDA_UTIL_DESCARTAVEL_MESES)
        custo_dia = cadeira.preco / DIAS_UTEIS_5_ANOS
        return (
            f"Entendo a pressão sobre o orçamento. Mas vale olhar o custo total de posse (TCO) em "
            f"5 anos: uma cadeira de {formatar_brl(concorrente)} dura em média "
            f"{VIDA_UTIL_DESCARTAVEL_MESES} meses e precisa de cerca de {trocas} trocas no período, "
            f"ou {formatar_brl(concorrente * trocas)} por posto, sem laudo NR-17. A {cadeira.nome} "
            f"custa {formatar_brl(cadeira.preco)} com garantia de {GARANTIA_PADRAO_ANOS} anos, ou "
            f"{formatar_brl(custo_dia)} por dia útil de trabalho. Some a isso a redução de até 40% nas "
            f"queixas posturais e a proteção contra passivos trabalhistas."
        )
    produto = _produto_principal(itens) or None
    nome = produto.nome if produto else "solução Taranis"
    custo_dia = (produto.preco / DIAS_UTEIS_5_ANOS) if produto else 0
    return (
        f"Entendo a comparação com opções mais baratas. A diferença está no custo total de posse "
        f"(TCO) em 5 anos: a {nome} tem motorização e componentes de padrão corporativo, laudo "
        f"NR-17 e garantia de {GARANTIA_PADRAO_ANOS} anos, o que dilui o investimento em "
        f"{formatar_brl(custo_dia)} por dia útil. Produtos de marketplace costumam exigir troca ou "
        f"manutenção antes disso, sem cobertura no Brasil."
    )


def _bloco_drywall(lead: dict, itens: list[tuple[int, Produto]]) -> str:
    return (
        f"Sobre a comparação com drywall: uma parede construída em prédio alugado vira benfeitoria "
        f"e fica no imóvel na mudança, além de exigir obra, poeira e paralisação. A Cabine Silence é "
        f"patrimônio móvel da {lead['empresa']}: acompanha a empresa em uma mudança ou novo layout, "
        f"é montada em cerca de 4 horas e entra no ativo imobilizado como móveis e utensílios, com "
        f"depreciação fiscal (taxa usual de 10% ao ano; vale validar com a sua contabilidade). E "
        f"entrega até 32 dB de atenuação certificada (ISO 23351-1) e ar renovado a cada 90 segundos, "
        f"algo que uma divisória comum não garante."
    )


def _bloco_prazo(lead: dict, itens: list[tuple[int, Produto]]) -> str:
    texto = (
        "Para não atrasar a sua operação, propomos o plano de Entrega Escalonada: um lote "
        "prioritário com os postos essenciais em até 10 dias (7 dias úteis), saindo do estoque "
        "regulador do nosso CD em Santa Catarina, e o saldo na sequência programada."
    )
    if float(lead.get("valor") or 0) >= FRETE_CIF_MINIMO:
        texto += (
            f" Como o pedido supera {formatar_brl(FRETE_CIF_MINIMO)}, o frete CIF é por nossa conta "
            f"para capitais do Sul e Sudeste."
        )
    return texto


def _bloco_orcamento(lead: dict, itens: list[tuple[int, Produto]]) -> str:
    return (
        "Sabemos que o caixa é prioridade. Trocar um mobiliário inadequado não é um custo "
        "discricionário: é mitigação de risco operacional e de absenteísmo. Para facilitar a "
        "aprovação com o financeiro, podemos faturar em 30/60/90 dias (CNPJ ativo há mais de 2 "
        "anos, sujeito à análise de crédito), mantendo a compra no OPEX, e levar ao CFO o cálculo "
        "de economia com a redução de atestados. Condições fora desse padrão podem ser avaliadas "
        "pelo nosso comitê financeiro."
    )


def _bloco_fornecedor(lead: dict, itens: list[tuple[int, Produto]]) -> str:
    return (
        "Não propomos romper a sua relação com o fornecedor atual. A sugestão é um projeto-piloto "
        "sem compromisso de 2 posições por 15 dias em uma área crítica, com acompanhamento de "
        "ergonomistas certificados, para comparar lado a lado o conforto, as queixas e o laudo "
        "NR-17 emitido por profissional credenciado."
    )


def _bloco_customizacao(lead: dict, itens: list[tuple[int, Produto]]) -> str:
    posicoes = sum(qtd for qtd, _ in itens)
    if posicoes > 30:
        abertura = f"Como o seu projeto tem {posicoes} posições, a personalização entra sem custo:"
    else:
        abertura = "A partir de 30 posições, a personalização entra sem custo:"
    return (
        f"Nosso núcleo de engenharia de aplicação trabalha direto com arquitetura e facilities. "
        f"{abertura} cores do tecido mesh e acabamentos de madeira (com acréscimo de 5 dias úteis no "
        f"prazo), tampos certificados FSC, blocos 3D/BIM (Revit e SketchUp) gratuitos para a planta "
        f"e amostras físicas enviadas em 48h."
    )


CHAMADAS = {
    PRECO: "Posso enviar o comparativo de TCO detalhado para o seu time de Compras?",
    DRYWALL: "Posso enviar o comparativo de custo obra vs. cabine móvel com a depreciação simulada?",
    PRAZO: "Podemos confirmar hoje quais postos entram no lote prioritário?",
    ORCAMENTO: "Topa uma conversa de 20 minutos com o financeiro para montarmos o fluxo de pagamento?",
    FORNECEDOR: "Qual área seria a melhor candidata para o piloto?",
    CUSTOMIZACAO: "Posso agendar o envio das amostras e dos blocos BIM esta semana?",
}


def argumento_por_objecao(categoria: str, lead: dict) -> str:
    """Regra IF/ELSE central: escolhe o argumento conforme a objeção do lead."""
    itens = interpretar_produtos(lead.get("produtos", ""))
    if categoria == PRECO:
        return _bloco_preco(lead, itens)
    elif categoria == DRYWALL:
        return _bloco_drywall(lead, itens)
    elif categoria == PRAZO:
        return _bloco_prazo(lead, itens)
    elif categoria == ORCAMENTO:
        return _bloco_orcamento(lead, itens)
    elif categoria == FORNECEDOR:
        return _bloco_fornecedor(lead, itens)
    elif categoria == CUSTOMIZACAO:
        return _bloco_customizacao(lead, itens)
    return _bloco_preco(lead, itens)


def gerar_email_offline(lead: dict, tipo: str = "Follow-up") -> dict:
    """Gera assunto e corpo de forma determinística (sem LLM)."""
    categoria = lead["categoria"]
    empresa = lead["empresa"]
    assunto = montar_assunto(categoria, empresa)

    if tipo == "Prospecção":
        abertura = (
            f"Acompanho o momento da {empresa} no setor de {lead['segmento']} e queria compartilhar uma ideia rápida."
        )
    else:
        data_contato = str(lead["ultimo_contato"]).split(" - ")[0].strip()
        abertura = f"Retomando a nossa conversa de {data_contato}."

    proposta = (
        f"Para a cotação em andamento ({lead['produtos']}, estimada em "
        f"{formatar_brl(float(lead['valor']))}), toda compra B2B inclui Laudo Ergonômico NR-17 "
        f"individualizado em PDF e garantia Taranis de {GARANTIA_PADRAO_ANOS} anos."
    )

    corpo = "\n\n".join(
        [
            f"Olá, {saudacao(lead['decisor_nome'])}, tudo bem?",
            abertura,
            f"Pelo que mapeamos, o cenário atual de vocês é: {_primeira_minuscula(lead['dores'])}.",
            argumento_por_objecao(categoria, lead),
            proposta,
            CHAMADAS[categoria],
            "Atenciosamente,\n[Seu nome] | Consultor(a) B2B Taranis Black",
        ]
    )
    return {
        "assunto": assunto,
        "corpo": corpo,
        "categoria": categoria,
        "regra": rotulo_categoria(categoria),
        "fonte": "offline",
    }


def gerar_email_llm(cliente: LLMClient, lead: dict, tipo: str = "Follow-up") -> dict:
    """Gera o e-mail com o LLM usando a regra da objeção; cai no offline em caso de erro."""
    base = gerar_email_offline(lead, tipo)
    if not cliente.configurado:
        return base

    sistema = (
        "Você é um consultor de vendas B2B sênior da Taranis Black (ergonomia corporativa). "
        "Escreva em português do Brasil, tom consultivo, científico e sofisticado, sem exageros. "
        "Use somente fatos fornecidos. Responda apenas com JSON: "
        '{"assunto": "...", "corpo": "..."}. O assunto deve ter no máximo 6 palavras.'
    )
    usuario = (
        f"Tipo de e-mail: {tipo}\n"
        f"Empresa: {lead['empresa']} ({lead['segmento']}, {lead['porte']} colaboradores)\n"
        f"Decisor: {lead['decisor_nome']} - {lead['decisor_cargo']}\n"
        f"Produtos em cotação: {lead['produtos']} | Valor: {formatar_brl(float(lead['valor']))}\n"
        f"Dores: {lead['dores']}\n"
        f"Objeção: {lead['objecao']}\n"
        f"Argumento obrigatório (regra '{base['regra']}'): {argumento_por_objecao(lead['categoria'], lead)}\n"
        f"Inclua: laudo NR-17 individualizado em PDF e garantia de {GARANTIA_PADRAO_ANOS} anos. "
        f"Termine com uma chamada para ação e a assinatura '[Seu nome] | Consultor(a) B2B Taranis Black'."
    )
    try:
        dados = cliente.conversar_json([{"role": "system", "content": sistema}, {"role": "user", "content": usuario}])
        return {
            **base,
            "assunto": limitar_assunto(str(dados["assunto"]).strip()),
            "corpo": str(dados["corpo"]).strip(),
            "fonte": cliente.provedor,
        }
    except Exception as exc:  # noqa: BLE001 - qualquer falha volta ao modo offline
        return {**base, "fonte": "offline", "aviso": f"Falha na {cliente.provedor}, usado modo offline: {exc}"}
