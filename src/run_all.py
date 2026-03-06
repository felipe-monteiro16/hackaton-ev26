#!/usr/bin/env python3
"""
Pipeline completo de análise epidemiológica
Executa todos os passos da análise em sequência
"""

import subprocess
import sys
from pathlib import Path

def run_script(script_name, description):
    """Executa um script Python e exibe o resultado"""
    print("\n" + "=" * 80)
    print(f"EXECUTANDO: {description}")
    print("=" * 80)
    
    script_path = Path(__file__).parent / script_name
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,
            text=True,
            check=True
        )
        print(f"✓ {description} concluído com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ ERRO ao executar {description}")
        print(f"Código de saída: {e.returncode}")
        return False

def main():
    """Executapipeline completo"""
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETO DE ANÁLISE EPIDEMIOLÓGICA")
    print("Dengue x Precipitação - Montes Claros/MG")
    print("=" * 80)
    
    scripts = [
        ("main.py", "Tratamento de dados SINAN"),
        ("correlacao_temporal.py", "Análise de correlação temporal"),
        ("visualizacoes_apresentacao.py", "Geração de visualizações para apresentação")
    ]
    
    results = []
    for script, desc in scripts:
        success = run_script(script, desc)
        results.append((desc, success))
    
    # Resumo final
    print("\n" + "=" * 80)
    print("RESUMO DA EXECUÇÃO")
    print("=" * 80)
    
    for desc, success in results:
        status = "✓ OK" if success else "✗ FALHOU"
        print(f"{status}: {desc}")
    
    all_success = all(success for _, success in results)
    
    if all_success:
        print("\n" + "=" * 80)
        print("✓✓✓ PIPELINE COMPLETO EXECUTADO COM SUCESSO! ✓✓✓")
        print("=" * 80)
        print("\nArquivos gerados em output/:")
        print("  • Dados processados (CSV)")
        print("  • 6 visualizações para apresentação (PNG)")
        print("  • Resumo executivo (RESUMO_EXECUTIVO.md)")
        print("\nVeja output/RESUMO_EXECUTIVO.md para detalhes completos.")
        print("=" * 80)
        return 0
    else:
        print("\n" + "=" * 80)
        print("⚠️ PIPELINE CONCLUÍDO COM ERROS")
        print("=" * 80)
        return 1

if __name__ == "__main__":
    sys.exit(main())
