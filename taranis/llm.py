"""Camada de integração com a OpenAI, com fallback determinístico offline."""

from __future__ import annotations

import json
import os
import re

MODELO_PADRAO = "gpt-4o-mini"


def _ler_segredo(nome: str) -> str | None:
    """Busca o valor em st.secrets e, em seguida, nas variáveis de ambiente."""
    try:
        import streamlit as st

        valor = st.secrets.get(nome)
        if valor:
            return str(valor)
    except Exception:  # noqa: BLE001 - secrets.toml ausente ou fora do Streamlit
        pass
    return os.environ.get(nome) or None


class LLMClient:
    """Cliente simples para Chat Completions. Nunca expõe a chave para a interface."""

    def __init__(self, api_key: str | None = None, modelo: str | None = None):
        self._api_key = api_key if api_key is not None else _ler_segredo("OPENAI_API_KEY")
        self.modelo = modelo or _ler_segredo("OPENAI_MODEL") or MODELO_PADRAO
        self._cliente = None
        self.erro_importacao: str | None = None
        if self._api_key:
            try:
                from openai import OpenAI

                self._cliente = OpenAI(api_key=self._api_key)
            except ImportError as exc:
                self.erro_importacao = str(exc)

    @property
    def configurado(self) -> bool:
        return self._cliente is not None

    def conversar(self, mensagens: list[dict], temperatura: float = 0.7) -> str:
        if not self.configurado:
            raise RuntimeError("LLM não configurado.")
        resposta = self._cliente.chat.completions.create(model=self.modelo, messages=mensagens, temperature=temperatura)
        return (resposta.choices[0].message.content or "").strip()

    def conversar_json(self, mensagens: list[dict], temperatura: float = 0.4) -> dict:
        texto = self.conversar(mensagens, temperatura)
        return extrair_json(texto)


def extrair_json(texto: str) -> dict:
    """Extrai o primeiro objeto JSON de uma resposta do modelo."""
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if not match:
        raise ValueError("Resposta do modelo sem JSON.")
    return json.loads(match.group(0))
