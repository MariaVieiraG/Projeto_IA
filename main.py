import os
import time
# Importa apenas as classes necessárias do novo arquivo
from agente_a_estrela import AgenteAStar 
from agente_a_estrela import Labirinto

# --- FUNÇÕES DE TESTE E MAIN (NOVA LÓGICA) ---

def testar_agente_astar(nome_arquivo, heuristica):
    """Testa o Agente A* com uma heurística específica."""
    
    lab = Labirinto(nome_arquivo)
    
    if not lab.inicio or not lab.fim:
        return 0, 0.0, "Erro ao carregar Labirinto"
        
    agente_astar = AgenteAStar(lab)
    
    start_time = time.time()
    
    try:
        caminho, custo_total = agente_astar.solve_astar(heuristica)
        duracao = time.time() - start_time
        
        if caminho:
            passos = len(caminho) - 1
            return passos, duracao, "SUCESSO"
        else:
            return 0, duracao, "FALHA (Caminho não encontrado)"
            
    except Exception as e:
        duracao = time.time() - start_time
        return 0, duracao, f"ERRO: {e}"


def main():
    """Loop principal para testar o Agente A* e gerar o relatório."""
    
    arquivos = [
        "labirinto expiral.txt", "labiritno aleatorio1.txt", 
        "labirinto aleatorio 2.txt", "labirinto estrela.txt", 
        "labirinto onda.txt", "labirinto comeia.txt"
    ]
    
    heuristica_mapa = ["Manhattan", "Manhattan Ponderada", "Obstáculos"]
    resultados_comparativos = {}
    
    print("\n\n=== RELATÓRIO DE EXECUÇÃO: AGENTE BASEADO EM UTILIDADE (A*) ===\n")
    
    for nome_arquivo in arquivos:
        if not os.path.exists(nome_arquivo):
            print(f"ERRO: Arquivo '{nome_arquivo}' não encontrado. Pulando.\n")
            continue
            
        print(f"--- Labirinto: {nome_arquivo} ---")
        
        resultados_lab = {}
        
        # Testar cada heurística (Requisito 4)
        for heuristica in heuristica_mapa:
            passos, duracao, status = testar_agente_astar(nome_arquivo, heuristica)
            
            resultados_lab[heuristica] = {
                "passos": passos,
                "tempo": duracao,
                "status": status
            }
            print(f"  > {heuristica}: {status} | Passos: {passos} | Tempo: {duracao:.4f}s")

        resultados_comparativos[nome_arquivo] = resultados_lab
        print("-" * 30)

    # --- Tabela de Comparação Final (Requisito 6) ---
    print("\n### 📊 Comparação de Desempenho do A* entre Heurísticas ###")
    
    print("| Labirinto | Heurística | Passos (Caminho) | Tempo (s) | Status |")
    print("| :--- | :--- | :---: | :---: | :--- |")
    
    for nome_lab, res_lab in resultados_comparativos.items():
        primeira_linha = True
        
        sucessos = [res['passos'] for res in res_lab.values() if res['status'] == 'SUCESSO']
        melhor_passo = min(sucessos) if sucessos else 0
        
        for heuristica, res in res_lab.items():
            lab_str = nome_lab if primeira_linha else ""
            primeira_linha = False
            
            passos_str = str(res['passos'])
            if res['passos'] == melhor_passo and res['passos'] > 0:
                 passos_str = f"**{passos_str}**"
            
            print(f"| {lab_str} | {heuristica} | {passos_str} | {res['tempo']:.4f} | {res['status']} |")
    
if __name__ == "__main__":
    main()
