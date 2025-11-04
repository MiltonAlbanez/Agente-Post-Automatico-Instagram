# Postgres: "invalid length of startup packet" — Análise e Mitigação

Este erro aparece nos logs do PostgreSQL quando **um cliente conecta na porta do banco** e envia **um protocolo que não é PostgreSQL** (por exemplo, um health check HTTP, port scan ou outro serviço tentando abrir TCP sem falar o protocolo correto).

## Situação atual
- O serviço começa com `python railway_scheduler.py` e o healthcheck HTTP está em `/health` (via `health_server.py`).
- O código não faz health check na porta do Postgres; usa `psycopg` com DSN PostgreSQL quando necessário.
- O log contínuo de `invalid length of startup packet` aponta para **tráfego externo** chegando à porta pública do banco (ex.: scanner, balanceador, ou healthcheck incorreto do próprio DB).

## Impacto
- É **ruído de log** e **não indica falha** na aplicação.
- Não impede conexões válidas via `psycopg`.

## Causas comuns
- Health check configurado para a porta do Postgres usando HTTP.
- Porta pública do Postgres exposta e recebendo conexões indevidas.
- Ferramentas de monitoramento externos que checam a porta com protocolos genéricos.

## Ações recomendadas no Railway
1. Verifique o serviço do Postgres:
   - Em Networking, **desative Public connections** se não houver necessidade de acesso externo.
   - Se precisar manter público, **restrinja IPs** ou troque o endpoint público por credenciais internas.
   - Confirme que **não há healthcheck HTTP** apontando para a porta do Postgres.
2. App (este serviço): mantenha o Start command como `python railway_scheduler.py`.
3. Teste de banco pontual (sem alterar Start command): use “Run Command” no Railway:
   - `python test_db_connection.py`
   - `python scripts/quick_verify_dest.py`
4. Variáveis de ambiente:
   - Se usar Postgres de provedores que exigem TLS (Supabase, etc.), defina `FORCE_SSLMODE_REQUIRE=true`.
   - Garanta que `DATABASE_URL` esteja no formato `postgresql://user:pass@host:port/db`.

## O que o código já faz para prevenir erros
- `src/services/db.py` valida o DSN, força `sslmode=require` quando necessário e define `connect_timeout=10`.
- O health server só checa endpoints HTTP externos conhecidos e **não toca a porta do banco**.

## Como confirmar que está tudo ok
- Execute `python test_db_connection.py` → deve retornar versão do PostgreSQL.
- Execute `python scripts/quick_verify_dest.py` → cria tabela `top_trends` e insere uma linha demo.
- Observe que os logs de `invalid length of startup packet` podem continuar se a porta pública do Postgres permanecer exposta; isso é esperado e **não impacta a aplicação**.

## Observação final
Se o ruído de log for incômodo, a mitigação efetiva é **fechar ou restringir** a porta pública do Postgres. Esse erro não tem correção no código da aplicação quando a origem é tráfego externo indevido.