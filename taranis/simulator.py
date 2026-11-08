"""Simulador de role-play com o decisor cético Dr. Roberto Mendes (Nexus Corp)."""

from __future__ import annotations

import re
import unicodedata

from taranis.llm import LLMClient

PERSONA_NOME = "Dr. Roberto Mendes"
PERSONA_DESCRICAO = (
    "Diretor de Facilities da Nexus Corp (400 colaboradores), cético e focado em custos. "
    "Quer reformar o escritório, mas achou a Taranis 35% mais cara e questiona por que não "
    "comprar de concorrentes mais baratos."
)

ABERTURA = (
    "Bom dia. Vou ser direto: recebi a proposta de vocês e ela está 35% acima das outras duas "
    "cotações que tenho na mesa. Para 400 colaboradores, essa diferença é muito dinheiro. "
    "Por que eu não deveria simplesmente fechar com o concorrente mais barato?"
)

TOPICOS: dict[str, tuple[str, ...]] = {
    "nr17": ("nr-17", "nr17", "nr 17", "laudo", "norma", "auditoria", "fiscaliza", "ministerio", "abergo"),
    "garantia": ("garantia", "5 anos", "cinco anos"),
    "tco": ("tco", "custo total", "roi", "payback", "retorno", "por dia", "vida util", "durabilidade", "trocas"),
    "absenteismo": ("absenteismo", "atestado", "afastamento", "lombalgia", "dor", "lesao", "ler", "produtividade"),
    "piloto": ("piloto", "teste", "amostra", "experimentar"),
    "passivo": ("processo", "trabalhista", "passivo", "multa", "risco juridico"),
    "pagamento": ("parcel", "faturamento", "30/60/90", "boleto", "condicao de pagamento"),
    "prazo": ("prazo", "entrega", "escalonad"),
    "empatia": ("entendo", "compreendo", "faz sentido", "concordo", "justo", "imagino"),
}

TOPICOS_DE_VALOR = ("nr17", "garantia", "tco", "absenteismo", "piloto", "passivo")

RESPOSTAS: dict[str, tuple[str, ...]] = {
    "nr17": (
        "Laudo NR-17 todo fornecedor diz que tem. O concorrente também me mandou um atestado. "
        "O que o de vocês tem de diferente na prática, numa fiscalização?",
        "Certo, o laudo individualizado ajuda na auditoria. Mas isso justifica 35% a mais?",
    ),
    "garantia": (
        "Cinco anos de garantia é bonito no papel. E se a empresa de vocês não existir daqui a três "
        "anos? Quem me atende?",
        "Garantia longa eu valorizo, mas o meu CFO olha o desembolso de hoje, não o de 2031.",
    ),
    "tco": (
        "Essa conta de custo total sempre fecha a favor de quem vende. Que premissa de vida útil "
        "você usou para a cadeira do concorrente?",
        "Supondo que a conta esteja certa, em quantos meses eu recupero essa diferença?",
    ),
    "absenteismo": (
        "Atestado de coluna tem mil causas. Como eu vou provar para a diretoria que a queda veio da "
        "cadeira e não de outra coisa?",
        "Ok, temos queixas de lombalgia, isso é fato. Mas reduzir 40% me parece otimista demais.",
    ),
    "piloto": (
        "Um piloto pode funcionar, mas eu não tenho tempo para ficar avaliando cadeira. Quem conduz "
        "isso e quanto me custa?",
        "Piloto sem custo eu aceito discutir. Mas preciso de métricas claras no final.",
    ),
    "passivo": (
        "Nunca tivemos processo por causa de cadeira. Você está me vendendo medo?",
        "Risco trabalhista é com o jurídico. Eu respondo por orçamento de facilities.",
    ),
    "pagamento": (
        "Parcelar não muda o preço. Continua 35% mais caro, só que dividido.",
        "Faturamento em 30/60/90 ajuda o fluxo, mas a minha pergunta continua sendo o valor total.",
    ),
    "prazo": ("Prazo não é meu problema agora. Meu problema é preço.",),
    "generico": (
        "Você ainda não me deu um motivo concreto. O concorrente entrega cadeira preta com rodinha "
        "também. Qual é o argumento que eu levo para o meu CFO?",
        "Seja objetivo: o que eu ganho em reais pagando mais caro por vocês?",
        "Estou ouvindo, mas até agora parece discurso de catálogo. Me traga números.",
    ),
    "desconto": (
        "Se você já começa oferecendo desconto, é sinal de que tinha gordura no preço. Quanto mais "
        "você consegue tirar?",
    ),
}

CONCESSAO = (
    "Está bem, você trouxe argumentos melhores do que eu esperava. Faça assim: me mande uma "
    "proposta com o piloto, o laudo NR-17 e a conta de payback por escrito. Se os números se "
    "sustentarem, levo para o comitê. Mas não prometo nada."
)

PADRAO_DESCONTO = re.compile(
    r"(dou|damos|posso dar|consigo dar|ofere\w+|fa\w+)\s+(um\s+)?(desconto|abatimento)|baixar o preco"
)


def _normalizar(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def detectar_topicos(mensagem: str) -> set[str]:
    norm = _normalizar(mensagem)
    return {
        topico
        for topico, chaves in TOPICOS.items()
        if any(re.search(r"\b" + re.escape(chave.strip()), norm) for chave in chaves)
    }


def ofereceu_desconto(mensagem: str) -> bool:
    return bool(PADRAO_DESCONTO.search(_normalizar(mensagem)))


def _mensagens_vendedor(historico: list[dict]) -> list[str]:
    return [m["content"] for m in historico if m["role"] == "user"]


def responder_offline(historico: list[dict]) -> str:
    """Gera a resposta do decisor com base nos tópicos já abordados pelo vendedor."""
    vendedor = _mensagens_vendedor(historico)
    if not vendedor:
        return ABERTURA
    ultima = vendedor[-1]
    cobertos = set().union(*(detectar_topicos(m) for m in vendedor)) & set(TOPICOS_DE_VALOR)

    if ofereceu_desconto(ultima):
        return RESPOSTAS["desconto"][0]
    if len(cobertos) >= 4 and len(vendedor) >= 3:
        return CONCESSAO

    atuais = [t for t in TOPICOS if t in detectar_topicos(ultima) and t != "empatia"]
    topico = atuais[0] if atuais else "generico"
    usos = sum(1 for m in vendedor[:-1] if topico in detectar_topicos(m)) if atuais else len(vendedor) - 1
    opcoes = RESPOSTAS[topico]
    return opcoes[usos % len(opcoes)]


def avaliar_offline(historico: list[dict]) -> dict:
    """Avalia o vendedor com base em cobertura de argumentos, escuta e uso de dados."""
    vendedor = _mensagens_vendedor(historico)
    texto = " ".join(vendedor)
    topicos = set().union(*(detectar_topicos(m) for m in vendedor)) if vendedor else set()
    perguntas = sum(m.count("?") for m in vendedor)
    usou_numeros = bool(re.search(r"\d", texto))
    cedeu_preco = any(ofereceu_desconto(m) for m in vendedor)

    pesos = {
        "nr17": 1.5,
        "garantia": 1.5,
        "tco": 1.5,
        "absenteismo": 1.0,
        "piloto": 1.0,
        "passivo": 0.5,
        "empatia": 0.5,
    }
    nota = 2.0 + sum(peso for t, peso in pesos.items() if t in topicos)
    nota += 0.5 if perguntas else 0
    nota += 0.5 if usou_numeros else 0
    nota -= 1.5 if cedeu_preco else 0
    nota -= 1.0 if len(vendedor) < 3 else 0
    nota = round(max(1, min(10, nota)))

    fortes, melhorias = [], []
    mapa_fortes = {
        "nr17": "Usou a conformidade NR-17 e o laudo como diferencial técnico.",
        "garantia": "Trouxe a garantia de 5 anos para reduzir a percepção de risco.",
        "tco": "Deslocou a conversa do preço para o custo total de posse (TCO/ROI).",
        "absenteismo": "Conectou ergonomia a absenteísmo e produtividade.",
        "piloto": "Propôs um piloto para reduzir o risco da decisão.",
        "passivo": "Mostrou o risco de passivo trabalhista.",
        "empatia": "Validou a preocupação do cliente antes de argumentar (escuta ativa).",
    }
    fortes.extend(frase for t, frase in mapa_fortes.items() if t in topicos)
    if perguntas:
        fortes.append("Fez perguntas para entender o contexto do cliente.")
    if usou_numeros:
        fortes.append("Usou números para sustentar os argumentos.")

    if "nr17" not in topicos:
        melhorias.append(
            "Faltou enfatizar a NR-17: o laudo ergonômico individualizado em PDF, assinado por "
            "engenheiro e ergonomista, é prova imediata em auditorias do Ministério do Trabalho."
        )
    if "garantia" not in topicos:
        melhorias.append(
            "Faltou usar a garantia de 5 anos: ela dilui o investimento e elimina as trocas "
            "frequentes da cadeira barata."
        )
    if "tco" not in topicos:
        melhorias.append("Traga a conta de TCO: custo por dia útil e número de trocas do concorrente em 5 anos.")
    if "absenteismo" not in topicos:
        melhorias.append("Conecte a proposta à redução de até 40% nas queixas e atestados de coluna.")
    if "piloto" not in topicos:
        melhorias.append("Ofereça um piloto sem compromisso (2 posições por 15 dias) para destravar a decisão.")
    if not perguntas:
        melhorias.append("Faça perguntas de diagnóstico (quantos atestados, vida útil atual das cadeiras).")
    if cedeu_preco:
        melhorias.append("Evite oferecer desconto cedo: isso sinaliza gordura no preço e enfraquece o valor.")
    if len(vendedor) < 3:
        melhorias.append("A conversa foi curta; sustente a negociação por mais rodadas.")

    if not fortes:
        fortes.append("Manteve a conversa ativa com o decisor.")
    return {
        "nota": nota,
        "pontos_fortes": fortes,
        "pontos_melhoria": melhorias or ["Continue praticando com objeções mais duras para manter o nível."],
        "fonte": "offline",
    }


def _sistema_persona() -> str:
    return (
        f"Você é {PERSONA_NOME}, {PERSONA_DESCRICAO} Responda em português do Brasil, em no "
        "máximo 3 frases, sustentando objeções com firmeza e pedindo números. Só ceda parcialmente "
        "se o vendedor apresentar NR-17, garantia de 5 anos, TCO/ROI e redução de absenteísmo. "
        "Nunca saia do personagem."
    )


def responder(cliente: LLMClient | None, historico: list[dict]) -> tuple[str, str]:
    """Retorna (resposta, fonte). Usa OpenAI se configurada, senão o motor offline."""
    if cliente and cliente.configurado and _mensagens_vendedor(historico):
        try:
            mensagens = [{"role": "system", "content": _sistema_persona()}, *historico]
            return cliente.conversar(mensagens, temperatura=0.8), "openai"
        except Exception:  # noqa: BLE001
            pass
    return responder_offline(historico), "offline"


def avaliar(cliente: LLMClient | None, historico: list[dict]) -> dict:
    if cliente and cliente.configurado:
        transcricao = "\n".join(
            f"{'Vendedor' if m['role'] == 'user' else PERSONA_NOME}: {m['content']}" for m in historico
        )
        instrucao = (
            "Avalie o vendedor neste role-play de vendas B2B da Taranis Black. Responda apenas com "
            'JSON: {"nota": inteiro 1-10, "pontos_fortes": [..], "pontos_melhoria": [..]}. '
            "Nos pontos de melhoria, aponte onde a argumentação de NR-17 ou garantia de 5 anos "
            "poderia ter sido mais enfática.\n\n" + transcricao
        )
        try:
            dados = cliente.conversar_json([{"role": "user", "content": instrucao}], temperatura=0.2)
            return {
                "nota": int(max(1, min(10, int(dados["nota"])))),
                "pontos_fortes": list(dados["pontos_fortes"]),
                "pontos_melhoria": list(dados["pontos_melhoria"]),
                "fonte": "openai",
            }
        except Exception:  # noqa: BLE001
            pass
    return avaliar_offline(historico)
