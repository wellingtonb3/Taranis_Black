# TARANIS BLACK | AI Sales Cockpit (Rota 1 B2B)

Plataforma comercial inteligente desenvolvida para o **Challenge Alura Oracle ONE G11 — AI for Business**.
Ela apoia a força de vendas B2B da Taranis Black (empresa fictícia de ergonomia corporativa, R$ 48M/ano e
280 colaboradores) a qualificar leads, contornar objeções com argumentos de valor, treinar negociação e
traduzir ergonomia em retorno financeiro ao vivo com o cliente.

> Funciona **100% offline** (motor determinístico) e, opcionalmente, com a **DeepSeek** ou a **OpenAI** quando uma chave é configurada.

---

## O problema da Taranis Black e como o app resolve

| Dor da força de vendas | Solução no AI Sales Cockpit |
|---|---|
| Vendedores sem domínio técnico do portfólio (NR-17, garantias, políticas) | **Aba 1** – catálogo interativo com fichas técnicas, preços, público indicado e políticas comerciais |
| E-mails genéricos que não respondem à objeção real do cliente | **Aba 2** – CRM com os 20 leads da base e gerador de e-mail com regras **IF/ELSE** para as 5 objeções mapeadas |
| Baixa preparação para negociar com decisores céticos | **Aba 3** – role-play com o *Dr. Roberto Mendes* (Nexus Corp) e avaliação com nota, pontos fortes e de melhoria |
| Dificuldade em provar valor para RH/Financeiro | **Aba 4** – calculadora de ROI, payback e TCO de 5 anos com gráfico interativo |
| Risco de uso irresponsável de IA e dados pessoais | Modo Seguro LGPD, e-mails mascarados, chave de API nunca exibida e **Human-in-the-Loop** obrigatório |

## Módulos

### 🏢 Aba 1 – Visão Geral & Catálogo Interativo
- Cabeçalho executivo, propósito da empresa, laudo NR-17 e garantia Taranis de 5 anos.
- Cards com ilustração, especificações técnicas, público indicado, preço e badge de garantia.
- Filtro por linha (Cadeiras, Mesas, Cabines) e ordenação por valor.

### 🎯 Aba 2 – CRM B2B & Gerador de E-mails Inteligente
- Lê `data/02_Leads_B2B_Comercial.xlsx` (aba de leads + matriz de objeções).
- Tabela interativa com filtros por segmento e tipo de objeção; painel lateral com os detalhes do lead.
- Playbook da objeção: o que **não** dizer, argumento consultivo e evidência de apoio.
- **Regras IF/ELSE** (`taranis/email_engine.py → argumento_por_objecao`):

| Objeção | Argumento aplicado |
|---|---|
| Preço | TCO em 5 anos, custo por dia útil e trocas de cadeiras descartáveis (vida útil de 14 meses) |
| Drywall vs Cabine | Mobilidade patrimonial e depreciação fiscal da Cabine Silence (ativo imobilizado) |
| Prazo | Entrega Escalonada: lote prioritário em até 10 dias (7 dias úteis) pelo CD de Santa Catarina |
| Orçamento | Faturamento 30/60/90 dias, OPEX vs CAPEX e economia com redução de atestados |
| Fornecedor Atual | Piloto sem compromisso de 2 posições por 15 dias com ergonomistas certificados |
| Customização | Personalização sem custo acima de 30 posições, FSC, blocos BIM e amostras em 48h |

- Botão **Gerar E-mail com IA**: assunto de até 6 palavras e corpo consultivo, editáveis.
- Cópia e download liberados apenas após o vendedor marcar a revisão humana.

### 🥊 Aba 3 – Simulador de Vendas & Objeções
- Chat (`st.chat_message`) com o Dr. Roberto Mendes, Diretor de Facilities cético da Nexus Corp (400 colaboradores),
  que achou a Taranis 35% mais cara.
- **Encerrar Simulação & Avaliar**: nota de 1 a 10, pontos fortes e pontos de melhoria (com foco em NR-17 e garantia).

### 📊 Aba 4 – Calculadora Consultiva de ROI & TCO Ergonômico
- Entradas: colaboradores, salário médio e taxa de queixas/atestados de coluna; modelo ErgoPro.
- Premissas editáveis (padrões): 5 dias parados por caso, custo de até 3x o salário diário (dias parados + reposição),
  redução de 40% no absenteísmo, cadeira comum de R$ 650 trocada a cada 18 meses.
- Saídas: custo anual de absenteísmo, investimento, economia anual, **payback (meses)**, **ROI em 5 anos** e gráfico
  Plotly do custo acumulado (Cadeira Comum vs. Linha ErgoPro).

---

## Como rodar localmente

Pré-requisito: **Python 3.10+** (testado em 3.10 e 3.14).

**Windows (cmd):**
```bat
git clone https://github.com/wellingtonb3/Taranis_Black.git
cd Taranis_Black
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

**Linux / macOS:**
```bash
git clone https://github.com/wellingtonb3/Taranis_Black.git
cd Taranis_Black
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

O app abre em `http://localhost:8501`.

### Ativando a IA (opcional: DeepSeek ou OpenAI)
Sem chave, tudo funciona no modo offline. Para usar um LLM, escolha **uma** opção:

1. Copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e preencha `DEEPSEEK_API_KEY`
   (ou `OPENAI_API_KEY`).
2. Ou defina a variável de ambiente antes de rodar:
   - Windows (cmd): `set DEEPSEEK_API_KEY=sk-...`
   - Linux/macOS: `export DEEPSEEK_API_KEY=sk-...`

Modelos padrão: `deepseek-chat` (altere com `DEEPSEEK_MODEL`) e `gpt-4o-mini` (altere com `OPENAI_MODEL`).
Se as duas chaves existirem, a DeepSeek tem prioridade. Na barra lateral é possível alternar entre a IA e o
modo offline. Se a API falhar, o app volta automaticamente ao modo offline.
O arquivo `secrets.toml` está no `.gitignore` e a chave nunca é exibida na interface.

### Testes
```bash
pip install pytest
python -m pytest -q
```

---

## Estrutura do projeto
```
app.py                     # Interface Streamlit (4 abas + barra lateral LGPD)
taranis/
  catalog.py               # Catálogo oficial, políticas comerciais e utilitários
  leads.py                 # Leitura da planilha, classificação das objeções e máscara LGPD
  email_engine.py          # Regras IF/ELSE e geração de e-mails (offline e LLM)
  simulator.py             # Persona Dr. Roberto Mendes, respostas e avaliação
  roi.py                   # Cálculo de ROI, payback e TCO
  llm.py                   # Cliente DeepSeek/OpenAI com fallback offline
  ui.py                    # CSS, ilustrações SVG e cards
data/02_Leads_B2B_Comercial.xlsx
docs/                      # Catálogo e índice do kit de dados do Challenge
tests/                     # Testes unitários e de interface (Streamlit AppTest)
```

## LGPD e supervisão humana
- Base de dados **sintética**, fornecida pelo Challenge.
- E-mails mascarados nas listagens; o contato completo só aparece por ação explícita do vendedor.
- Chaves de API lidas apenas de `secrets.toml` ou variáveis de ambiente, nunca exibidas.
- Todo conteúdo gerado é rascunho: cópia e download só são liberados após a revisão humana (Human-in-the-Loop).

## Premissas de negócio
- **Garantia Taranis de 5 anos** em todo o portfólio, adotada como proposta de melhoria da confiança do cliente
  (o catálogo original prevê prazos menores para alguns itens e componentes).
- Os demais dados (preços, especificações, prazos, frete e faturamento) seguem o catálogo oficial do kit.
- Os resultados da calculadora são estimativas consultivas e devem ser validados com o cliente.
