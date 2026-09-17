from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from datetime import datetime

app = FastAPI(title="Lumina API")

# 1. Liberar CORS (Essencial para o front-end carregar os dados)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite chamadas do Cloudflare Pages ou local
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de dados enviado pelo ESP2
class Leitura(BaseModel):
    corrente: float
    potencia: float

# Inicializar Banco de Dados SQLite
def init_db():
    conn = sqlite3.connect("lumina.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leituras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            corrente REAL,
            potencia REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ROTA 1: O ESP2 envia as leituras para cá (POST)
@app.post("/api/dados")
def receber_dados(leitura: Leitura):
    conn = sqlite3.connect("lumina.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO leituras (corrente, potencia) VALUES (?, ?)",
        (leitura.corrente, leitura.potencia)
    )
    conn.commit()
    conn.close()
    return {"status": "sucesso", "mensagem": "Dados gravados"}

# ROTA 2: O Dashboard em HTML/JS consulta os dados aqui (GET)
@app.get("/api/historico")
def obter_historico(limite: int = 20):
    conn = sqlite3.connect("lumina.db")
    cursor = conn.cursor()
    # Pega os últimos 'limite' registros ordenados pelo tempo
    cursor.execute(
        "SELECT corrente, potencia, timestamp FROM leituras ORDER BY id DESC LIMIT ?", 
        (limite,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    # Formata em JSON para o Chart.js ler facilmente
    dados = [
        {"corrente": row[0], "potencia": row[1], "timestamp": row[2]} 
        for row in reversed(rows)
    ]
    return dados
