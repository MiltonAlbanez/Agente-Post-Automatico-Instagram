from datetime import datetime, timezone, timedelta

# Horário atual
utc_now = datetime.now(timezone.utc)
brt_now = utc_now - timedelta(hours=3)  # UTC-3 = BRT

print(f"🕐 Horário atual: {brt_now.strftime('%H:%M')} BRT ({utc_now.strftime('%H:%M')} UTC)")
print(f"📅 Data: {brt_now.strftime('%d/%m/%Y')}")
print(f"⏰ É 15h BRT? {brt_now.hour == 15}")

# Simular 15h BRT
brt_15h = brt_now.replace(hour=15, minute=0, second=0, microsecond=0)
utc_15h = brt_15h + timedelta(hours=3)  # BRT+3 = UTC

print(f"\n🎯 SIMULAÇÃO 15h BRT:")
print(f"   BRT: {brt_15h.strftime('%H:%M')} BRT")
print(f"   UTC: {utc_15h.strftime('%H:%M')} UTC")
print(f"   Fallback ativado? {brt_15h.hour == 15}")

# Próxima execução
if brt_now.hour >= 15:
    # Amanhã
    proxima = brt_now.replace(hour=15, minute=0, second=0, microsecond=0) + timedelta(days=1)
else:
    # Hoje
    proxima = brt_now.replace(hour=15, minute=0, second=0, microsecond=0)

print(f"\n⏭️ PRÓXIMA EXECUÇÃO STORIES:")
print(f"   {proxima.strftime('%d/%m/%Y às %H:%M')} BRT")
print(f"   {(proxima + timedelta(hours=3)).strftime('%d/%m/%Y às %H:%M')} UTC")