# Agente Post Automático Instagram

Automatiza coleta de tendências, geração de imagens conceituais e publicação no Instagram, com coerência entre imagem e legenda.

## 🚀 Como Usar

### Instalação
```bash
pip install -r requirements.txt
```

### Executar o Dashboard Principal
```bash
streamlit run dashboard/dashboard_server.py
```

### Comandos Principais

1. **🚀 Modo Standalone (Recomendado)**:
   ```bash
   # Geração independente com tema específico
   python src/main.py standalone --theme motivacional --disable_replicate
   
   # Com prompt personalizado
   python src/main.py standalone --content_prompt "Crie uma mensagem sobre liderança" --style profissional
   
   # Para stories
   python src/main.py standalone --theme produtividade --stories
   ```

2. **Coleta de dados** (Opcional - requer RapidAPI):
   ```bash
   python src/main.py collect --hashtag motivacao --limit 10
   ```

3. **Geração e publicação** (Modo tradicional):
   ```bash
   python src/main.py generate --account miltonalcantara --style "motivacional, inspirador"
   ```

### Sistema de Automação

#### Executar Automação Completa
```bash
python run_automation.py start
```

#### Dashboard de Automação
```bash
python run_automation.py dashboard
```

### 🔧 Auto-Inicialização dos Dashboards (Windows)

Para resolver o problema de portas inativas (5000 e 8502) após reinicialização do computador:

#### Configurar Auto-Inicialização
```powershell
# Configurar para iniciar automaticamente no boot
.\scripts\setup_auto_start.ps1 -Install

# Verificar status da configuração
.\scripts\setup_auto_start.ps1 -Status

# Remover auto-inicialização
.\scripts\setup_auto_start.ps1 -Uninstall
```

#### Inicialização Manual Rápida
```batch
# Executar arquivo .bat para iniciar dashboards imediatamente
.\start_dashboards.bat
```

#### Dashboards Disponíveis
- **Dashboard A/B Testing**: http://localhost:5000
- **Dashboard de Automação**: http://localhost:8502

> **Nota**: A auto-inicialização resolve o problema de configurações perdidas após desligar o computador, garantindo que os dashboards estejam sempre disponíveis.

#### Executar Ciclo Manual
```bash
python run_automation.py manual
```

#### Ver Configurações
```bash
python run_automation.py config
```

#### Ver Status do Sistema
```bash
python run_automation.py status
```

### Gerar Post Automaticamente
```python
from core.post_generator import PostGenerator

generator = PostGenerator()
post = generator.generate_post()
print(post)
```

## 🚀 Modo Standalone - Geração Independente

O **Modo Standalone** é a nova funcionalidade principal que permite gerar e publicar conteúdo de alta qualidade **sem depender de APIs externas** como RapidAPI.

### ✨ Benefícios do Modo Standalone

- **🔒 Totalmente Independente**: Não requer RapidAPI ou outras APIs externas
- **🎨 Conteúdo 100% Original**: Geração personalizada com OpenAI
- **⚡ Sem Limitações**: Não há rate limits de APIs externas
- **🖼️ Imagens de Qualidade**: Usa Unsplash ou Replicate para imagens
- **🎯 Sistema Temático**: Temas pré-configurados (motivacional, produtividade, liderança, etc.)
- **⚙️ Configuração por Conta**: Suporte a múltiplas contas Instagram

### 🎨 Temas Disponíveis

- **motivacional**: Mensagens inspiradoras sobre superação e crescimento
- **produtividade**: Dicas práticas sobre organização e gestão de tempo
- **lideranca**: Insights sobre liderança e desenvolvimento profissional
- **mindset**: Conceitos de mindset de crescimento e mentalidade positiva
- **negocios**: Estratégias sobre empreendedorismo e inovação

### 📋 Exemplos de Uso

```bash
# Publicação motivacional básica
python src/main.py standalone --theme motivacional

# Com conta específica
python src/main.py standalone --account miltonalcantara --theme lideranca

# Com prompt personalizado
python src/main.py standalone --content_prompt "Fale sobre a importância da persistência" --style inspirador

# Para stories
python src/main.py standalone --theme produtividade --stories

# Sem usar Replicate (mais rápido)
python src/main.py standalone --theme mindset --disable_replicate
```

## 🤖 Sistema de Automação

O sistema de automação implementa os **Próximos Passos Recomendados**:

### 1. 📊 Monitoramento
- **Engagement Tracker**: Monitora curtidas, comentários, salvamentos e alcance
- **Análise de Tendências**: Identifica padrões de performance
- **Alertas Automáticos**: Notifica sobre mudanças significativas

### 2. 🔄 Expansão de Conceitos
- **Conceitos Superiores**: Sistema expandido com 50+ conceitos visuais
- **Categorização Avançada**: Organização por temas e estilos
- **Adaptação Dinâmica**: Novos conceitos baseados em performance

### 3. ⚡ Otimização Automática
- **Performance Optimizer**: Ajusta conceitos baseado em dados reais
- **Machine Learning**: Aprende com histórico de engagement
- **A/B Testing**: Testa variações automaticamente

### 4. 🎯 Automação Consistente
- **Agendamento Inteligente**: Posts automáticos em horários otimizados
- **Controle de Qualidade**: Validação automática antes da publicação
- **Consistência de Marca**: Mantém tom de voz e estilo visual

## 📈 Funcionalidades de Automação

### Agendamento
- ⏰ **Posts Automáticos**: 3 posts diários em horários otimizados
- 🔄 **Otimização Noturna**: Análise e ajustes automáticos às 23h
- 📊 **Monitoramento Contínuo**: Coleta de dados a cada hora

### Qualidade
- ✅ **Validação Automática**: Verifica qualidade antes da publicação
- 🎨 **Consistência Visual**: Mantém padrões de design
- 📝 **Otimização de Texto**: Ajusta legendas e hashtags

### Monitoramento
- 📈 **Métricas em Tempo Real**: Acompanha performance dos posts
- 🎯 **Identificação de Tendências**: Detecta conceitos em alta
- 🚨 **Alertas Inteligentes**: Notifica sobre oportunidades

### Dashboard
- 📊 **Visão Geral**: Métricas principais e status do sistema
- ⚙️ **Configurações**: Controle completo dos parâmetros
- 📈 **Análise de Performance**: Gráficos e relatórios detalhados
- 🔄 **Controle de Consistência**: Monitoramento de qualidade

## Comandos rápidos (Railway — Windows)
- Listar não postados: `railway run python src/main.py unposted --limit 10`
- Publicar primeiro não postado: `railway run python src/main.py autopost --no-replicate --style "isometric, minimalista"`
  - Com Supabase overrides via CLI: `railway run python src/main.py autopost --tags coaching --supabase_url https://SEU_REF.supabase.co --supabase_service_key service_role_key --supabase_bucket instagram-images`
  - Com prompt visual do Replicate: `railway run python src/main.py autopost --replicate_prompt "paisagem serena ou animal fofinho em cenário natural, minimalista, sem pessoas, cores suaves, composição limpa"`
- Coletar por usuários: `railway run python src/main.py collect_users --users milton_albanez`
- Gerar a partir de URL: `railway run python src/main.py generate --image_url <url> --style "isometric, minimalista"`
- Limpar cache RapidAPI: `railway run python src/main.py clear_cache --older 3600`

## Comandos rápidos (Railway — Linux/macOS)
- Listar não postados: `railway run python src/main.py unposted --limit 10`
- Publicar primeiro não postado: `railway run python src/main.py autopost --no-replicate --style "isometric, minimalista"`
  - Com Supabase overrides via CLI: `railway run python src/main.py autopost --tags coaching --supabase_url https://SEU_REF.supabase.co --supabase_service_key service_role_key --supabase_bucket instagram-images`
  - Com prompt visual do Replicate: `railway run python src/main.py autopost --replicate_prompt "paisagem serena ou animal fofinho em cenário natural, minimalista, sem pessoas, cores suaves, composição limpa"`
- Coletar por usuários: `railway run python src/main.py collect_users --users milton_albanez`
- Gerar a partir de URL: `railway run python src/main.py generate --image_url <url> --style "isometric, minimalista"`
- Limpar cache RapidAPI: `railway run python src/main.py clear_cache --older 3600`

## Variáveis úteis (Railway)
- Obrigatórias: `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `INSTAGRAM_ACCESS_TOKEN`, `OPENAI_API_KEY`, `POSTGRES_DSN` (ou `DATABASE_URL`)
- Opcionais: `RAPIDAPI_KEY`, `RAPIDAPI_HOST`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_BUCKET`, `ACCOUNT_NAME`, `LIMIT`, `STYLE`, `REPLICATE_PROMPT`
- Fallback de RapidAPI (opcional): `RAPIDAPI_ALT_HOSTS` com uma lista separada por vírgulas de hosts alternativos a tentar caso o host principal falhe (ex.: `instagram-scraper-api2.p.rapidapi.com,instagram-scraper.p.rapidapi.com`).

**⚠️ Importante**: O sistema agora funciona completamente sem RapidAPI usando o **Modo Standalone**
- Definir via CLI sem deploy:
  `railway variables --set "INSTAGRAM_BUSINESS_ACCOUNT_ID=<id>" --set "INSTAGRAM_ACCESS_TOKEN=<token>" --set "OPENAI_API_KEY=<key>" --set "RAPIDAPI_KEY=<key>" --set "RAPIDAPI_HOST=instagram-scraper-api2.p.rapidapi.com" --set "POSTGRES_DSN=<dsn>" --set "ACCOUNT_NAME=Milton_Albanez" --set "LIMIT=1" --set "STYLE=isometric, minimalista" --skip-deploys`

## Requisitos
- Python 3.11+
- Conta do Instagram (Graph API): `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `INSTAGRAM_ACCESS_TOKEN`
- RapidAPI (Instagram Scraper): `RAPIDAPI_KEY`, `RAPIDAPI_HOST`
- OpenAI: `OPENAI_API_KEY`
- Replicate: `REPLICATE_TOKEN`
- PostgreSQL: `POSTGRES_DSN`
  - No Railway, pode usar `DATABASE_URL` (fallback automático)
- Supabase Storage (opcional p/ re-hospedar): `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_BUCKET`

## Instalação Local
1. Crie e ative venv
   - Windows: `python -m venv .venv && .venv\Scripts\activate`
2. Instale deps: `pip install -r requirements.txt`
3. Configure `.env` com as variáveis (veja Requisitos)
4. Execute um teste: `python src/main.py multirun --limit 1 --only Milton_Albanez`

### Exemplo de `.env`
```
# Instagram Graph API
INSTAGRAM_BUSINESS_ACCOUNT_ID=xxxxxxxxxxxxxxxx
INSTAGRAM_ACCESS_TOKEN=EAAB...long_token

# Telegram (opcional)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789

# RapidAPI
RAPIDAPI_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
RAPIDAPI_HOST=instagram-scraper-api2.p.rapidapi.com
RAPIDAPI_ALT_HOSTS=instagram-scraper.p.rapidapi.com,instagram-scraper-api.p.rapidapi.com

# OpenAI e Replicate
OPENAI_API_KEY=sk-xxxxx
REPLICATE_TOKEN=r8_xxxxx
REPLICATE_PROMPT=paisagem serena ou animal fofinho em cenário natural, minimalista

# Banco de Dados
POSTGRES_DSN=postgresql://usuario:senha@host:5432/dbname
# Railway fallback automático
# DATABASE_URL=postgresql://usuario:senha@host:5432/dbname

# Supabase Storage (opcional)
SUPABASE_URL=https://SEU_REF.supabase.co
SUPABASE_SERVICE_KEY=service_role_key
SUPABASE_BUCKET=instagram-images
```

## Estrutura
 - `accounts.json`: define contas, hashtags/usernames, prompts e flags.
   - `prompt_ia_replicate`: prompt visual do Replicate, usado como fallback quando `--replicate_prompt` não é informado.

## Deploy no Railway (Compose v3)
- Este projeto inclui `railway.json` com `version: 3` e um serviço `Autopost Worker`.
- Os Cron Runs estão definidos dentro de `services.app.cron` e são executados em UTC:
  - `morning_preseed`: 08:55 UTC (prepara o banco antes do post da manhã)
  - `midday_preseed`: 14:55 UTC
  - `evening_preseed`: 21:55 UTC
  - `morning_post`: 09:00 UTC (≈ 06:00 BRT)
  - `midday_post`: 15:00 UTC (≈ 12:00 BRT)
  - `evening_post`: 22:00 UTC (≈ 19:00 BRT)
- O comando padrão do serviço (`startCommand`) mantém o container ativo apenas para fins de implantação; os jobs são disparados via Cron.

### Dicas
- Variáveis que podem ser usadas nos comandos:
  - `ACCOUNT_NAME`: nome de uma conta do `accounts.json` (default: `Milton_Albanez`)
  - `LIMIT`: limite de itens a processar (default: `1`)
  - `STYLE`: estilo opcional para `autopost`
- Railway utiliza UTC nos Cron Runs; ajuste horários conforme seu fuso.
- Caso prefira configurar via Dashboard, espelhe os mesmos comandos e horários.
- `src/services/*`: clientes (Instagram, Replicate, RapidAPI, Supabase, OpenAI).
- `src/pipeline/*`: fluxo de coleta e geração/publicação.
- `src/main.py`: CLI com comandos `collect`, `collect_users`, `generate`, `multirun`, `clear_cache`.

## Agendamento Local (Windows)
- Use `scripts/run_multirun.ps1` ou `scripts/run_autopost.ps1` com o Agendador de Tarefas do Windows; PC precisa estar ligado (sem hibernação).
- Horários (BRT): 06:00, 12:00, 19:00.
- Exemplo de ação:
  - Programa: `powershell.exe`
  - Argumentos: `-ExecutionPolicy Bypass -File "C:\caminho\para\scripts\run_autopost.ps1" -Style "portrait, natural light"`
  - Iniciar em: `C:\caminho\para\o\projeto`

## Deploy no Railway
1. Link ao projeto: `railway link -p <PROJECT_ID>`
2. Configure Variables com os segredos dos Requisitos.
   - Banco: defina `POSTGRES_DSN` ou use `DATABASE_URL` do add-on PostgreSQL
3. Faça deploy: `railway up`
4. Procfile já define `worker: python src/main.py multirun --limit 1 --only Milton_Albanez`.
5. Cron Job (UTC): 
   - Command: `python src/main.py multirun --limit 1 --only Milton_Albanez`
   - Ajuste horário conforme sua timezone (ex.: 09:00 UTC ≈ 06:00 BRT).

### Agendamento de Postagens Automáticas
- Timezone: BRT (UTC-3). Horários desejados: 06:00, 12:00 e 19:00.
- Equivalência em UTC: 09:00, 15:00 e 22:00 UTC.
- Crie três Cron Jobs no Railway com o comando abaixo:
  - Command: `python src/main.py autopost --no-replicate`
  - Horários (UTC): `09:00`, `15:00`, `22:00`
- Opcional: defina `STYLE` (fotográfico) via Variables para orientar legenda/descrição, por exemplo:
  - `STYLE=isometric, minimalista`
  - `REPLICATE_PROMPT=paisagem serena ou animal fofinho em cenário natural, minimalista`
- Dica (multicontas): se usar `multirun`, mantenha `"disable_replicate": true` em `accounts.json` e agende `multirun` nos mesmos horários.

## Dicas e Observações
- RapidAPI pode retornar 429; ajuste limite/horários e diversifique hashtags.
- Tokens do Instagram expiram; mantenha renovação.
- Logs: veja `logs/` localmente ou o dashboard do Railway.
- `accounts.json` não deve conter segredos; Supabase usa fallback de variáveis de ambiente.

## Comandos úteis
- Coleta por hashtags: `python src/main.py collect --hashtags empreendedorismo,pnl`
- Coleta por usuários: `python src/main.py collect_users --users milton_albanez`
- Gerar a partir de URL: `python src/main.py generate --image_url <url>`
 - Limpar cache RapidAPI: `python src/main.py clear_cache --older 3600`
  - Listar não postados (Railway): `railway run python src/main.py unposted --limit 10`
  - Publicar primeiro não postado (Railway): `railway run python src/main.py autopost --no-replicate --style "isometric, minimalista"`
  - Publicar com imagem gerada (Replicate): `railway run python src/main.py autopost --replicate_prompt "paisagem serena ou animal fofinho em cenário natural, minimalista"`
  - Listar não postados (Railway - Windows): `railway run python src/main.py unposted --limit 10`
  - Publicar primeiro não postado (Railway - Windows): `railway run python src/main.py autopost --no-replicate --style "isometric, minimalista"`
  - Dica: defina variáveis úteis via CLI (sem disparar deploy):
    `railway variables --set "ACCOUNT_NAME=Milton_Albanez" --set "LIMIT=1" --set "STYLE=isometric, minimalista" --skip-deploys`

## Licença
Uso pessoal do autor. Ajuste conforme seu contexto.
**Deploy no Railway**
- Pré-requisitos: conta no Railway e acesso ao projeto deste repositório.
- Manifesto Railway: use apenas UM formato (YAML ou JSON).
  - `railway.yaml` (já incluso) ou `railway.json` (espelho em JSON).
  - Não mantenha os dois ativos simultaneamente para evitar conflitos de interpretação.
  - Ambos definem o serviço “Autopost Worker” e os três jobs diários (09:00, 15:00, 22:00 UTC) com `preseed` 5 minutos antes.
- Variáveis obrigatórias do serviço:
  - `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_BUSINESS_ACCOUNT_ID`
  - `OPENAI_API_KEY`, `RAPIDAPI_KEY`, `RAPIDAPI_HOST`
  - `POSTGRES_DSN` com itens não postados disponíveis
  - Opcional: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_BUCKET`
  - Opcional: `ACCOUNT_NAME` para escolher os prompts da conta (ex.: `Milton_Albanez`).
- Como criar pelo painel:
  - Crie um serviço novo apontando para este repo e faça o deploy.
  - Em “Variables”, adicione as chaves acima com seus valores.
  - Em “Scheduled Jobs”, confirme que apareceram:
    - `morning_post` diário às `09:00` UTC: `python src/main.py autopost --no-replicate --style "street, candid, natural light"`
    - `midday_post` diário às `15:00` UTC: `python src/main.py autopost --no-replicate --style "portrait, studio-like natural light"`
    - `evening_post` diário às `22:00` UTC: `python src/main.py autopost --no-replicate --style "evening golden hour, city scenes"`
  - E os preseed 5 minutos antes de cada horário (`08:55`, `14:55`, `21:55` UTC).
- Como criar via CLI (opcional):
  - `railway login`
  - `railway link` na pasta do projeto
  - `railway up` para build/deploy
  - `railway variables set KEY=VALUE` para definir variáveis.
  - Exemplo de fallback de RapidAPI sem mudar o host primário:
    - `railway variables set RAPIDAPI_ALT_HOSTS="instagram-scraper-api2.p.rapidapi.com,instagram-scraper.p.rapidapi.com"`
- Testar antes do horário:
  - Execute manualmente: `railway run python src/main.py autopost --no-replicate --style "street, candid, natural light"`
  - Verifique logs: `railway logs` e se o item foi marcado como postado no DB.
- Observações de horário:
  - Horários do manifest estão em UTC: 09:00 (06:00 BRT), 15:00 (12:00 BRT), 22:00 (19:00 BRT).
  - Ajuste os `schedule` em `railway.yaml` se quiser outro fuso.
- Estilos e fluxo:
  - Cada job usa `--style` próprio; se omitir, o código aceita `STYLE` como fallback.
  - Fluxo mantém fotos reais (`--no-replicate`), descrição da imagem por IA e legenda gerada com seus prompts de conta usando `{descricao}` e `{texto_original}`.