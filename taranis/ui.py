"""Componentes visuais (CSS, ilustrações SVG e cards HTML) do AI Sales Cockpit."""

from __future__ import annotations

from html import escape

from taranis.catalog import LINHAS, Produto, formatar_brl

DOURADO = "#C9A227"
VERDE = "#3FA37C"
CHUMBO = "#1C1E22"
CINZA = "#9AA0A6"

CSS = f"""
<style>
.block-container {{padding-top: 2rem; max-width: 1400px;}}
.tb-header {{display:flex; align-items:center; justify-content:space-between; gap:1rem;
  padding:1.1rem 1.4rem; border:1px solid #2A2D33; border-radius:14px;
  background:linear-gradient(120deg,#16181B 0%,#1F2226 60%,#23251F 100%); margin-bottom:1rem;}}
.tb-logo {{font-size:1.65rem; font-weight:800; letter-spacing:.18em; color:#F5F5F5;}}
.tb-logo span {{color:{DOURADO}; font-weight:500; letter-spacing:.08em;}}
.tb-tag {{color:{CINZA}; font-size:.9rem;}}
.tb-pill {{display:inline-block; padding:.18rem .6rem; border-radius:999px; font-size:.72rem;
  font-weight:600; letter-spacing:.03em; margin:.12rem .2rem .12rem 0;
  border:1px solid #33363C; color:#D8D8D8; background:#24272C;}}
.tb-pill.gold {{border-color:{DOURADO}; color:{DOURADO}; background:rgba(201,162,39,.08);}}
.tb-pill.green {{border-color:{VERDE}; color:{VERDE}; background:rgba(63,163,124,.08);}}
.tb-card {{border:1px solid #2A2D33; border-radius:14px; background:{CHUMBO}; overflow:hidden;
  height:100%; margin-bottom:1rem; transition:border-color .2s, transform .2s;}}
.tb-card:hover {{border-color:{DOURADO}; transform:translateY(-2px);}}
.tb-card .tb-img {{height:170px; display:flex; align-items:center; justify-content:center;
  background:radial-gradient(circle at 50% 40%,#2B2E33 0%,#17191C 75%); position:relative;}}
.tb-card .tb-img .tb-badge {{position:absolute; top:10px; right:10px;}}
.tb-card .tb-body {{padding:.9rem 1.1rem 1.1rem;}}
.tb-card h4 {{margin:0 0 .15rem; color:#F5F5F5; font-size:1.08rem;}}
.tb-price {{color:{DOURADO}; font-size:1.35rem; font-weight:700; margin:.2rem 0 .4rem;}}
.tb-muted {{color:{CINZA}; font-size:.84rem;}}
.tb-card details {{margin-top:.5rem; color:#CFCFCF; font-size:.82rem;}}
.tb-card summary {{cursor:pointer; color:{DOURADO}; font-size:.82rem;}}
.tb-pilar {{border:1px solid #2A2D33; border-left:3px solid {DOURADO}; border-radius:10px;
  padding:.8rem 1rem; background:{CHUMBO}; height:100%;}}
.tb-pilar b {{color:#F5F5F5;}}
.tb-pilar p {{color:{CINZA}; font-size:.86rem; margin:.3rem 0 0;}}
.tb-panel {{border:1px solid #2A2D33; border-radius:12px; padding:1rem 1.1rem; background:{CHUMBO};}}
.tb-panel h4 {{margin:0 0 .3rem; color:#F5F5F5;}}
.tb-panel .tb-label {{color:{CINZA}; font-size:.74rem; text-transform:uppercase; letter-spacing:.06em;
  margin-top:.55rem;}}
.tb-panel .tb-value {{color:#E6E6E6; font-size:.9rem;}}
.tb-lgpd {{border:1px solid {VERDE}; border-radius:10px; padding:.7rem .8rem; font-size:.8rem;
  background:rgba(63,163,124,.07); color:#D9E9E2;}}
.tb-persona {{display:flex; gap:1rem; align-items:center; border:1px solid #2A2D33; border-radius:12px;
  padding:.9rem 1.1rem; background:{CHUMBO}; margin-bottom:.8rem;}}
.tb-avatar {{width:54px; height:54px; border-radius:50%; background:#2B2E33; display:flex;
  align-items:center; justify-content:center; font-weight:700; color:{DOURADO};
  border:1px solid {DOURADO}; flex-shrink:0;}}
.tb-score {{font-size:3rem; font-weight:800; color:{DOURADO}; line-height:1;}}
div[data-testid="stMetric"] {{border:1px solid #2A2D33; border-radius:12px; padding:.7rem .9rem;
  background:{CHUMBO};}}
div[data-testid="stMetricValue"] {{color:#F5F5F5;}}
.stTabs [data-baseweb="tab-list"] {{gap:.4rem;}}
.stTabs [data-baseweb="tab"] {{padding:.5rem 1rem; border-radius:8px 8px 0 0;}}
</style>
"""

SVG_CADEIRA = (
    '<svg width="120" height="140" viewBox="0 0 120 140" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<defs><pattern id="mesh" width="6" height="6" patternUnits="userSpaceOnUse">'
    '<path d="M0 6L6 0" stroke="#3A3D43" stroke-width="1"/></pattern></defs>'
    '<path d="M34 12 Q60 2 86 12 L82 70 Q60 78 38 70 Z" fill="#0E0F11" stroke="#5A5E66" stroke-width="2"/>'
    '<path d="M34 12 Q60 2 86 12 L82 70 Q60 78 38 70 Z" fill="url(#mesh)"/>'
    '<path d="M44 52 Q60 60 76 52" stroke="#C9A227" stroke-width="2.5" stroke-linecap="round"/>'
    '<rect x="28" y="76" width="64" height="12" rx="6" fill="#16181B" stroke="#5A5E66" stroke-width="2"/>'
    '<path d="M24 66 h12 v14 M96 66 h-12 v14" stroke="#5A5E66" stroke-width="3" stroke-linecap="round"/>'
    '<rect x="57" y="88" width="6" height="22" fill="#8A8F98"/>'
    '<path d="M60 110 L28 124 M60 110 L92 124 M60 110 L44 130 M60 110 L76 130" stroke="#8A8F98" '
    'stroke-width="3" stroke-linecap="round"/>'
    '<circle cx="28" cy="126" r="4" fill="#C9A227"/><circle cx="92" cy="126" r="4" fill="#C9A227"/>'
    '<circle cx="44" cy="132" r="4" fill="#C9A227"/><circle cx="76" cy="132" r="4" fill="#C9A227"/>'
    "</svg>"
)

SVG_MESA = (
    '<svg width="170" height="130" viewBox="0 0 170 130" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<rect x="10" y="30" width="150" height="12" rx="3" fill="#8B6A43" stroke="#B48A57" stroke-width="1.5"/>'
    '<rect x="10" y="40" width="150" height="3" fill="#5E4730"/>'
    '<rect x="62" y="12" width="46" height="18" rx="2" fill="#0E0F11" stroke="#5A5E66" stroke-width="2"/>'
    '<rect x="30" y="43" width="10" height="66" fill="#2C2F35" stroke="#5A5E66" stroke-width="1.5"/>'
    '<rect x="130" y="43" width="10" height="66" fill="#2C2F35" stroke="#5A5E66" stroke-width="1.5"/>'
    '<rect x="32" y="62" width="6" height="22" fill="#3A3D43"/>'
    '<rect x="132" y="62" width="6" height="22" fill="#3A3D43"/>'
    '<path d="M18 110 h34 M118 110 h34" stroke="#8A8F98" stroke-width="4" stroke-linecap="round"/>'
    '<rect x="40" y="48" width="90" height="5" rx="2" fill="#2C2F35"/>'
    '<rect x="140" y="34" width="14" height="5" rx="1" fill="#C9A227"/>'
    '<path d="M150 50 v12 M146 54 l4 -4 l4 4 M146 58 l4 4 l4 -4" stroke="#3FA37C" stroke-width="1.6" '
    'stroke-linecap="round"/>'
    "</svg>"
)

SVG_CABINE = (
    '<svg width="130" height="150" viewBox="0 0 130 150" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<rect x="15" y="8" width="100" height="134" rx="4" fill="#8B6A43" stroke="#B48A57" stroke-width="1.5"/>'
    '<rect x="15" y="8" width="100" height="12" fill="#2C2F35"/>'
    '<rect x="25" y="26" width="80" height="108" rx="2" fill="#9EC3D1" fill-opacity=".18" stroke="#9EC3D1" '
    'stroke-opacity=".6" stroke-width="1.5"/>'
    '<path d="M32 34 L50 34 L32 60 Z" fill="#FFFFFF" fill-opacity=".08"/>'
    '<rect x="44" y="92" width="42" height="6" rx="2" fill="#B48A57"/>'
    '<rect x="50" y="98" width="4" height="22" fill="#5A5E66"/>'
    '<rect x="76" y="98" width="4" height="22" fill="#5A5E66"/>'
    '<rect x="96" y="70" width="4" height="22" rx="2" fill="#C9A227"/>'
    '<circle cx="30" cy="14" r="2" fill="#3FA37C"/><circle cx="37" cy="14" r="2" fill="#3FA37C"/>'
    '<path d="M86 13 h20" stroke="#5A5E66" stroke-width="2" stroke-dasharray="3 2"/>'
    "</svg>"
)

ILUSTRACOES = {"ErgoPro": SVG_CADEIRA, "SmartDesk": SVG_MESA, "Silence": SVG_CABINE}


def cabecalho_html() -> str:
    return (
        '<div class="tb-header"><div><div class="tb-logo">TARANIS BLACK <span>| AI Sales Cockpit</span></div>'
        '<div class="tb-tag">Mobiliário corporativo &amp; ergonomia ativa · Inteligência comercial B2B</div></div>'
        '<div><span class="tb-pill gold">NR-17</span><span class="tb-pill gold">Garantia 5 anos</span>'
        '<span class="tb-pill green">Human-in-the-Loop</span></div></div>'
    )


def pilar_html(titulo: str, texto: str) -> str:
    return f'<div class="tb-pilar"><b>{escape(titulo)}</b><p>{escape(texto)}</p></div>'


def card_produto_html(produto: Produto) -> str:
    chips = "".join(f'<span class="tb-pill">{escape(d)}</span>' for d in produto.destaques)
    linha = LINHAS[produto.linha]["titulo"]
    return (
        '<div class="tb-card">'
        f'<div class="tb-img">{ILUSTRACOES[produto.linha]}'
        f'<span class="tb-badge tb-pill gold">Garantia {produto.garantia_anos} anos</span></div>'
        '<div class="tb-body">'
        f'<div class="tb-muted">{escape(linha)}</div>'
        f"<h4>{escape(produto.nome)}</h4>"
        f'<div class="tb-price">{formatar_brl(produto.preco)}</div>'
        f'<div class="tb-muted"><b>Indicado para:</b> {escape(produto.publico)}</div>'
        f'<div style="margin-top:.45rem">{chips}</div>'
        f'<div style="margin-top:.35rem"><span class="tb-pill green">{escape(produto.certificacoes)}</span></div>'
        f"<details><summary>Especificações técnicas</summary>{escape(produto.especificacoes)}</details>"
        "</div></div>"
    )


def painel_html(titulo: str, campos: list[tuple[str, str]]) -> str:
    linhas = "".join(
        f'<div class="tb-label">{escape(rotulo)}</div><div class="tb-value">{escape(str(valor))}</div>'
        for rotulo, valor in campos
    )
    return f'<div class="tb-panel"><h4>{escape(titulo)}</h4>{linhas}</div>'


def persona_html(nome: str, descricao: str) -> str:
    iniciais = "".join(p[0] for p in nome.replace("Dr. ", "").split()[:2])
    return (
        f'<div class="tb-persona"><div class="tb-avatar">{escape(iniciais)}</div>'
        f'<div><b>{escape(nome)}</b><div class="tb-muted">{escape(descricao)}</div></div></div>'
    )


LGPD_HTML = (
    '<div class="tb-lgpd"><b>🔒 Modo Seguro · LGPD</b><br>'
    "Base de leads sintética do Challenge. E-mails são mascarados nas listagens (minimização de dados) "
    "e chaves de API nunca são exibidas na interface.<br><br>"
    "<b>👤 Human-in-the-Loop obrigatório</b><br>"
    "Todo conteúdo gerado por IA é um rascunho: o vendedor deve revisar e aprovar antes de qualquer "
    "envio ao cliente.</div>"
)
