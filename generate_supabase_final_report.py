#!/usr/bin/env python3
"""
Script para gerar relatório final consolidado da verificação do Supabase
Consolida todos os testes realizados e gera relatório detalhado
"""

import os
import json
from datetime import datetime

class SupabaseFinalReportGenerator:
    def __init__(self):
        self.timestamp = datetime.now()
        self.final_report = {
            "timestamp": self.timestamp.isoformat(),
            "report_type": "supabase_final_verification",
            "executive_summary": {},
            "component_results": {},
            "overall_assessment": {},
            "critical_issues": [],
            "recommendations": [],
            "next_steps": [],
            "metadata": {
                "tests_performed": [],
                "reports_analyzed": [],
                "total_components_tested": 0,
                "total_tests_executed": 0
            }
        }
    
    def load_individual_reports(self):
        """Carrega relatórios individuais gerados"""
        reports = {}
        
        # Lista de relatórios para carregar
        report_files = [
            "supabase_verification_report_20251023_195841.json",
            "supabase_demo_verification_report_20251023_200035.json",
            "supabase_real_config_report_20251023_200228.json"
        ]
        
        for report_file in report_files:
            if os.path.exists(report_file):
                try:
                    with open(report_file, "r", encoding="utf-8") as f:
                        report_data = json.load(f)
                    reports[report_file] = report_data
                    self.final_report["metadata"]["reports_analyzed"].append(report_file)
                except Exception as e:
                    print(f"⚠️ Erro ao carregar {report_file}: {e}")
        
        return reports
    
    def analyze_component_status(self, reports):
        """Analisa status de cada componente do Supabase"""
        components = {
            "postgresql_database": {
                "name": "Banco de Dados PostgreSQL",
                "status": "NOT_TESTED",
                "score": 0,
                "max_score": 0,
                "details": {},
                "tests_performed": []
            },
            "authentication": {
                "name": "Autenticação e Autorização",
                "status": "NOT_TESTED",
                "score": 0,
                "max_score": 0,
                "details": {},
                "tests_performed": []
            },
            "rest_graphql_apis": {
                "name": "APIs REST e GraphQL",
                "status": "NOT_TESTED",
                "score": 0,
                "max_score": 0,
                "details": {},
                "tests_performed": []
            },
            "file_storage": {
                "name": "Armazenamento de Arquivos",
                "status": "NOT_TESTED",
                "score": 0,
                "max_score": 0,
                "details": {},
                "tests_performed": []
            },
            "edge_functions_rpc": {
                "name": "Funções Edge e RPC",
                "status": "NOT_TESTED",
                "score": 0,
                "max_score": 0,
                "details": {},
                "tests_performed": []
            },
            "service_availability": {
                "name": "Disponibilidade do Serviço",
                "status": "NOT_TESTED",
                "score": 0,
                "max_score": 0,
                "details": {},
                "tests_performed": []
            },
            "configuration": {
                "name": "Configuração Local",
                "status": "NOT_TESTED",
                "score": 0,
                "max_score": 0,
                "details": {},
                "tests_performed": []
            },
            "implementation": {
                "name": "Implementação no Código",
                "status": "NOT_TESTED",
                "score": 0,
                "max_score": 0,
                "details": {},
                "tests_performed": []
            }
        }
        
        # Analisar cada relatório
        for report_name, report_data in reports.items():
            if "components" in report_data:
                for comp_key, comp_data in report_data["components"].items():
                    
                    # Mapear componentes dos relatórios para categorias finais
                    if comp_key in ["service_availability"]:
                        target_comp = "service_availability"
                    elif comp_key in ["project_structure", "api_capabilities"]:
                        target_comp = "rest_graphql_apis"
                    elif comp_key in ["local_configuration", "local_configurations"]:
                        target_comp = "configuration"
                    elif comp_key in ["supabase_implementation"]:
                        target_comp = "implementation"
                    elif comp_key in ["connectivity_test"]:
                        target_comp = "postgresql_database"
                    elif comp_key in ["railway_variables"]:
                        target_comp = "configuration"
                    else:
                        continue
                    
                    # Atualizar dados do componente
                    if target_comp in components:
                        comp = components[target_comp]
                        comp["score"] += comp_data.get("score", 0)
                        comp["max_score"] += comp_data.get("max_score", 0)
                        comp["tests_performed"].extend(comp_data.get("tests", []))
                        
                        # Atualizar status (pior status prevalece)
                        current_status = comp_data.get("status", "NOT_TESTED")
                        if comp["status"] == "NOT_TESTED":
                            comp["status"] = current_status
                        elif current_status in ["ERROR", "CRITICAL", "UNHEALTHY", "NOT_CONFIGURED", "NOT_CONNECTED"]:
                            comp["status"] = current_status
                        elif current_status in ["PARTIAL", "MINIMAL", "LIMITED"] and comp["status"] not in ["ERROR", "CRITICAL", "UNHEALTHY"]:
                            comp["status"] = current_status
                        
                        # Adicionar detalhes
                        comp["details"].update(comp_data.get("details", {}))
        
        # Calcular status final para cada componente
        for comp_key, comp in components.items():
            if comp["max_score"] > 0:
                percentage = (comp["score"] / comp["max_score"]) * 100
                
                if percentage >= 90:
                    comp["final_status"] = "EXCELENTE"
                elif percentage >= 75:
                    comp["final_status"] = "BOM"
                elif percentage >= 50:
                    comp["final_status"] = "PARCIAL"
                elif percentage >= 25:
                    comp["final_status"] = "LIMITADO"
                else:
                    comp["final_status"] = "CRÍTICO"
            else:
                comp["final_status"] = "NÃO_CONFIGURADO"
        
        return components
    
    def generate_executive_summary(self, components, reports):
        """Gera resumo executivo"""
        total_score = sum(comp["score"] for comp in components.values())
        total_max_score = sum(comp["max_score"] for comp in components.values())
        
        if total_max_score > 0:
            overall_percentage = (total_score / total_max_score) * 100
        else:
            overall_percentage = 0
        
        # Determinar status geral
        if overall_percentage >= 90:
            overall_status = "EXCELENTE"
        elif overall_percentage >= 75:
            overall_status = "BOM"
        elif overall_percentage >= 50:
            overall_status = "PARCIAL"
        elif overall_percentage >= 25:
            overall_status = "LIMITADO"
        else:
            overall_status = "CRÍTICO"
        
        # Contar componentes por status
        status_counts = {}
        for comp in components.values():
            status = comp["final_status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Contar total de testes
        total_tests = sum(len(comp["tests_performed"]) for comp in components.values())
        
        summary = {
            "overall_status": overall_status,
            "overall_score": f"{total_score}/{total_max_score}",
            "overall_percentage": f"{overall_percentage:.1f}%",
            "components_tested": len(components),
            "total_tests_executed": total_tests,
            "status_distribution": status_counts,
            "reports_analyzed": len(reports),
            "test_date": self.timestamp.strftime("%d/%m/%Y às %H:%M:%S")
        }
        
        return summary
    
    def identify_critical_issues(self, components):
        """Identifica problemas críticos"""
        critical_issues = []
        
        for comp_key, comp in components.items():
            if comp["final_status"] in ["CRÍTICO", "NÃO_CONFIGURADO"]:
                critical_issues.append({
                    "component": comp["name"],
                    "issue": f"Componente {comp['name']} não está configurado ou funcional",
                    "impact": "ALTO",
                    "details": f"Status: {comp['final_status']}, Score: {comp['score']}/{comp['max_score']}"
                })
            elif comp["final_status"] == "LIMITADO":
                critical_issues.append({
                    "component": comp["name"],
                    "issue": f"Componente {comp['name']} com funcionalidade limitada",
                    "impact": "MÉDIO",
                    "details": f"Status: {comp['final_status']}, Score: {comp['score']}/{comp['max_score']}"
                })
        
        # Problemas específicos identificados
        config_comp = components.get("configuration", {})
        if config_comp.get("final_status") in ["CRÍTICO", "NÃO_CONFIGURADO"]:
            critical_issues.append({
                "component": "Configuração Geral",
                "issue": "Supabase não está configurado no sistema",
                "impact": "CRÍTICO",
                "details": "Nenhuma variável de ambiente ou configuração válida encontrada"
            })
        
        impl_comp = components.get("implementation", {})
        if impl_comp.get("score", 0) > 0:
            critical_issues.append({
                "component": "Implementação",
                "issue": "Código preparado mas sem configuração",
                "impact": "MÉDIO",
                "details": "SupabaseUploader implementado mas sem credenciais válidas"
            })
        
        return critical_issues
    
    def generate_recommendations(self, components, critical_issues):
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Recomendações baseadas em problemas críticos
        config_issues = any(issue["component"] in ["Configuração Local", "Configuração Geral"] for issue in critical_issues)
        if config_issues:
            recommendations.append({
                "priority": "CRÍTICA",
                "category": "Configuração",
                "action": "Configurar projeto Supabase",
                "description": "Criar projeto no Supabase e configurar todas as variáveis necessárias",
                "steps": [
                    "1. Criar conta no Supabase (https://supabase.com)",
                    "2. Criar novo projeto",
                    "3. Obter SUPABASE_URL e SUPABASE_SERVICE_KEY",
                    "4. Configurar variáveis no Railway",
                    "5. Criar bucket para armazenamento de imagens"
                ]
            })
        
        # Verificar se implementação está pronta
        impl_comp = components.get("implementation", {})
        if impl_comp.get("score", 0) > 0:
            recommendations.append({
                "priority": "ALTA",
                "category": "Implementação",
                "action": "Ativar funcionalidade do Supabase",
                "description": "O código está preparado, apenas faltam as configurações",
                "steps": [
                    "1. Configurar variáveis de ambiente",
                    "2. Testar upload de imagens",
                    "3. Verificar permissões do bucket",
                    "4. Validar integração no pipeline"
                ]
            })
        
        # Recomendações de monitoramento
        recommendations.append({
            "priority": "MÉDIA",
            "category": "Monitoramento",
            "action": "Implementar monitoramento do Supabase",
            "description": "Adicionar logs e métricas para acompanhar uso do Supabase",
            "steps": [
                "1. Adicionar logs de upload",
                "2. Monitorar quotas de armazenamento",
                "3. Configurar alertas de erro",
                "4. Acompanhar performance das APIs"
            ]
        })
        
        return recommendations
    
    def generate_next_steps(self, components, recommendations):
        """Gera próximos passos"""
        next_steps = []
        
        # Verificar se há problemas críticos
        critical_count = sum(1 for comp in components.values() if comp["final_status"] in ["CRÍTICO", "NÃO_CONFIGURADO"])
        
        if critical_count > 0:
            next_steps.extend([
                "🔴 URGENTE: Configurar projeto Supabase",
                "📝 Obter credenciais do Supabase",
                "⚙️ Configurar variáveis no Railway",
                "🧪 Testar conectividade básica"
            ])
        else:
            next_steps.extend([
                "✅ Validar configurações existentes",
                "🔧 Otimizar implementação",
                "📊 Implementar monitoramento",
                "🚀 Ativar em produção"
            ])
        
        # Adicionar passos específicos baseados em recomendações
        for rec in recommendations:
            if rec["priority"] == "CRÍTICA":
                next_steps.append(f"🔴 {rec['action']}")
            elif rec["priority"] == "ALTA":
                next_steps.append(f"🟠 {rec['action']}")
        
        return next_steps
    
    def save_reports(self, final_report):
        """Salva relatórios em JSON e Markdown"""
        timestamp_str = self.timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Salvar JSON
        json_filename = f"RELATORIO_FINAL_SUPABASE_{timestamp_str}.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        # Gerar Markdown
        md_filename = f"RELATORIO_FINAL_SUPABASE_{timestamp_str}.md"
        md_content = self.generate_markdown_report(final_report)
        
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(md_content)
        
        return json_filename, md_filename
    
    def generate_markdown_report(self, report):
        """Gera relatório em formato Markdown"""
        md = []
        
        # Cabeçalho
        md.append("# 📊 RELATÓRIO FINAL DE VERIFICAÇÃO DO SUPABASE")
        md.append("")
        md.append(f"**Data:** {report['executive_summary']['test_date']}")
        md.append(f"**Tipo:** Verificação Completa do Supabase")
        md.append("")
        
        # Resumo Executivo
        md.append("## 🎯 RESUMO EXECUTIVO")
        md.append("")
        summary = report['executive_summary']
        md.append(f"- **Status Geral:** {summary['overall_status']}")
        md.append(f"- **Pontuação:** {summary['overall_score']} ({summary['overall_percentage']})")
        md.append(f"- **Componentes Testados:** {summary['components_tested']}")
        md.append(f"- **Total de Testes:** {summary['total_tests_executed']}")
        md.append("")
        
        # Distribuição de Status
        md.append("### 📈 Distribuição de Status")
        md.append("")
        for status, count in summary['status_distribution'].items():
            emoji = {
                "EXCELENTE": "✅",
                "BOM": "✅", 
                "PARCIAL": "⚠️",
                "LIMITADO": "🟡",
                "CRÍTICO": "❌",
                "NÃO_CONFIGURADO": "⚙️"
            }.get(status, "❓")
            md.append(f"- {emoji} **{status}:** {count} componente(s)")
        md.append("")
        
        # Resultados por Componente
        md.append("## 📋 RESULTADOS POR COMPONENTE")
        md.append("")
        
        for comp_key, comp in report['component_results'].items():
            status_emoji = {
                "EXCELENTE": "✅",
                "BOM": "✅",
                "PARCIAL": "⚠️", 
                "LIMITADO": "🟡",
                "CRÍTICO": "❌",
                "NÃO_CONFIGURADO": "⚙️"
            }.get(comp['final_status'], "❓")
            
            md.append(f"### {status_emoji} {comp['name']}")
            md.append(f"- **Status:** {comp['final_status']}")
            md.append(f"- **Pontuação:** {comp['score']}/{comp['max_score']}")
            md.append(f"- **Testes Realizados:** {len(comp['tests_performed'])}")
            md.append("")
        
        # Problemas Críticos
        if report['critical_issues']:
            md.append("## 🚨 PROBLEMAS CRÍTICOS")
            md.append("")
            for issue in report['critical_issues']:
                impact_emoji = {"CRÍTICO": "🔴", "ALTO": "🟠", "MÉDIO": "🟡"}.get(issue['impact'], "⚪")
                md.append(f"### {impact_emoji} {issue['component']}")
                md.append(f"- **Problema:** {issue['issue']}")
                md.append(f"- **Impacto:** {issue['impact']}")
                md.append(f"- **Detalhes:** {issue['details']}")
                md.append("")
        
        # Recomendações
        if report['recommendations']:
            md.append("## 💡 RECOMENDAÇÕES")
            md.append("")
            for rec in report['recommendations']:
                priority_emoji = {"CRÍTICA": "🔴", "ALTA": "🟠", "MÉDIA": "🟡", "BAIXA": "🟢"}.get(rec['priority'], "⚪")
                md.append(f"### {priority_emoji} {rec['action']} ({rec['priority']})")
                md.append(f"**Categoria:** {rec['category']}")
                md.append(f"**Descrição:** {rec['description']}")
                md.append("")
                md.append("**Passos:**")
                for step in rec['steps']:
                    md.append(f"- {step}")
                md.append("")
        
        # Próximos Passos
        if report['next_steps']:
            md.append("## 🚀 PRÓXIMOS PASSOS")
            md.append("")
            for step in report['next_steps']:
                md.append(f"- {step}")
            md.append("")
        
        # Conclusão
        md.append("## 📝 CONCLUSÃO")
        md.append("")
        overall_status = report['executive_summary']['overall_status']
        
        if overall_status in ["EXCELENTE", "BOM"]:
            md.append("✅ **O Supabase está configurado e funcional.** O sistema está pronto para uso em produção.")
        elif overall_status == "PARCIAL":
            md.append("⚠️ **O Supabase está parcialmente configurado.** Algumas melhorias são necessárias antes do uso em produção.")
        elif overall_status == "LIMITADO":
            md.append("🟡 **O Supabase tem configuração limitada.** Configuração adicional é necessária para funcionalidade completa.")
        else:
            md.append("❌ **O Supabase não está configurado.** Configuração completa é necessária antes do uso.")
        
        md.append("")
        md.append("---")
        md.append(f"*Relatório gerado automaticamente em {report['executive_summary']['test_date']}*")
        
        return "\n".join(md)
    
    def generate_final_report(self):
        """Gera relatório final consolidado"""
        print("📊 Gerando relatório final do Supabase...")
        
        # Carregar relatórios individuais
        reports = self.load_individual_reports()
        print(f"📄 Carregados {len(reports)} relatórios")
        
        # Analisar componentes
        components = self.analyze_component_status(reports)
        print(f"🔍 Analisados {len(components)} componentes")
        
        # Gerar resumo executivo
        executive_summary = self.generate_executive_summary(components, reports)
        
        # Identificar problemas críticos
        critical_issues = self.identify_critical_issues(components)
        
        # Gerar recomendações
        recommendations = self.generate_recommendations(components, critical_issues)
        
        # Gerar próximos passos
        next_steps = self.generate_next_steps(components, recommendations)
        
        # Montar relatório final
        self.final_report.update({
            "executive_summary": executive_summary,
            "component_results": components,
            "overall_assessment": {
                "total_components": len(components),
                "functional_components": sum(1 for comp in components.values() if comp["final_status"] in ["EXCELENTE", "BOM"]),
                "problematic_components": sum(1 for comp in components.values() if comp["final_status"] in ["CRÍTICO", "NÃO_CONFIGURADO"]),
                "needs_attention": sum(1 for comp in components.values() if comp["final_status"] in ["PARCIAL", "LIMITADO"])
            },
            "critical_issues": critical_issues,
            "recommendations": recommendations,
            "next_steps": next_steps
        })
        
        # Atualizar metadados
        self.final_report["metadata"].update({
            "total_components_tested": len(components),
            "total_tests_executed": sum(len(comp["tests_performed"]) for comp in components.values()),
            "tests_performed": list(set([test.get("name", "Unknown") for comp in components.values() for test in comp["tests_performed"]]))
        })
        
        # Salvar relatórios
        json_file, md_file = self.save_reports(self.final_report)
        
        print()
        print("=" * 70)
        print("📊 RELATÓRIO FINAL DE VERIFICAÇÃO DO SUPABASE")
        print("=" * 70)
        print(f"🎯 Status Geral: {executive_summary['overall_status']}")
        print(f"📈 Pontuação: {executive_summary['overall_score']} ({executive_summary['overall_percentage']})")
        print(f"🧪 Testes Executados: {executive_summary['total_tests_executed']}")
        print()
        
        print("📋 COMPONENTES:")
        for comp_key, comp in components.items():
            status_emoji = {
                "EXCELENTE": "✅",
                "BOM": "✅",
                "PARCIAL": "⚠️",
                "LIMITADO": "🟡", 
                "CRÍTICO": "❌",
                "NÃO_CONFIGURADO": "⚙️"
            }.get(comp['final_status'], "❓")
            print(f"  {status_emoji} {comp['name']}: {comp['final_status']} ({comp['score']}/{comp['max_score']})")
        
        if critical_issues:
            print()
            print("🚨 PROBLEMAS CRÍTICOS:")
            for issue in critical_issues:
                impact_emoji = {"CRÍTICO": "🔴", "ALTO": "🟠", "MÉDIO": "🟡"}.get(issue['impact'], "⚪")
                print(f"  {impact_emoji} {issue['component']}: {issue['issue']}")
        
        if recommendations:
            print()
            print("💡 PRINCIPAIS RECOMENDAÇÕES:")
            for rec in recommendations[:3]:  # Mostrar apenas as 3 principais
                priority_emoji = {"CRÍTICA": "🔴", "ALTA": "🟠", "MÉDIA": "🟡"}.get(rec['priority'], "⚪")
                print(f"  {priority_emoji} [{rec['priority']}] {rec['action']}")
        
        print()
        print("📝 CONCLUSÃO:")
        overall_status = executive_summary['overall_status']
        if overall_status in ["EXCELENTE", "BOM"]:
            print("  ✅ Supabase configurado e funcional")
        elif overall_status == "PARCIAL":
            print("  ⚠️ Supabase parcialmente configurado - melhorias necessárias")
        elif overall_status == "LIMITADO":
            print("  🟡 Supabase com configuração limitada")
        else:
            print("  ❌ Supabase não configurado - configuração completa necessária")
        
        print()
        print(f"📄 Relatórios salvos:")
        print(f"  📊 JSON: {json_file}")
        print(f"  📝 Markdown: {md_file}")
        print("=" * 70)
        
        return self.final_report

if __name__ == "__main__":
    generator = SupabaseFinalReportGenerator()
    final_report = generator.generate_final_report()