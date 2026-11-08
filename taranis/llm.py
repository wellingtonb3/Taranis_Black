"""Camada de integração com LLMs compatíveis com a API da OpenAI (DeepSeek ou OpenAI)."""

from __future__ import annotations

import json
import os
import re

PROVEDORES = {
    "deepseek": {
        "nome": "DeepSeek",
        "chave": "DEEPSEEK_API_KEY",
        "modelo_var": "DEEPSEEK_MODEL",
        "modelo": "deepseek-chat",
        "base_url": "https://api.deepseek.com",
    },
    "openai": {
        "nome": "OpenAI",
        "chave": "OPENAI_API_KEY",
        "modelo_var": "OPENAI_MODEL",
        "modelo": "gpt-4o-mini",
        "base_url": None,
    },
}
MODELO_PADRAO = PROVEDORES["openai"]["modelo"]


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


def _detectar_provedor() -> tuple[str, str | None]:
    """Retorna o primeiro provedor com chave configurada (DeepSeek tem prioridade)."""
    for codigo, cfg in PROVEDORES.items():
        chave = _ler_segredo(cfg["chave"])
        if chave:
            return codigo, chave
    return "openai", None


class LLMClient:
    """Cliente simples para Chat Completions. Nunca expõe a chave para a interface."""

    def __init__(self, api_key: str | None = None, modelo: str | None = None, provedor: str | None = None):
        if api_key is not None:
            codigo = provedor or "openai"
        else:
            codigo, api_key = _detectar_provedor()
        cfg = PROVEDORES[codigo]
        self._api_key = api_key
        self.provedor = cfg["nome"]
        self.modelo = modelo or _ler_segredo(cfg["modelo_var"]) or cfg["modelo"]
        self._cliente = None
        self.erro_importacao: str | None = None
        if self._api_key:
            try:
                from openai import OpenAI

                self._cliente = OpenAI(api_key=self._api_key, base_url=cfg["base_url"])
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
