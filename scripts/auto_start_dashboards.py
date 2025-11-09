#!/usr/bin/env python3
"""
Script de Auto-Inicialização dos Dashboards
Inicia automaticamente os dashboards nas portas 5000 e 8502 quando o sistema é iniciado.
"""

import os
import sys
import time
import subprocess
import threading
import signal
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

class DashboardManager:
    """Gerenciador de dashboards para auto-inicialização"""
    
    def __init__(self):
        self.processes = {}
        self.running = True
        self.project_root = Path(__file__).parent.parent
        
    def start_flask_dashboard(self):
        """Iniciar dashboard Flask (porta 5000)"""
        try:
            print("🚀 Iniciando Dashboard A/B Testing (porta 5000)...")
            
            dashboard_path = self.project_root / "dashboard" / "dashboard_server.py"
            
            if dashboard_path.exists():
                process = subprocess.Popen(
                    [sys.executable, str(dashboard_path)],
                    cwd=str(self.project_root),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                self.processes['flask'] = process
                print("✅ Dashboard A/B Testing iniciado com sucesso!")
                print("📊 Acesse: http://localhost:5000")
                
                return True
            else:
                print("❌ Arquivo dashboard_server.py não encontrado!")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao iniciar Dashboard Flask: {e}")
            return False
    
    def start_streamlit_dashboard(self):
        """Iniciar dashboard Streamlit (porta 8502)"""
        try:
            print("🚀 Iniciando Dashboard de Automação (porta 8502)...")
            
            dashboard_path = self.project_root / "automation" / "automation_dashboard.py"
            
            if dashboard_path.exists():
                process = subprocess.Popen(
                    [
                        sys.executable, "-m", "streamlit", "run", 
                        str(dashboard_path), 
                        "--server.port", "8502",
                        "--server.headless", "true"
                    ],
                    cwd=str(self.project_root),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                self.processes['streamlit'] = process
                print("✅ Dashboard de Automação iniciado com sucesso!")
                print("📊 Acesse: http://localhost:8502")
                
                return True
            else:
                print("❌ Arquivo automation_dashboard.py não encontrado!")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao iniciar Dashboard Streamlit: {e}")
            return False
    
    def check_port_availability(self, port):
        """Verificar se uma porta está disponível"""
        import socket
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def wait_for_dashboards(self):
        """Aguardar que os dashboards estejam prontos"""
        print("⏳ Aguardando dashboards ficarem prontos...")
        
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts and self.running:
            flask_ready = not self.check_port_availability(5000)
            streamlit_ready = not self.check_port_availability(8502)
            
            if flask_ready and streamlit_ready:
                print("✅ Ambos os dashboards estão prontos!")
                break
            elif flask_ready:
                print("✅ Dashboard Flask pronto (porta 5000)")
            elif streamlit_ready:
                print("✅ Dashboard Streamlit pronto (porta 8502)")
            
            time.sleep(2)
            attempt += 1
        
        if attempt >= max_attempts:
            print("⚠️ Timeout aguardando dashboards ficarem prontos")
    
    def monitor_processes(self):
        """Monitorar processos e reiniciar se necessário"""
        while self.running:
            for name, process in list(self.processes.items()):
                if process.poll() is not None:
                    print(f"⚠️ Dashboard {name} parou inesperadamente. Reiniciando...")
                    
                    if name == 'flask':
                        self.start_flask_dashboard()
                    elif name == 'streamlit':
                        self.start_streamlit_dashboard()
            
            time.sleep(10)
    
    def stop_all_dashboards(self):
        """Parar todos os dashboards"""
        print("🛑 Parando dashboards...")
        self.running = False
        
        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Dashboard {name} parado")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔥 Dashboard {name} forçado a parar")
            except Exception as e:
                print(f"❌ Erro ao parar dashboard {name}: {e}")
    
    def start_all_dashboards(self):
        """Iniciar todos os dashboards"""
        print("🚀 Iniciando sistema de dashboards...")
        print("=" * 50)
        
        # Verificar portas
        if not self.check_port_availability(5000):
            print("⚠️ Porta 5000 já está em uso")
        
        if not self.check_port_availability(8502):
            print("⚠️ Porta 8502 já está em uso")
        
        # Iniciar dashboards
        flask_started = self.start_flask_dashboard()
        time.sleep(2)  # Aguardar um pouco entre inicializações
        
        streamlit_started = self.start_streamlit_dashboard()
        
        if flask_started or streamlit_started:
            # Aguardar dashboards ficarem prontos
            self.wait_for_dashboards()
            
            # Iniciar monitoramento em thread separada
            monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
            monitor_thread.start()
            
            print("=" * 50)
            print("🎉 Sistema de dashboards iniciado com sucesso!")
            print("📊 Dashboard A/B Testing: http://localhost:5000")
            print("🤖 Dashboard de Automação: http://localhost:8502")
            print("⚡ Use Ctrl+C para parar todos os dashboards")
            print("=" * 50)
            
            return True
        else:
            print("❌ Falha ao iniciar dashboards")
            return False

def signal_handler(signum, frame):
    """Handler para sinais de interrupção"""
    print("\n🛑 Recebido sinal de interrupção...")
    if 'manager' in globals():
        manager.stop_all_dashboards()
    sys.exit(0)

def main():
    """Função principal"""
    global manager
    
    # Configurar handlers de sinal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    manager = DashboardManager()
    
    try:
        success = manager.start_all_dashboards()
        
        if success:
            # Manter o script rodando
            while manager.running:
                time.sleep(1)
        else:
            print("❌ Falha ao iniciar sistema de dashboards")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    finally:
        manager.stop_all_dashboards()

if __name__ == "__main__":
    main()