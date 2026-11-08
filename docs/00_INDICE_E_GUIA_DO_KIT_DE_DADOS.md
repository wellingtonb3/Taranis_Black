# 📦 KIT DE DADOS SIMULADOS (MOCK DATA KIT) — TARANIS BLACK
**ONE AI for Business | G11**

Este diretório contém todos os insumos, planilhas e documentos sintéticos preparados para que os alunos executem o challenge sem precisar criar dados do zero.

---

## 🗂️ Mapeamento de Arquivos por Rota de Especialização

| Arquivo | Formatos Disponíveis | Para qual Rota? | O que contém & Como o aluno deve usar |
|---|---|---|---|
| **`01_Catalogo_Produtos_e_Precos_Taranis_Black`** | `.docx` e `.pdf` | **Todas as Rotas** (Especialmente Vendas e Marketing) | Catálogo com fichas técnicas detalhadas das linhas *ErgoPro* (cadeiras), *SmartDesk* (mesas elevatórias), *Silence* (cabines acústicas) e periféricos. Contém especificações de NR-17, prazos, políticas de frete CIF/FOB e garantias de 5 anos. |
| **`02_Leads_B2B_Comercial`** | `.xlsx` | **Rota 1 (Vendas e Comercial)** | **Aba 1:** 20 empresas B2B qualificadas no CRM da Taranis Black, com dores registradas, personas de decisores (RH, Facilities, Compras) e as objeções reais travando cada negócio.<br>**Aba 2:** Matriz com as 5 principais objeções mapeadas e contornos com foco em valor e IA. |
| **`03_Marketing_Artigo_Semente_e_Guia_Tom_de_Voz`** | `.docx` e `.pdf` | **Rota 2 (Marketing e Conteúdo)** | **Parte 1 (Artigo-Semente):** Estudo técnico e aprofundado sobre o impacto da ergonomia ativa e NR-17 no combate ao absenteísmo e aumento de produtividade.<br>**Parte 2 (Brand Voice):** Os 4 pilares de tom de voz da Taranis Black (Científico, Empático, Sofisticado, Descomplicado), matriz "Como falamos vs. Como NÃO falamos" e diretrizes para LinkedIn, Instagram e E-mail. |
| **`04_Base_Colaboradores_People_Analytics`** | `.xlsx` | **Rota 3 (RH e People Analytics)** | **Aba 1:** Base sintética completa com os 280 colaboradores da Taranis Black (departamento, cargo, salário, absenteísmo anual, eNPS, status ativo/desligado e feedbacks reais de saída).<br>**Aba 2:** Amostra qualitativa de pesquisa de clima com comentários abertos para análise de sentimento com IA.<br>**Aba 3:** KPIs consolidados de turnover (22,5% geral, 24% em <90 dias, áreas críticas). |
| **`05_Financas_Orcado_vs_Realizado`** | `.xlsx` | **Rota 4 (Finanças e Operações)** | **Aba 1 (DRE Trimestral):** Demonstrativo de resultado em 4 trimestres comparando Orçado vs. Realizado (revelando estouro de custos em fretes de emergência e inadimplência no T3/T4).<br>**Aba 2:** Receita e margem bruta por linha de produto.<br>**Aba 3:** Métricas de dor e custos de retrabalho com sistemas legados (R$ 960k em fretes extras e 5 dias de atraso no fechamento). |
| **`06_Descritivo_Processo_Operacional_SIPOC`** | `.docx` e `.pdf` | **Rota 4 (Finanças e Operações)** | Mapeamento narrativo do fluxo atual ("As-Is") de aprovação de crédito, faturamento e expedição em 5 passos manuais.<br>Inclui matriz estruturada de fornecedores, entradas, processo, saídas e clientes (SIPOC) e evidências categorizadas nos 6M para o Diagrama de Ishikawa. |

---

## 🎯 Recomendações de Uso para os Alunos

1. **Rota 1 (Vendas):** Importe os dados da planilha `02_Leads_B2B_Comercial.xlsx` no ChatGPT para treinar o contorno das 5 objeções de clientes com argumentos baseados em dados reais do catálogo `01_Catalogo_Produtos_e_Precos_Taranis_Black`.
2. **Rota 2 (Marketing):** Cole o texto da Parte 1 do arquivo `03_Marketing_Artigo_Semente...` nas instruções do seu Gem ou Custom GPT junto com as diretrizes de tom de voz da Parte 2 para testar a transformação automática em posts de LinkedIn, carrosséis de Instagram e e-mails corporativos.
3. **Rota 3 (RH):** Faça o upload da planilha `04_Base_Colaboradores...` no ChatGPT (Code Interpreter / Análise de Dados) para calcular correlações de turnover e cruzar com a análise de sentimento dos comentários da pesquisa de clima.
4. **Rota 4 (Finanças):** Use o documento `06_Descritivo_Processo_Operacional_SIPOC` para montar o fluxo Lean e a Espinha de Peixe; e suba a planilha `05_Financas_Orcado_vs_Realizado.xlsx` no Claude para gerar dashboards dinâmicos (Live Artifacts) e projeções preditivas.
