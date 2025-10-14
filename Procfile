worker: python simple_test.py

unposted: python src/main.py unposted --limit ${LIMIT:-10}
autopost: python src/main.py autopost --style "${STYLE:-}"

# Para agendar via Cron no Railway, configure um job em UTC:
# Exemplo (06:00 BRT ≈ 09:00 UTC):
# Command: python src/main.py multirun --limit 1 --only Milton_Albanez
# Variáveis úteis:
# - ACCOUNT_NAME: nome da conta do accounts.json (default: Milton_Albanez)
# - LIMIT: limite de itens (default: 1)
# - STYLE: estilo opcional para autopost (ex.: "street, portrait, natural light")
# Obs: autopost agora gera imagens coerentes com o conteúdo usando Replicate.