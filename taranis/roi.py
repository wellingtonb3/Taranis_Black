"""Calculadora consultiva de ROI e TCO ergonômico (5 anos de garantia)."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ParametrosROI:
    colaboradores: int
    salario_medio: float
    taxa_queixas: float
    preco_ergopro: float
    dias_parados_por_caso: float = 5
    multiplicador_custo: float = 3.0
    reducao_absenteismo: float = 0.40
    preco_cadeira_comum: float = 650.0
    vida_util_comum_meses: int = 18
    horizonte_meses: int = 60
    dias_uteis_mes: int = 22


@dataclass(frozen=True)
class ResultadoROI:
    casos_por_ano: float
    custo_por_caso: float
    custo_absenteismo_anual: float
    economia_absenteismo_anual: float
    investimento_ergopro: float
    custo_total_comum: float
    custo_total_ergopro: float
    economia_liquida: float
    roi_percentual: float
    payback_meses: int | None
    serie: pd.DataFrame


def calcular_roi(p: ParametrosROI) -> ResultadoROI:
    """Compara o custo acumulado de cadeiras comuns (com trocas) e da linha ErgoPro.

    - Custo por caso = dias parados x salário diário x multiplicador (dias parados + reposição).
    - Casos por ano = colaboradores x taxa de queixas/atestados de coluna.
    - ErgoPro reduz o absenteísmo em `reducao_absenteismo` e não precisa de troca no horizonte.
    - Cadeira comum é recomprada a cada `vida_util_comum_meses`.
    """
    salario_diario = p.salario_medio / p.dias_uteis_mes
    custo_por_caso = p.dias_parados_por_caso * salario_diario * p.multiplicador_custo
    casos_por_ano = p.colaboradores * p.taxa_queixas
    absenteismo_anual = casos_por_ano * custo_por_caso
    absenteismo_ergo_anual = absenteismo_anual * (1 - p.reducao_absenteismo)

    investimento_ergo = p.colaboradores * p.preco_ergopro
    lote_comum = p.colaboradores * p.preco_cadeira_comum

    meses, acumulado_comum, acumulado_ergo = [], [], []
    total_comum, total_ergo = 0.0, investimento_ergo
    for mes in range(p.horizonte_meses + 1):
        if mes % p.vida_util_comum_meses == 0 and mes < p.horizonte_meses:
            total_comum += lote_comum
        if mes > 0:
            total_comum += absenteismo_anual / 12
            total_ergo += absenteismo_ergo_anual / 12
        meses.append(mes)
        acumulado_comum.append(total_comum)
        acumulado_ergo.append(total_ergo)

    payback = next(
        (m for m, c, e in zip(meses, acumulado_comum, acumulado_ergo, strict=True) if m > 0 and e <= c),
        None,
    )
    economia = total_comum - total_ergo
    serie = pd.DataFrame(
        {
            "Mês": meses,
            "Cadeira Comum (com trocas)": acumulado_comum,
            "Linha ErgoPro Taranis": acumulado_ergo,
        }
    )
    return ResultadoROI(
        casos_por_ano=casos_por_ano,
        custo_por_caso=custo_por_caso,
        custo_absenteismo_anual=absenteismo_anual,
        economia_absenteismo_anual=absenteismo_anual - absenteismo_ergo_anual,
        investimento_ergopro=investimento_ergo,
        custo_total_comum=total_comum,
        custo_total_ergopro=total_ergo,
        economia_liquida=economia,
        roi_percentual=(economia / investimento_ergo * 100) if investimento_ergo else 0.0,
        payback_meses=payback,
        serie=serie,
    )
