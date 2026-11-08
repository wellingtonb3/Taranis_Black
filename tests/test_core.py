import pytest

from taranis import catalog, email_engine, simulator
from taranis.leads import (
    CUSTOMIZACAO,
    DRYWALL,
    FORNECEDOR,
    ORCAMENTO,
    PRAZO,
    PRECO,
    carregar_leads,
    carregar_matriz,
    classificar_objecao,
    interpretar_produtos,
    mascarar_email,
)
from taranis.llm import LLMClient
from taranis.roi import ParametrosROI, calcular_roi


@pytest.fixture(scope="module")
def leads():
    return carregar_leads()


def test_catalogo_tem_9_produtos_com_garantia_5_anos():
    assert len(catalog.PRODUTOS) == 9
    assert all(p.garantia_anos == 5 for p in catalog.PRODUTOS)
    assert {p.categoria for p in catalog.PRODUTOS} == {"Cadeiras", "Mesas", "Cabines"}


def test_filtro_e_ordenacao():
    mesas = catalog.ordenar_por_preco(catalog.produtos_por_categoria(["Mesas"]), decrescente=True)
    assert [p.preco for p in mesas] == [4800, 3600, 2700]


def test_formatar_brl():
    assert catalog.formatar_brl(1234567.8) == "R$ 1.234.567,80"


@pytest.mark.parametrize(
    "texto,esperado",
    [
        ("Prazo de entrega: Acha o prazo longo", PRAZO),
        ("Preço: Orçamento rígido do semestre", PRECO),
        ("Preço / Custo de Instalação: cabine vs drywall", DRYWALL),
        ("Orçamento Congelado: CFO travou", ORCAMENTO),
        ("Prazo e Pagamento: Quer parcelamento em 10 boletos", ORCAMENTO),
        ("Fornecedor Atual: contrato de 4 anos", FORNECEDOR),
        ("Dúvida de Customização: tecido terracota", CUSTOMIZACAO),
    ],
)
def test_classificar_objecao(texto, esperado):
    assert classificar_objecao(texto) == esperado


def test_planilha_cobre_as_5_objecoes_e_drywall(leads):
    assert len(leads) == 20
    assert set(leads["categoria"]) == {PRECO, DRYWALL, PRAZO, ORCAMENTO, FORNECEDOR, CUSTOMIZACAO}
    assert len(carregar_matriz()) == 5


def test_mascarar_email():
    assert mascarar_email("m.silveira@fincloud.com.br") == "m.***@fincloud.com.br"


def test_interpretar_produtos():
    itens = interpretar_produtos("12x ErgoPro Core + 12x SmartDesk Studio")
    assert [(q, p.sku) for q, p in itens] == [(12, "ERGO-COR"), (12, "DESK-STU140")]


@pytest.mark.parametrize(
    "categoria,trecho",
    [
        (PRECO, "TCO"),
        (PRAZO, "Entrega Escalonada"),
        (DRYWALL, "depreciação"),
        (ORCAMENTO, "30/60/90"),
        (FORNECEDOR, "piloto"),
        (CUSTOMIZACAO, "BIM"),
    ],
)
def test_email_aplica_regra_da_objecao(leads, categoria, trecho):
    lead = leads[leads["categoria"] == categoria].iloc[0].to_dict()
    email = email_engine.gerar_email_offline(lead)
    assert trecho in email["corpo"]
    assert len(email["assunto"].split()) <= 6
    assert "NR-17" in email["corpo"]


def test_todos_os_assuntos_tem_ate_6_palavras(leads):
    for lead in leads.to_dict("records"):
        for tipo in email_engine.TIPOS_EMAIL:
            assert len(email_engine.gerar_email_offline(lead, tipo)["assunto"].split()) <= 6


def test_email_llm_sem_chave_cai_no_offline(leads):
    lead = leads.iloc[0].to_dict()
    email = email_engine.gerar_email_llm(LLMClient(api_key=""), lead)
    assert email["fonte"] == "offline"


def test_roi_payback_e_economia():
    r = calcular_roi(ParametrosROI(colaboradores=200, salario_medio=5000, taxa_queixas=0.15, preco_ergopro=2490))
    assert r.investimento_ergopro == 200 * 2490
    assert r.economia_absenteismo_anual == pytest.approx(r.custo_absenteismo_anual * 0.4)
    assert r.payback_meses is not None and 0 < r.payback_meses <= 60
    assert r.economia_liquida > 0
    assert len(r.serie) == 61


def test_simulador_offline_responde_e_avalia():
    historico = [{"role": "assistant", "content": simulator.ABERTURA}]
    falas = [
        "Entendo, Dr. Roberto. Quantos atestados de coluna vocês tiveram no último ano?",
        "Nossa cadeira tem laudo NR-17 individualizado e garantia de 5 anos.",
        "No TCO de 5 anos a concorrente precisa de 4 trocas; reduzimos 40% do absenteísmo.",
        "Proponho um piloto de 15 dias sem custo.",
    ]
    for fala in falas:
        historico.append({"role": "user", "content": fala})
        resposta, fonte = simulator.responder(None, historico)
        assert fonte == "offline" and resposta
        historico.append({"role": "assistant", "content": resposta})
    assert historico[-1]["content"] == simulator.CONCESSAO
    avaliacao = simulator.avaliar(None, historico)
    assert avaliacao["nota"] >= 8


def test_avaliacao_aponta_nr17_e_garantia_quando_ausentes():
    historico = [
        {"role": "assistant", "content": simulator.ABERTURA},
        {"role": "user", "content": "Posso dar um desconto de 10%."},
    ]
    avaliacao = simulator.avaliar(None, historico)
    assert avaliacao["nota"] <= 3
    texto = " ".join(avaliacao["pontos_melhoria"])
    assert "NR-17" in texto and "garantia" in texto


def test_detectar_topicos_nao_confunde_fornecedor_com_dor():
    assert "absenteismo" not in simulator.detectar_topicos("Já temos um fornecedor")


def test_formatar_brl_compacto():
    assert catalog.formatar_brl_compacto(4693630) == "R$ 4,69 mi"
    assert catalog.formatar_brl_compacto(234681.5) == "R$ 234,7 mil"
