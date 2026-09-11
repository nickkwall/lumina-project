from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import uvicorn

app = FastAPI(title="Lumina API - ODS 7")

# Inicializa o banco de dados SQLite local
def init_db():
    conn = sqlite3.connect("lumina.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leituras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            tensao_v REAL,
            corrente_a REAL,
            potencia_w REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Estrutura esperada dos dados de entrada
class MedicaoSchema(BaseModel):
    timestamp: str
    tensao_v: float
    corrente_a: float
    potencia_w: float

# Endpoint POST para receber leituras (simulador ou ESP32)
@app.post("/api/medicao")
def receber_medicao(medicao: MedicaoSchema):
    conn = sqlite3.connect("lumina.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO leituras (timestamp, tensao_v, corrente_a, potencia_w)
        VALUES (?, ?, ?, ?)
    ''', (medicao.timestamp, medicao.tensao_v, medicao.corrente_a, medicao.potencia_w))
    conn.commit()
    conn.close()
    return {"status": "sucesso", "mensagem": "Leitura registrada com sucesso!"}

# Endpoint GET para o Dashboard ler os dados históricos
@app.get("/api/historico")
def obter_historico(limite: int = 50):
    conn = sqlite3.connect("lumina.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, timestamp, tensao_v, corrente_a, potencia_w FROM leituras ORDER BY id DESC LIMIT ?", 
        (limite,)
    )
    rows = cursor.fetchall()
    conn.close()

    resultado = [
        {
            "id": r[0],
            "timestamp": r[1],
            "tensao_v": r[2],
            "corrente_a": r[3],
            "potencia_w": r[4]
        }
        for r in rows
    ]
    return resultado

if __name__ == "__main__":
    print("🚀 API Lumina iniciada em http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)