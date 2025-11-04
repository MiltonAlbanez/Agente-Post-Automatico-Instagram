# AGENDADOR AUTOMÁTICO 24/7 - COMANDO PRINCIPAL (processo web)
web: python railway_scheduler.py

# COMANDOS MANUAIS (para testes)
unposted: python -m src.main unposted --limit ${LIMIT:-10}
autopost: python -m src.main autopost --style "${STYLE:-}"
teste: python railway_automation_teste.py

# AGENDADOR AUTOMÁTICO:
# O comando 'scheduler' executa o sistema 24/7 com agendamentos automáticos:
# - Feed: 06:00, 12:00, 18:00, 19:00 BRT (09:00, 15:00, 21:00, 22:00 UTC)
# - Stories: 09:00, 15:00, 21:00 BRT (12:00, 18:00, 00:00 UTC)
# - Processa TODAS as contas do accounts.json automaticamente
# - Funciona de forma completamente autônoma na nuvem

# COMANDOS MANUAIS ANTIGOS (para referência):
# - ACCOUNT_NAME: nome da conta do accounts.json (default: Milton_Albanez)
# - LIMIT: limite de itens (default: 1)
# - STYLE: estilo opcional para autopost (ex.: "street, portrait, natural light")