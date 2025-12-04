# 🧠 Projeto de IA: Agente de Labirinto

Este projeto implementa um ambiente de simulação para agentes inteligentes resolverem labirintos. A versão atual conta com um **Agente Reativo Simples** que utiliza regras de navegação local para encontrar a saída.

## 🚀 Funcionalidades

* **Ambiente de Simulação:**
    * Leitura de labirintos a partir de arquivos de texto (`.txt`).
    * Detecção automática dos pontos de início e fim baseada em coordenadas ou aberturas nas bordas.
    * Mecanismo de percepção que informa ao agente o estado das células vizinhas (Norte, Sul, Leste, Oeste).
* **Agente Reativo Simples:**
    * Implementa a estratégia da **Regra da Mão Direita**.
    * Toma decisões baseadas apenas na percepção imediata, sem memória de estados anteriores.
    * Prioridade de movimento: Direita > Frente > Esquerda > Trás (180º).
* **Relatórios de Execução:**
    * Monitoramento do número de passos e tempo de execução por labirinto.
    * Limite de segurança de 10.000 passos para evitar loops infinitos.

## 📂 Estrutura de Arquivos

* `main.py`: Arquivo principal. Carrega os mapas, instancia o agente e controla o loop de simulação.
* `agente_simples.py`: Módulo que contém a classe `AgenteReativoSimples` e a sua lógica de decisão.
* `labirinto *.txt`: Arquivos que representam os mapas, onde `1` representa paredes e `0` (ou outros números) representam caminhos livres.

## 🛠️ Como Executar

Certifique-se de ter o **Python 3** instalado.

1.  **Clone o repositório ou baixe os arquivos:**
    Mantenha o `main.py`, `agente_simples.py` e os arquivos `.txt` na mesma pasta.

2.  **Ative o ambiente virtual (opcional, mas recomendado):**
    * Linux/Mac: `source venv/bin/activate`
    * Windows: `.\venv\Scripts\activate`
    *(O projeto já inclui a estrutura de pastas para venv)*.

3.  **Execute o simulador:**
    ```bash
    python main.py
    ```

## 📊 Exemplo de Saída

O programa processará a lista de labirintos configurada e exibirá o resultado no terminal:

```text
=== RELATÓRIO DE EXECUÇÃO: AGENTE REATIVO SIMPLES (MODULARIZADO) ===

--- Processando: labirinto expiral.txt ---
Entrada: (0, 1) -> Saída: (10, 10)
RESULTADO: SUCESSO! (Passos: 152 | Tempo: 0.0042s)
