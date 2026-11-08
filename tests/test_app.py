from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent.parent / "app.py"


def test_app_renderiza_sem_erros():
    at = AppTest.from_file(str(APP), default_timeout=60).run()
    assert not at.exception
    abrir = [b for b in at.button if b.label.startswith("Abrir solução")]
    assert len(abrir) == 4
    assert any("Baixar relatório" in b.label for b in at.get("download_button"))


def test_navegacao_capa_e_voltar():
    at = AppTest.from_file(str(APP), default_timeout=60).run()
    for secao in ("crm", "simulador", "roi", "catalogo"):
        at.button(key=f"abrir_{secao}").click().run()
        assert not at.exception
        assert at.session_state.secao == secao
        at.button(key=f"voltar_{secao}").click().run()
        assert at.session_state.secao == "capa"


def test_gerar_email_e_simulador():
    at = AppTest.from_file(str(APP), default_timeout=60).run()
    at.button(key="abrir_crm").click().run()
    gerar = next(b for b in at.button if "Gerar E-mail" in b.label)
    gerar.click().run()
    assert not at.exception
    assert any("Assunto" in t.label for t in at.text_input)
    assert any("Corpo" in t.label for t in at.text_area)

    at.button(key="voltar_crm").click().run()
    at.button(key="abrir_simulador").click().run()

    at.chat_input[0].set_value("Entendo. Temos laudo NR-17 e garantia de 5 anos.").run()
    assert not at.exception
    encerrar = next(b for b in at.button if "Encerrar" in b.label)
    encerrar.click().run()
    assert not at.exception
    assert any("Relatório" in m.value for m in at.markdown)
