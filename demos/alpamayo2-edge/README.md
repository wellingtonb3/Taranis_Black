# Simulador Alpamayo 2 Edge (demo educacional)

Demo web interativa inspirada no [NVIDIA Alpamayo 2 Edge](https://huggingface.co/nvidia/Alpamayo2-Edge), um modelo VLA (Vision-Language-Action) para direção autônoma.

**Não executa o modelo real.** O carro é guiado por um planejador simples baseado em regras; a demo reproduz o *formato* de entrada e saída do modelo:

- Entrada: 6 câmeras (22 quadros por inferência), 20 poses de histórico e instrução de navegação em texto.
- Saída: trajetória de 64 waypoints (6,4 s) e, quando necessário, raciocínio Chain-of-Causation com nota do AlpaJudge (simulado).

Recursos: eventos provocados (pedestre, corte de faixa, freada brusca, obra), clima, perfis de frota, modo de raciocínio adaptativo, perguntas livres e painel de dados analisados comparado aos 8 bilhões de pontos de dados por corrida citados pela Oracle Red Bull Racing.

## Como abrir

Arquivo único, sem dependências: abra `index.html` direto no navegador (duplo clique).
