import random
import time
import requests
from datetime import datetime

TENSAO_VOLTS = 127
FATOR_POTENCIA = 0.92
API_URL = "https://lumina-project-r8xx.onrender.com/"

def gerar_e_enviar_leitura():
    if random.random() < 0.8:
        corrente = round(random.uniform(0.5, 3.5), 2)
    else:
        corrente = round(random.uniform(8.0, 22.0), 2)

    potencia = round(TENSAO_VOLTS * corrente * FATOR_POTENCIA, 2)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "timestamp": timestamp,
        "tensao_v": TENSAO_VOLTS,
        "corrente_a": corrente,
        "potencia_w": potencia
    }

    try:
        resposta = requests.post(API_URL, json=payload)
        if resposta.status_code == 200:
            print(f"[{timestamp}] ✅ Salvo no Banco! 🔌 Corrente: {corrente} A | 💡 Potência: {potencia} W")
        else:
            print(f"[{timestamp}] ⚠️ Erro na API: Status {resposta.status_code}")
    except Exception as e:
        print(f"[{timestamp}] ❌ Falha ao conectar na API. Certifique-se que api.py está rodando.")

if __name__ == "__main__":
    print("⚡ [Lumina] Simulador conectado à API em execução...")
    print("Pressione Ctrl + C para encerrar.\n")
    try:
        while True:
            gerar_e_enviar_leitura()
            time.sleep(3)
    except KeyboardInterrupt:
        print("\nSimulador parado.")
