"""Leitura do Relatório Executivo (.docx) exibido na capa do cockpit."""

from __future__ import annotations

import re
import zipfile
from html import unescape
from pathlib import Path

RELATORIO_PATH = Path(__file__).resolve().parent.parent / "docs" / "relatorio_executivo_taranis_black_rota1.docx"

KPIS_RELATORIO = (
    ("10h/semana", "resgatadas por vendedor"),
    ("+18%", "conversão de propostas"),
    ("380%", "ROI estimado no 1º ano"),
    ("85%", "adoção da equipe em 45 dias"),
)

_TITULO = re.compile(r"^(Etapa \d|PARTE \d|Resumo Executivo|[^\w\s(\"'“])")


def carregar_paragrafos(caminho: Path | str = RELATORIO_PATH) -> list[str]:
    """Extrai os parágrafos de texto do .docx sem dependências externas."""
    xml = zipfile.ZipFile(caminho).read("word/document.xml").decode("utf-8")
    paragrafos = []
    for bloco in re.findall(r"<w:p[ >].*?</w:p>", xml, re.DOTALL):
        texto = unescape("".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", bloco, re.DOTALL))).strip()
        if texto:
            paragrafos.append(texto)
    return paragrafos


def eh_titulo(paragrafo: str) -> bool:
    return bool(_TITULO.match(paragrafo)) and not paragrafo.startswith(("💡", "•", "-"))


def resumo_executivo(paragrafos: list[str]) -> list[str]:
    """Retorna o e-mail à CEO (de 'Prezada CEO,' até o parágrafo de impacto projetado)."""
    try:
        inicio = next(i for i, p in enumerate(paragrafos) if p.startswith("Prezada"))
    except StopIteration:
        return []
    fim = next((i for i in range(inicio, len(paragrafos)) if paragrafos[i].startswith("Impacto")), inicio)
    return paragrafos[inicio : fim + 1]
