# LTM – Atualização de Configurações Railway e Supabase

- Data/Hora: 2025-11-04T10:33:20-03:00
- Responsável: Automação Trae

## Problemas Identificados

- Linhas de Supabase vazias em `railway_env_commands.txt` levando a divergência e confusão na configuração.
- Ausência de referência única e padronizada para configuração de variáveis do Railway em relação ao Supabase.
- Falha de execução do comando `generate` local por `OPENAI_API_KEY` inválido (placeholder), não relacionada ao Supabase.
- Componente “Authentication & Authorization” do Supabase reportado como UNHEALTHY no teste de verificação.

## Ações e Correções Aplicadas

- Removidas linhas vazias de Supabase em `railway_env_commands.txt` e adicionada nota explícita para utilizar exclusivamente `scripts/railway_env_bootstrap.ps1` para configurar variáveis do Supabase.
- Atualizado o cabeçalho de `railway_env_commands.txt` para reforçar a referência única ao script de bootstrap.
- Validação de sintaxe: arquivo permanece com comandos `railway variables set` válidos, sem entradas de Supabase vazias.
- Testes executados:
  - `python -m src.main generate --image_url ... --disable_replicate --stories` – falha por `OPENAI_API_KEY` inválido (erro 401), confirmando dependência de chave real para geração.
  - `python test_supabase_verification.py` – sucesso, gerou relatório com Status Geral BOM (13.5/18), porém com “Authentication & Authorization” UNHEALTHY.

## Impacto Esperado

- Maior consistência de configuração: Supabase gerenciado somente via `scripts/railway_env_bootstrap.ps1`.
- Redução de riscos de variáveis conflitantes entre arquivos de comando e script padrão.
- Diagnóstico claro para correções futuras em autenticação Supabase.

## Riscos e Dependências

- Risco: se `OPENAI_API_KEY` não for real em produção, comandos que dependem de geração de conteúdo falharão.
- Dependências: `accounts.json` (credenciais Supabase), Railway CLI instalado e autenticado, acesso à internet para testes HTTP.
- Risco: componente de autenticação Supabase UNHEALTHY indica possível problema de configuração de chaves/roles/endpoint.

## Próximos Passos Recomendados

- Garantir chaves reais em produção: `OPENAI_API_KEY`, `INSTAGRAM_ACCESS_TOKEN`, `TELEGRAM_BOT_TOKEN`.
- Revisar autenticação Supabase:
  - Validar `SUPABASE_SERVICE_KEY` e `SUPABASE_ANON_KEY` no projeto correspondente.
  - Checar políticas RLS e permissões de tabelas usadas pelo uploader/storage.
  - Confirmar que endpoints `/auth/v1` retornam status esperado.
- Utilizar exclusivamente `scripts/railway_env_bootstrap.ps1` para configurar variáveis no Railway, evitando edições manuais dispersas.

## Evidências

- Arquivo atualizado: `railway_env_commands.txt` sem linhas de Supabase vazias e com nota de referência única.
- Relatório gerado: `supabase_verification_report_20251104_103246.json` com pontuação e componentes detalhados.