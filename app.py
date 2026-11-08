"""Taranis Black - AI Sales Cockpit (Rota 1 B2B). Execute com: streamlit run app.py"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from taranis import catalog, email_engine, relatorio, simulator, ui
from taranis.leads import carregar_leads, carregar_matriz, mascarar_email, matriz_por_categoria
from taranis.llm import LLMClient
from taranis.roi import ParametrosROI, calcular_roi

st.set_page_config(page_title="Taranis Black | AI Sales Cockpit", page_icon="🖤", layout="wide")
st.markdown(ui.CSS, unsafe_allow_html=True)
st.markdown(ui.CSS_CAPA, unsafe_allow_html=True)

SECOES = {
    "capa": "🏠 Capa · Dores & Soluções",
    "crm": "🎯 CRM B2B & E-mails",
    "simulador": "🥊 Simulador de Objeções",
    "roi": "📊 Calculadora ROI & TCO",
    "catalogo": "🏢 Catálogo & Políticas",
}


@st.cache_resource
def obter_cliente_llm() -> LLMClient:
    return LLMClient()


@st.cache_data
def obter_leads() -> pd.DataFrame:
    return carregar_leads()


@st.cache_data
def obter_matriz() -> list[dict]:
    return carregar_matriz()


def barra_lateral(cliente: LLMClient) -> LLMClient | None:
    """Renderiza a barra lateral e retorna o cliente LLM ativo (ou None no modo offline)."""
    with st.sidebar:
        st.markdown("### 🖤 TARANIS BLACK")
        st.caption("AI Sales Cockpit · Rota 1 B2B · Challenge ONE G11")
        st.divider()
        st.radio("**Navegação**", list(SECOES), format_func=SECOES.get, key="secao")
        st.divider()
        st.markdown("**Motor de IA**")
        ativo = None
        if cliente.configurado:
            usar = st.toggle(f"Usar {cliente.provedor} ({cliente.modelo})", value=True)
            ativo = cliente if usar else None
        else:
            st.info(
                "Modo **offline** (determinístico) ativo. Para ativar a IA, defina "
                "`DEEPSEEK_API_KEY` ou `OPENAI_API_KEY` em `.streamlit/secrets.toml` "
                "ou como variável de ambiente.",
                icon="🧠",
            )
        st.caption("Status: " + (f"🟢 {ativo.provedor}" if ativo else "⚪ Offline"))
        st.divider()
        st.markdown(ui.LGPD_HTML, unsafe_allow_html=True)
    return ativo


def aba_catalogo() -> None:
    st.markdown("#### Ergonomia corporativa que reduz absenteísmo e protege a sua empresa")
    st.markdown(
        "A Taranis Black combina engenharia ergonômica baseada em laudos clínicos, tecnologia embarcada "
        "e design contemporâneo, alinhados à **NR-17**, para escritórios modernos e ambientes híbridos."
    )
    pilares = st.columns(3)
    pilares[0].markdown(
        ui.pilar_html("Laudo NR-17 incluso", catalog.POLITICAS_COMERCIAIS["Laudo NR-17"]), unsafe_allow_html=True
    )
    pilares[1].markdown(
        ui.pilar_html("Garantia Taranis 5 anos", catalog.POLITICAS_COMERCIAIS["Garantia Taranis"]),
        unsafe_allow_html=True,
    )
    pilares[2].markdown(
        ui.pilar_html("Frete CIF e faturamento", catalog.POLITICAS_COMERCIAIS["Frete CIF/FOB"]), unsafe_allow_html=True
    )
    st.write("")

    filtro, ordem = st.columns([3, 1])
    categorias = ["Cadeiras", "Mesas", "Cabines"]
    selecionadas = filtro.pills("Linha de produto", categorias, selection_mode="multi", default=categorias)
    ordenacao = ordem.selectbox("Ordenar por valor", ["Menor preço", "Maior preço"])

    produtos = catalog.ordenar_por_preco(
        catalog.produtos_por_categoria(selecionadas or None), decrescente=ordenacao == "Maior preço"
    )
    colunas = st.columns(3)
    for i, produto in enumerate(produtos):
        colunas[i % 3].markdown(ui.card_produto_html(produto), unsafe_allow_html=True)

    with st.expander("📋 Políticas comerciais B2B"):
        for titulo, texto in catalog.POLITICAS_COMERCIAIS.items():
            st.markdown(f"**{titulo}:** {texto}")


def _preencher_email(lead: dict, tipo: str, cliente: LLMClient | None) -> None:
    if cliente:
        email = email_engine.gerar_email_llm(cliente, lead, tipo)
    else:
        email = email_engine.gerar_email_offline(lead, tipo)
    st.session_state[f"assunto_{lead['id']}"] = email["assunto"]
    st.session_state[f"corpo_{lead['id']}"] = email["corpo"]
    st.session_state[f"meta_{lead['id']}"] = email
    st.session_state[f"aprovado_{lead['id']}"] = False


def aba_crm(cliente: LLMClient | None) -> None:
    leads = obter_leads()
    matriz = obter_matriz()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Leads no CRM", len(leads))
    m2.metric("Pipeline estimado", catalog.formatar_brl_compacto(leads["valor"].sum()))
    m3.metric("Aguardando contorno", int((leads["status"] == "Aguardando Contorno").sum()))
    m4.metric("Ticket médio", catalog.formatar_brl_compacto(leads["valor"].mean()))

    f1, f2 = st.columns(2)
    segmentos = f1.multiselect("Segmento", sorted(leads["segmento"].unique()), placeholder="Todos")
    objecoes = f2.multiselect("Tipo de objeção", sorted(leads["objecao_tipo"].unique()), placeholder="Todas")
    filtrados = leads
    if segmentos:
        filtrados = filtrados[filtrados["segmento"].isin(segmentos)]
    if objecoes:
        filtrados = filtrados[filtrados["objecao_tipo"].isin(objecoes)]
    filtrados = filtrados.reset_index(drop=True)

    tabela, painel = st.columns([1.75, 1])
    with tabela:
        st.caption("Selecione um lead na tabela para ver os detalhes e gerar o e-mail.")
        visao = pd.DataFrame(
            {
                "ID": filtrados["id"],
                "Empresa": filtrados["empresa"],
                "Segmento": filtrados["segmento"],
                "Porte": filtrados["porte"],
                "Decisor": filtrados["decisor_nome"],
                "Cargo": filtrados["decisor_cargo"],
                "E-mail": filtrados["email"].map(mascarar_email),
                "Objeção": filtrados["objecao_tipo"],
                "Valor (R$)": filtrados["valor"],
                "Status": filtrados["status"],
            }
        )
        evento = st.dataframe(
            visao,
            hide_index=True,
            use_container_width=True,
            height=420,
            on_select="rerun",
            selection_mode="single-row",
            key="tabela_leads",
            column_config={"Valor (R$)": st.column_config.NumberColumn(format="R$ %.2f")},
        )
    if filtrados.empty:
        painel.warning("Nenhum lead encontrado com os filtros atuais.")
        return
    linhas = evento.selection.rows if evento and evento.selection else []
    lead = filtrados.iloc[linhas[0] if linhas else 0].to_dict()

    with painel:
        mostrar_contato = st.toggle("Exibir contato completo (uso interno)", value=False)
        contato = lead["email"] if mostrar_contato else mascarar_email(lead["email"])
        st.markdown(
            ui.painel_html(
                f"{lead['id']} · {lead['empresa']}",
                [
                    ("Segmento / Porte", f"{lead['segmento']} · {lead['porte']} colaboradores"),
                    ("Decisor", f"{lead['decisor_nome']} — {lead['decisor_cargo']}"),
                    ("Contato", contato),
                    ("Produtos em cotação", lead["produtos"]),
                    ("Valor estimado", catalog.formatar_brl(float(lead["valor"]))),
                    ("Dores registradas", lead["dores"]),
                    ("Objeção atual", lead["objecao"]),
                    ("Status / Último contato", f"{lead['status']} · {lead['ultimo_contato']}"),
                ],
            ),
            unsafe_allow_html=True,
        )

    st.divider()
    regra = matriz_por_categoria(matriz, lead["categoria"])
    st.markdown(f"#### 🎯 Playbook da objeção: **{lead['objecao_tipo']}** ({regra.get('id', '')})")
    p1, p2, p3 = st.columns(3)
    p1.error(f"**O que NÃO dizer**\n\n{regra.get('argumento_fraco', '')}")
    p2.success(f"**Argumento consultivo**\n\n{regra.get('argumento_forte', '')}")
    p3.info(f"**Evidência de apoio**\n\n{regra.get('evidencia', '')}")

    st.markdown("#### ✉️ Gerador de E-mail Inteligente")
    c1, c2 = st.columns([1, 3])
    tipo = c1.radio("Tipo de e-mail", email_engine.TIPOS_EMAIL, key=f"tipo_{lead['id']}")
    c2.write("")
    c2.button(
        "✨ Gerar E-mail com IA",
        type="primary",
        on_click=_preencher_email,
        args=(lead, tipo, cliente),
        key=f"gerar_{lead['id']}",
    )

    meta = st.session_state.get(f"meta_{lead['id']}")
    if not meta:
        st.caption("Clique em **Gerar E-mail com IA** para criar o rascunho com base na regra da objeção.")
        return
    if meta.get("aviso"):
        st.warning(meta["aviso"])
    fonte = "motor offline" if meta["fonte"] == "offline" else meta["fonte"]
    st.caption(f"Regra aplicada: **{meta['regra']}** · Gerado por {fonte} · Rascunho editável")

    assunto = st.text_input("Assunto (máx. 6 palavras)", key=f"assunto_{lead['id']}")
    palavras = len(assunto.split())
    if palavras > email_engine.MAX_PALAVRAS_ASSUNTO:
        st.warning(f"O assunto tem {palavras} palavras; o recomendado é no máximo 6.")
    corpo = st.text_area("Corpo do e-mail", key=f"corpo_{lead['id']}", height=380)

    aprovado = st.checkbox("Revisei o conteúdo e aprovo o envio (Human-in-the-Loop)", key=f"aprovado_{lead['id']}")
    if aprovado:
        texto_final = f"Para: {lead['email']}\nAssunto: {assunto}\n\n{corpo}"
        st.caption("Use o ícone de copiar no canto do bloco para levar o e-mail à área de transferência.")
        st.code(texto_final, language=None, wrap_lines=True)
        st.download_button(
            "⬇️ Baixar .txt",
            texto_final,
            file_name=f"email_{lead['id'].lstrip('#')}.txt",
            key=f"download_{lead['id']}",
        )
    else:
        st.caption("Aprove o rascunho para liberar a cópia e o download.")


def aba_simulador(cliente: LLMClient | None) -> None:
    st.markdown(ui.persona_html(simulator.PERSONA_NOME, simulator.PERSONA_DESCRICAO), unsafe_allow_html=True)
    if "chat" not in st.session_state:
        st.session_state.chat = [{"role": "assistant", "content": simulator.ABERTURA}]
        st.session_state.avaliacao = None

    with st.expander("💡 Dicas para o role-play"):
        st.markdown(
            "- Valide a preocupação antes de argumentar.\n"
            "- Use **NR-17** (laudo individualizado), **garantia de 5 anos** e **TCO/payback**.\n"
            "- Conecte a proposta à redução de **absenteísmo** e ofereça um **piloto**.\n"
            "- Evite oferecer desconto logo de início."
        )

    conversa = st.container(height=430)
    with conversa:
        for msg in st.session_state.chat:
            avatar = "🧑‍💼" if msg["role"] == "user" else "🕴️"
            st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

    encerrado = st.session_state.avaliacao is not None
    mensagem = st.chat_input("Sua resposta ao Dr. Roberto...", disabled=encerrado, key="chat_input_simulador")
    if mensagem:
        st.session_state.chat.append({"role": "user", "content": mensagem})
        with conversa:
            st.chat_message("user", avatar="🧑‍💼").write(mensagem)
            with st.spinner("Dr. Roberto está pensando..."):
                resposta, _ = simulator.responder(cliente, st.session_state.chat)
            st.session_state.chat.append({"role": "assistant", "content": resposta})
            st.chat_message("assistant", avatar="🕴️").write(resposta)

    b1, b2, _ = st.columns([1.3, 1, 3])
    vendedor_falou = any(m["role"] == "user" for m in st.session_state.chat)
    if b1.button("🏁 Encerrar Simulação & Avaliar", type="primary", disabled=encerrado or not vendedor_falou):
        with st.spinner("Analisando o diálogo..."):
            st.session_state.avaliacao = simulator.avaliar(cliente, st.session_state.chat)
        st.rerun()
    if b2.button("🔄 Reiniciar simulação"):
        st.session_state.chat = [{"role": "assistant", "content": simulator.ABERTURA}]
        st.session_state.avaliacao = None
        st.rerun()

    avaliacao = st.session_state.avaliacao
    if avaliacao:
        st.markdown("#### 📝 Relatório de Desempenho")
        nota_col, fortes_col, melhorias_col = st.columns([1, 2, 2])
        with nota_col:
            st.markdown(f'<div class="tb-score">{avaliacao["nota"]}/10</div>', unsafe_allow_html=True)
            st.progress(avaliacao["nota"] / 10)
            st.caption("Avaliado por " + ("motor offline" if avaliacao["fonte"] == "offline" else avaliacao["fonte"]))
        with fortes_col:
            st.markdown("**✅ Pontos fortes**")
            st.markdown("\n".join(f"- {p}" for p in avaliacao["pontos_fortes"]))
        with melhorias_col:
            st.markdown("**🔧 Pontos de melhoria**")
            st.markdown("\n".join(f"- {p}" for p in avaliacao["pontos_melhoria"]))


def aba_roi() -> None:
    st.markdown("Use ao vivo com RH e Financeiro para traduzir ergonomia em retorno financeiro.")
    modelos = {p.nome: p for p in catalog.ergopro()}
    i1, i2, i3, i4 = st.columns(4)
    colaboradores = i1.number_input("Número de colaboradores", min_value=1, value=200, step=10)
    salario = i2.number_input("Salário médio mensal (R$)", min_value=0.0, value=5000.0, step=250.0)
    taxa = i3.slider("Taxa de queixas/atestados de coluna (%)", 1, 40, 15)
    modelo = i4.selectbox("Modelo ErgoPro", list(modelos), index=1)

    with st.expander("⚙️ Premissas avançadas"):
        a1, a2, a3, a4, a5 = st.columns(5)
        dias = a1.number_input("Dias parados por caso", min_value=0.0, value=5.0, step=1.0)
        mult = a2.slider("Custo total (x salário diário)", 1.0, 3.0, 3.0, 0.1, help="Dias parados + reposição: até 3x.")
        reducao = a3.slider("Redução de absenteísmo (%)", 0, 60, 40)
        preco_comum = a4.number_input("Cadeira comum (R$)", min_value=0.0, value=650.0, step=50.0)
        vida_comum = a5.number_input("Vida útil comum (meses)", min_value=1, value=18, step=1)

    r = calcular_roi(
        ParametrosROI(
            colaboradores=int(colaboradores),
            salario_medio=salario,
            taxa_queixas=taxa / 100,
            preco_ergopro=modelos[modelo].preco,
            dias_parados_por_caso=dias,
            multiplicador_custo=mult,
            reducao_absenteismo=reducao / 100,
            preco_cadeira_comum=preco_comum,
            vida_util_comum_meses=int(vida_comum),
        )
    )

    k = st.columns(3)
    k[0].metric("Custo anual de absenteísmo (atual)", catalog.formatar_brl(r.custo_absenteismo_anual))
    k[1].metric("Investimento ErgoPro", catalog.formatar_brl(r.investimento_ergopro))
    k[2].metric("Economia anual com absenteísmo", catalog.formatar_brl(r.economia_absenteismo_anual))
    k = st.columns(3)
    k[0].metric("Payback", f"{r.payback_meses} meses" if r.payback_meses else "> 60 meses")
    k[1].metric("ROI em 5 anos", f"{r.roi_percentual:.1f}%".replace(".", ","))
    k[2].metric("Economia líquida em 5 anos", catalog.formatar_brl(r.economia_liquida))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=r.serie["Mês"],
            y=r.serie["Cadeira Comum (com trocas)"],
            name="Cadeira Comum (com trocas)",
            line={"color": ui.CINZA, "width": 3, "shape": "hv"},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=r.serie["Mês"],
            y=r.serie["Linha ErgoPro Taranis"],
            name=f"Linha ErgoPro Taranis ({modelo})",
            line={"color": ui.DOURADO, "width": 3},
        )
    )
    if r.payback_meses:
        fig.add_vline(
            x=r.payback_meses,
            line_dash="dot",
            line_color=ui.VERDE,
            annotation_text=f"Payback: mês {r.payback_meses}",
            annotation_font_color=ui.VERDE,
        )
    fig.update_layout(
        title="Custo acumulado em 5 anos",
        template="plotly_dark",
        height=430,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Mês",
        yaxis_title="Custo acumulado (R$)",
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.2},
        separators=",.",
    )
    fig.update_yaxes(tickprefix="R$ ", tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("🧮 Memória de cálculo"):
        st.markdown(
            f"- Casos/ano = {int(colaboradores)} × {taxa}% = **{r.casos_por_ano:.0f}**\n"
            f"- Custo por caso = {dias:g} dias × salário diário ({catalog.formatar_brl(salario / 22)}) × {mult:g} "
            f"= **{catalog.formatar_brl(r.custo_por_caso)}**\n"
            f"- Cadeira comum recomprada a cada {int(vida_comum)} meses; ErgoPro sem troca em 5 anos (garantia).\n"
            f"- ErgoPro reduz o absenteísmo em {reducao}%.\n"
            f"- ROI = economia líquida em 5 anos ÷ investimento ErgoPro. Payback = primeiro mês em que o custo "
            f"acumulado ErgoPro fica abaixo do da cadeira comum.\n\n"
            "_Estimativa consultiva; valide as premissas com o cliente._"
        )


def ir_para(secao: str) -> None:
    st.session_state.secao = secao


@st.cache_data
def obter_relatorio() -> list[str]:
    return relatorio.carregar_paragrafos()


DORES = (
    (
        "crm",
        "Objeções travando o pipeline",
        "{n} leads parados em 5 objeções (orçamento, preço, fornecedor, prazo e customização), "
        "somando {valor}. E-mails genéricos e CRM manual consomem 40% da semana do vendedor.",
        "CRM B2B & Gerador de E-mails com IA",
        "Seleciona o lead, identifica a objeção e gera o e-mail consultivo certo, com revisão humana.",
    ),
    (
        "simulador",
        "Vendedor despreparado para o comprador cético",
        "Respostas fracas como “nossa qualidade é melhor” ou “me ligue ano que vem” perdem o timing "
        "diante de um concorrente 35% mais barato.",
        "Simulador de Objeções (Role-Play)",
        "Treino com o Dr. Roberto Mendes, diretor cético, e avaliação de 1 a 10 com pontos de melhoria.",
    ),
    (
        "roi",
        "Venda pelo preço, não pelo valor",
        "Sem números de absenteísmo, TCO e payback, a conversa vira desconto e a margem desaparece.",
        "Calculadora ROI & TCO Ergonômico",
        "Calcula ao vivo, na reunião, economia anual, payback e ROI de 5 anos frente à cadeira comum.",
    ),
    (
        "catalogo",
        "Falta de prova técnica na mão do vendedor",
        "NR-17, garantia de 5 anos, certificações e políticas comerciais ficam espalhadas em PDFs.",
        "Catálogo Interativo & Políticas B2B",
        "9 produtos com especificações, preços, garantia, certificações e condições comerciais.",
    ),
)


def pagina_capa() -> None:
    leads = obter_leads()
    valor = catalog.formatar_brl_compacto(leads["valor"].sum())
    kpis_dor = [("40%", "do tempo do vendedor em tarefas manuais"), (valor, f"travados em {len(leads)} leads")]
    st.markdown(ui.hero_html(kpis_dor, relatorio.KPIS_RELATORIO), unsafe_allow_html=True)

    st.markdown('<div class="tb-secao">As 4 dores e as soluções</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="tb-secao-sub">Vermelho: o problema · Verde: a solução no cockpit</div>',
        unsafe_allow_html=True,
    )
    for linha in (DORES[:2], DORES[2:]):
        colunas = st.columns(2, gap="large")
        for coluna, (secao, dor, evidencia, solucao, como) in zip(colunas, linha, strict=True):
            numero = list(SECOES).index(secao)
            with coluna:
                texto = evidencia.format(n=len(leads), valor=valor)
                st.markdown(ui.dor_card_html(numero, dor, texto, solucao, como), unsafe_allow_html=True)
                st.button(
                    f"Abrir solução {numero} →",
                    key=f"abrir_{secao}",
                    type="primary",
                    use_container_width=True,
                    on_click=ir_para,
                    args=(secao,),
                )

    st.markdown('<div class="tb-secao">📄 Relatório Executivo</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="tb-secao-sub">Diagnóstico e plano de IA apresentado à CEO da Taranis Black</div>',
        unsafe_allow_html=True,
    )
    if not relatorio.RELATORIO_PATH.exists():
        st.info("Relatório executivo não encontrado em `docs/`.")
        return
    paragrafos = obter_relatorio()
    st.markdown(ui.email_ceo_html(relatorio.resumo_executivo(paragrafos)), unsafe_allow_html=True)
    ler, baixar = st.columns([3, 1])
    with ler, st.expander("Ler relatório completo"):
        st.markdown(ui.relatorio_html(paragrafos, relatorio.eh_titulo), unsafe_allow_html=True)
    with baixar:
        st.download_button(
            "⬇️ Baixar relatório (.docx)",
            data=relatorio.RELATORIO_PATH.read_bytes(),
            file_name=relatorio.RELATORIO_PATH.name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )


def topo_secao(secao: str) -> None:
    titulo, voltar = st.columns([5, 1])
    titulo.markdown(f"### {SECOES[secao]}")
    voltar.button("← Voltar à capa", key=f"voltar_{secao}", on_click=ir_para, args=("capa",), use_container_width=True)


def rolar_para_topo(secao: str) -> None:
    components.html(
        f"<script>/* {secao} */ const d = window.parent.document;"
        "(d.querySelector('[data-testid=\"stMain\"]') || d.documentElement).scrollTo(0, 0);</script>",
        height=0,
    )


CHAVES_PERSISTENTES = ("tipo_", "assunto_", "corpo_", "aprovado_")


def preservar_rascunhos() -> None:
    """Mantém o rascunho do e-mail quando a seção CRM não é renderizada (Streamlit limpa widgets ocultos)."""
    for chave in list(st.session_state):
        if isinstance(chave, str) and chave.startswith(CHAVES_PERSISTENTES):
            st.session_state[chave] = st.session_state[chave]


def main() -> None:
    st.session_state.setdefault("secao", "capa")
    preservar_rascunhos()
    cliente = barra_lateral(obter_cliente_llm())
    st.markdown(ui.cabecalho_html(), unsafe_allow_html=True)
    secao = st.session_state.secao
    if st.session_state.get("_secao_anterior") != secao:
        st.session_state._secao_anterior = secao
        rolar_para_topo(secao)
    if secao == "capa":
        pagina_capa()
        return
    topo_secao(secao)
    if secao == "crm":
        aba_crm(cliente)
    elif secao == "simulador":
        aba_simulador(cliente)
    elif secao == "roi":
        aba_roi()
    else:
        aba_catalogo()


main()
