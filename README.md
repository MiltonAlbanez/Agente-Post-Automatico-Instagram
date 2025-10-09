# Agente de Post Automático Instagram

Este projeto replica o fluxo descrito no N8N para coletar tendências do Instagram, gerar conteúdo com IA e publicar automaticamente. Nesta primeira versão, está implementada a Etapa 1: Coleta e Filtragem de Conteúdo.

## Estrutura

- `src/main.py`: CLI para executar o pipeline.
- `src/config.py`: Carregamento de variáveis de ambiente.
- `src/services/rapidapi_client.py`: Cliente para buscar tendências por hashtag.
- `src/services/db.py`: Camada de banco (PostgreSQL) para armazenar tendências.
- `src/pipeline/collect.py`: Lógica de coleta, filtragem e inserção no banco.

## Requisitos

- Python 3.10+
- Dependências em `requirements.txt`:
  - requests
  - python-dotenv
  - psycopg2-binary

Instalação:

```
pip install -r requirements.txt
```

## Configuração

Crie um arquivo `.env` na raiz com as variáveis:

```
INSTAGRAM_BUSINESS_ACCOUNT_ID=
TELEGRAM_CHAT_ID=
RAPIDAPI_KEY=
REPLICATE_TOKEN=
POSTGRES_DSN=postgresql://usuario:senha@host:porta/banco
OPENAI_API_KEY=

# Supabase Storage (opcional para fallback de hospedagem de imagem)
SUPABASE_URL=https://SEU_REF.supabase.co
SUPABASE_SERVICE_KEY=chave_service_role
SUPABASE_BUCKET=nome_do_bucket
```

Observação: Nesta etapa, são usadas `RAPIDAPI_KEY` e `POSTGRES_DSN`.

## Uso

Executar coleta de tendências por hashtags (ex.: `blender3d` e `isometric`):

```
python src/main.py collect --hashtags blender3d,isometric
```

Isso irá:
- Buscar posts top por hashtag na RapidAPI.
- Filtrar apenas imagens (não vídeos).
- Inserir itens novos na tabela `top_trends` (evitando duplicatas).

### Múltiplas Contas (multirun)

Crie um arquivo `accounts.json` com a configuração das contas:

```
[
  {
    "nome": "advogado_conta",
    "instagram_id": "<ID_INSTAGRAM>",
    "telegram_chat_id": "<CHAT_ID>",
    "hashtags_pesquisa": ["direito_digital", "advocacia_moderna"],
    "prompt_ia_geracao_conteudo": "Crie um post sobre tendências em direito digital...",
    "prompt_ia_legenda": "Resuma o conteúdo sobre direito digital em uma legenda com {descricao}",
    
    // Opcional: overrides de credenciais por conta
    "openai_api_key": "<OPENAI_API_KEY>",
    "replicate_token": "<REPLICATE_TOKEN>",
    "instagram_access_token": "<INSTAGRAM_ACCESS_TOKEN>",
    
    // Opcional: Supabase por conta (fallback robusto)
    "supabase_url": "https://SEU_REF.supabase.co",
    "supabase_service_key": "<SERVICE_ROLE_KEY>",
    "supabase_bucket": "nome_do_bucket"
  }
]
```

Execute o fluxo para todas as contas:

```
python src/main.py multirun --limit 1
```

Para cada conta:
- Coleta por hashtags definidas.
- Gera imagem e legenda com IA, usando prompts personalizados quando presentes.
- Publica no Instagram e envia notificação pelo Telegram.

## Banco de Dados

O projeto usa PostgreSQL via DSN. A tabela `top_trends` é criada automaticamente se não existir:

Campos:
- `prompt` (texto da legenda)
- `thumbnail_url`
- `code` (código único do post)
- `tag` (nome da hashtag)
- `isposted` (booleano)
- `created_at` (timestamp)

## Etapa 2 e 3: Geração e Publicação

- Geração de descrição e legenda com OpenAI (modelo `gpt-4o-mini`).
- Geração de imagem com Replicate (`black-forest-labs/flux-schnell`).
- Preparação e publicação no Instagram via Graph API.
- Notificação no Telegram após publicar.

Variáveis adicionais no `.env`:

```
OPENAI_API_KEY=
INSTAGRAM_ACCESS_TOKEN=
TELEGRAM_BOT_TOKEN=
```

Executar geração e publicação (entrada: URL de imagem):

```
python src/main.py generate --image_url https://exemplo/imagem.jpg --style "isometric, 3D, blender"
```

Listar itens não postados no banco:

```
python src/main.py unposted --limit 10
```

### Agendamento

Windows: use o Agendador de Tarefas para executar `python src/main.py collect --hashtags blender3d,isometric` nos horários desejados.

Linux: via `cron`, exemplo `5 13,19 * * *`.
### Fallback robusto de hospedagem de imagem (Supabase)

Se você ativar as variáveis `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` e `SUPABASE_BUCKET`,
o pipeline tentará re-hospedar a imagem original no Supabase Storage quando a geração do
Replicate falhar. O objeto será salvo em `/{bucket}/{arquivo}` e a URL pública retornada
seguirá o padrão `https://SEU_REF.supabase.co/storage/v1/object/public/{bucket}/{arquivo}`.

Requisitos:
- Bucket com acesso público para leitura, ou CDN habilitada.
- Chave `service_role` para upload via API.

Caso não esteja configurado, o fallback usa hosts públicos anônimos (0x0.st, transfer.sh, catbox.moe).