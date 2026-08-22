# Como criar seu calendário pessoal de oportunidades

Você pode usar o Opportunity Tracker para transformar uma planilha pessoal em
um calendário `.ics`, compatível com Google Calendar, Apple Calendar e Outlook.

## 1. Crie a planilha

Crie uma aba no Google Sheets com estes cabeçalhos, preservando a grafia:

```text
Programa
Categoria
Nível
Instituição / organização
Área / foco
Local
Formato
Duração
Applications open
Deadline
Período / data do programa
Elegível?
Requisitos / elegibilidade relevantes
Funding / benefícios
Seleção / docs relevantes
Prioridade
Status / observações
Link
Já apliquei?
```

Datas exatas podem usar `AAAA-MM-DD` ou `DD/MM/AAAA`. Use `N/A` quando não
houver uma data. O período do programa também aceita intervalos, como
`10/06/2027 a 30/08/2027`, e períodos aproximados como `Winter 2027`,
`Spring 2027`, `Summer 2027` e `Fall 2027`.

Períodos sazonais viram marcadores estimados em janeiro, março, junho ou
setembro. Quando a organização divulgar uma data exata, substitua a estimativa.

## 2. Exporte a aba como CSV

No Google Sheets, selecione **Arquivo → Fazer download → Valores separados por
vírgulas (.csv)** e salve o arquivo como `personal.csv`.

## 3. Gere o calendário localmente

```bash
git clone https://github.com/lumiis2/opportunity-tracker.git
cd opportunity-tracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m src.cli generate-ics \
  --track personal \
  --input personal.csv \
  --output meu-calendario.ics \
  --calendar-name "Minhas oportunidades"
```

Importe `meu-calendario.ics` no aplicativo de calendário. Essa importação é uma
cópia pontual: gere e importe novamente quando sua planilha mudar.

## 4. Publique um link atualizável (opcional)

Faça um fork deste repositório, coloque seu CSV em `data/personal.csv` e ajuste
em `config.yaml` o `sheet_id` e o `gid` da sua aba. O `gid` é o número exibido
na URL depois de `gid=`.

Para que a automação consiga baixar a planilha sem credenciais, compartilhe-a
como **qualquer pessoa com o link pode visualizar**. Ative o GitHub Pages com
GitHub Actions no fork. O workflow atualizará e publicará:

```text
https://SEU-USUARIO.github.io/opportunity-tracker/personal.ics
```

Assine essa URL no aplicativo de calendário para receber futuras atualizações.
Evite colocar dados sensíveis na planilha: CSV e ICS publicados ficam públicos.
