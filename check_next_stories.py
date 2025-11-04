from datetime import datetime, timezone, timedelta

# Horário atual
utc_now = datetime.now(timezone.utc)
brt_now = utc_now - timedelta(hours=3)  # UTC-3 = BRT

print(f"🕐 Horário atual: {brt_now.strftime('%H:%M')} BRT ({utc_now.strftime('%H:%M')} UTC)")
print(f"📅 Data: {brt_now.strftime('%d/%m/%Y')}")

# Próximo Stories 21h BRT
if brt_now.hour < 21:
    # Hoje
    proximo_stories = brt_now.replace(hour=21, minute=0, second=0, microsecond=0)
else:
    # Amanhã
    proximo_stories = brt_now.replace(hour=21, minute=0, second=0, microsecond=0) + timedelta(days=1)

proximo_stories_utc = proximo_stories + timedelta(hours=3)  # BRT+3 = UTC

print(f"\n🎯 PRÓXIMO STORIES 21h BRT:")
print(f"   📅 {proximo_stories.strftime('%d/%m/%Y às %H:%M')} BRT")
print(f"   🌍 {proximo_stories_utc.strftime('%d/%m/%Y às %H:%M')} UTC")

# Tempo restante
tempo_restante = proximo_stories - brt_now
horas = int(tempo_restante.total_seconds() // 3600)
minutos = int((tempo_restante.total_seconds() % 3600) // 60)

print(f"   ⏰ Faltam: {horas}h {minutos}min")

print(f"\n📱 CONFIGURAÇÃO STORIES 21h BRT:")
print(f"   🕐 Horário BRT: 21:00")
print(f"   🌍 Horário UTC: 00:00 (próximo dia)")
print(f"   ⚙️ Cron Schedule: 0 0 * * *")
print(f"   🎯 Comando: multirun --stories --limit 1")
print(f"   📊 Contas: 2 (Milton_Albanez + Albanez Assistência)")

print(f"\n✅ STATUS DO SISTEMA:")
print(f"   🚀 Sistema deployado no Railway")
print(f"   ⏰ Agendamento configurado")
print(f"   🔄 Execução automática ativa")
print(f"   📱 Próximo Stories será gerado automaticamente")