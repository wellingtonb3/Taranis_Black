"""Taranis Black - AI Sales Cockpit (Rota 1 B2B). Execute com: streamlit run app.py"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from taranis import catalog, email_engine, simulator, ui
from taranis.leads import carregar_leads, carregar_matriz, mascarar_email, matriz_por_categoria
from taranis.llm import LLMClient
from taranis.roi import ParametrosROI, calcular_roi

st.set_page_config(page_title="Taranis Black | AI Sales Cockpit", page_icon="🖤", layout="wide")
st.markdown(ui.CSS, unsafe_allow_html=True)


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


def main() -> None:
    cliente = barra_lateral(obter_cliente_llm())
    st.markdown(ui.cabecalho_html(), unsafe_allow_html=True)
    abas = st.tabs(
        [
            "🏢 Visão Geral & Catálogo",
            "🎯 CRM B2B & E-mails",
            "🥊 Simulador de Objeções",
            "📊 Calculadora ROI & TCO",
        ]
    )
    with abas[0]:
        aba_catalogo()
    with abas[1]:
        aba_crm(cliente)
    with abas[2]:
        aba_simulador(cliente)
    with abas[3]:
        aba_roi()


main()
