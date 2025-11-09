from datetime import datetime, timezone, timedelta

# Horário atual
utc_now = datetime.now(timezone.utc)
brt_now = utc_now - timedelta(hours=3)  # UTC-3 = BRT

print(f"🕐 Horário atual: {brt_now.strftime('%H:%M')} BRT ({utc_now.strftime('%H:%M')} UTC)")
print(f"📅 Data: {brt_now.strftime('%d/%m/%Y')}")

# Próximo Feed 18h BRT
if brt_now.hour >= 18:
    # Amanhã
    proximo_feed = brt_now.replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=1)
else:
    # Hoje
    proximo_feed = brt_now.replace(hour=18, minute=0, second=0, microsecond=0)

proximo_feed_utc = proximo_feed + timedelta(hours=3)  # BRT+3 = UTC

print(f"\n🎯 PRÓXIMO FEED 18h BRT:")
print(f"   📅 {proximo_feed.strftime('%d/%m/%Y às %H:%M')} BRT")
print(f"   🌍 {proximo_feed_utc.strftime('%d/%m/%Y às %H:%M')} UTC")

# Tempo restante
tempo_restante = proximo_feed - brt_now
horas = int(tempo_restante.total_seconds() // 3600)
minutos = int((tempo_restante.total_seconds() % 3600) // 60)

print(f"   ⏰ Faltam: {horas}h {minutos}min")

# Verificar se é horário crítico para Feed (não há horário crítico específico para Feed)
print(f"\n📊 MODO FEED:")
print(f"   🔍 RapidAPI será testado primeiro")
print(f"   🔄 Fallback ativado apenas se RapidAPI falhar")
print(f"   ✅ Não há horário crítico específico para Feed (diferente de Stories)")

# Agendamentos do dia
print(f"\n📋 AGENDAMENTOS HOJE ({brt_now.strftime('%d/%m/%Y')}):")
agendamentos = [
    ("06:00", "Feed Matinal"),
    ("09:00", "Stories Matinal"), 
    ("12:00", "Feed Meio-dia"),
    ("15:00", "Stories Meio-dia"),
    ("18:00", "Feed Noturno"),
    ("21:00", "Stories Noturno")
]

for hora, tipo in agendamentos:
    hora_obj = datetime.strptime(hora, "%H:%M").time()
    agendamento_hoje = brt_now.replace(hour=hora_obj.hour, minute=hora_obj.minute, second=0, microsecond=0)
    
    if agendamento_hoje > brt_now:
        status = "⏳ PENDENTE"
    elif agendamento_hoje.hour == brt_now.hour:
        status = "🔄 EXECUTANDO"
    else:
        status = "✅ CONCLUÍDO"
    
    print(f"   {hora} BRT - {tipo}: {status}")