worker: sh -lc "python src/main.py multirun --limit ${LIMIT:-1} --only ${ACCOUNT_NAME:-Milton_Albanez}"

unposted: python src/main.py unposted --limit ${LIMIT:-10}
autopost: python src/main.py autopost --style "${STYLE:-}"

# Para agendar via Cron no Railway, configure um job em UTC:
# Exemplo (06:00 BRT ≈ 09:00 UTC):
# Command: python src/main.py multirun --limit 1 --only Milton_Albanez
# Variáveis úteis:
# - ACCOUNT_NAME: nome da conta do accounts.json (default: Milton_Albanez)
# - LIMIT: limite de itens (default: 1)
# - STYLE: estilo opcional para autopost (ex.: "isometric, minimalista")