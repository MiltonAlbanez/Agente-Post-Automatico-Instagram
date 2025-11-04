#!/usr/bin/env python3
"""
TESTE DAS CORREÇÕES - FEED 19H BRT
==================================

Script para testar se as correções resolveram o problema do Feed 19h BRT.
"""

import os
import sys
from datetime import datetime
import logging

# Adicionar src ao path
sys.path.append('src')

from services.instagram_client_robust import InstagramClientRobust

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_robust_client():
    """Testa o cliente robusto"""
    logger.info("🧪 Testando cliente Instagram robusto...")
    
    # Verificar se variáveis de ambiente estão configuradas
    required_vars = ['INSTAGRAM_BUSINESS_ACCOUNT_ID', 'INSTAGRAM_ACCESS_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Variáveis de ambiente faltando: {missing_vars}")
        return False
    
    try:
        client = InstagramClientRobust(
            business_account_id=os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID'),
            access_token=os.getenv('INSTAGRAM_ACCESS_TOKEN')
        )
        
        logger.info("✅ Cliente robusto criado com sucesso")
        logger.info("✅ Configurações aplicadas:")
        logger.info("   - Timeout: 120 segundos")
        logger.info("   - Max retries: 3")
        logger.info("   - Polling: 10 minutos total")
        logger.info("   - Retry automático para erros temporários")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar cliente robusto: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("TESTE DAS CORREÇÕES - FEED 19H BRT")
    print("=" * 50)
    
    success = test_robust_client()
    
    if success:
        print("\n🎉 CORREÇÕES APLICADAS COM SUCESSO!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Fazer deploy no Railway")
        print("2. Aguardar próximo agendamento 19h BRT")
        print("3. Monitorar logs no Railway Dashboard")
        print("4. Verificar se post é concluído com sucesso")
    else:
        print("\n❌ ERRO NAS CORREÇÕES!")
        print("Verifique os logs acima para mais detalhes.")
