# Entrega do TP — Opportunity Tracker

Verificação técnica realizada em 19/11/2026, referente ao commit e7ce307.

## Cinco links para o Moodle

| Item | Link |
| --- | --- |
| Sistema em produção | https://lumiis2.github.io/opportunity-tracker/ |
| Repositório | https://github.com/lumiis2/opportunity-tracker |
| Build de testes e cobertura aprovado | https://github.com/lumiis2/opportunity-tracker/actions/runs/44594320839 |
| Relatório Codecov do commit verificado | https://app.codecov.io/gh/lumiis2/opportunity-tracker/commit/e7ce30792ca817f3cf5253207fa97267a112a3b2 |
| Vídeo no YouTube | PREENCHER após gravação e publicação |

Evidência adicional dos e2e nos três sistemas:
https://github.com/lumiis2/opportunity-tracker/actions/runs/44594320642

Depois de enviar novos commits, confira as novas execuções verdes e atualize o
link do build e o relatório de cobertura para o commit final da entrega.

## Evidências verificadas

- 54 funções unitárias em tests/unit, com 96 casos por parametrização.
- 5 e2e aprovados nos jobs Linux, macOS e Windows.
- Workflow Python/cobertura aprovado nos mesmos três sistemas.
- Suíte Python completa: 129 casos aprovados.
- Codecov: 92,98% de cobertura de linhas Python, 729/784 linhas, acima dos 80%.
- Produção carregando 173 oportunidades, 292 eventos e os sete calendários.
- Histórico com 213 commits, acima dos 50 exigidos.

Os números descrevem a revisão do commit e7ce307 em 19/11/2026; os dados do site
e o histórico podem crescer. A cobertura considera src e scripts, conforme a
configuração do projeto.

## Pendências de autoria e publicação

- Preencher os nomes completos dos dois integrantes nos READMEs.
- Revisar o relato de uso de IA para refletir as consultas efetivamente realizadas.
- Gravar e publicar o vídeo no YouTube, com duração máxima de cinco minutos.
- Inserir a URL do vídeo na tabela e entregar os cinco links no Moodle.

## Roteiro técnico sugerido para um vídeo de cerca de 4 minutos e 30 segundos

| Tempo | Demonstração |
| --- | --- |
| 0:00–0:30 | Apresentar os integrantes e o objetivo do Opportunity Tracker. |
| 0:30–1:10 | Mostrar o site publicado, categorias, próximos prazos e acesso a ICS/CSV. |
| 1:10–1:45 | Explicar o fluxo CSV → Python → ICS/JSON → HTML/CSS/JavaScript no GitHub Pages. |
| 1:45–2:10 | Relatar consultas ao Codex para requisitos, cenários, exemplos de testes e investigação do CI. |
| 2:10–3:00 | Mostrar um teste unitário, a pasta tests/unit e a execução dos unitários. |
| 3:00–3:40 | Mostrar um e2e e a execução no navegador com --headed. |
| 3:40–4:15 | Mostrar os workflows verdes nos três sistemas e o Codecov com cobertura acima de 80%. |
| 4:15–4:30 | Mostrar onde estão as instruções e os links de entrega. |

Prepare as páginas e o terminal antes de gravar. Se a execução ao vivo demorar,
mostre a saída concluída, identificando que se trata de uma execução anterior.
