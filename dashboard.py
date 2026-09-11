import requests
import pandas as pd
import streamlit as st
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Lumina - Conscientização Energética (ODS 7)",
    page_icon="💡",
    layout="wide"
)

# Título do Projeto
st.title("💡 Lumina — Monitoramento & Eficiência Energética")
st.caption("ODS 7: Garantir acesso à energia barata, confiável, sustentável e moderna para todos.")

# Parâmetros Elétricos e Ambientais
TARIFA_KWH = 0.85          # Valor médio do kWh em R$ (com impostos)
FATOR_EMISSAO_CO2 = 0.085  # kg de CO2 por kWh (Matriz Elétrica Brasileira)
API_URL = "https://lumina-project-r8xx.onrender.com/"

def carregar_dados():
    try:
        resposta = requests.get(API_URL, timeout=3)
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados:
                df = pd.DataFrame(dados)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                return df
    except Exception:
        pass
    return pd.DataFrame()

df = carregar_dados()

if df.empty:
    st.warning("⚠️ Não há dados no banco. Verifique se a API (`api.py`) e o simulador (`simulador.py`) estão rodando!")
    if st.button("🔄 Tentar Novamente"):
        st.rerun()
else:
    # Dados da última leitura
    ultima = df.iloc[-1]
    potencia_atual = ultima['potencia_w']
    corrente_atual = ultima['corrente_a']

    # Cálculos de Estimativa Mensal
    potencia_media_w = df['potencia_w'].mean()
    consumo_mensal_kwh = (potencia_media_w / 1000) * 24 * 30  # Projeção para 30 dias
    custo_mensal_estimado = consumo_mensal_kwh * TARIFA_KWH
    co2_mensal_estimado = consumo_mensal_kwh * FATOR_EMISSAO_CO2

    # --- CARTÕES DE MÉTRICAS (KPIs) ---
    st.subheader("📊 Métricas em Tempo Real")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Potência Instantânea", f"{potencia_atual:.1f} W")
    col2.metric("Corrente Atual", f"{corrente_atual:.2f} A")
    col3.metric("Fatura Mensal Estimada", f"R$ {custo_mensal_estimado:.2f}")
    col4.metric("Pegada de CO₂ Estimada", f"{co2_mensal_estimado:.2f} kg/mês")

    st.divider()

    # --- GRÁFICO E ÁREA DE CONSCIENTIZAÇÃO (ODS 7) ---
    col_grafico, col_ods = st.columns([2, 1])

    with col_grafico:
        st.subheader("📈 Histórico de Consumo (Watts)")
        fig = px.line(
            df, 
            x="timestamp", 
            y="potencia_w",
            labels={"timestamp": "Horário", "potencia_w": "Potência (W)"},
            markers=True
        )
        fig.update_traces(line_color="#e67e22")
        st.plotly_chart(fig, use_container_width=True)

    with col_ods:
        st.subheader("🌱 Painel ODS 7 - Conscientização")
        
        # Alerta de consumo dinâmico
        if potencia_atual > 1500:
            st.error("🚨 **Consumo Elevado!** Aparelho de alta potência em uso (ex: chuveiro, ferro). Reduzir o tempo de uso evita picos na conta!")
        elif potencia_atual > 500:
            st.warning("⚠️ **Consumo Moderado.** Atenção a aparelhos mantidos em modo standby.")
        else:
            st.success("✅ **Consumo Baixo.** A residência está operando dentro da faixa de eficiência energética.")

        st.markdown("---")
        st.markdown("### 💡 Dicas Práticas de Economia:")
        st.markdown("- Substitua lâmpadas incandescentes por **LED**.")
        st.markdown("- Aproveite a luz natural durante o dia.")
        st.markdown("- Desconecte carregadores e aparelhos sem uso da tomada.")

    # Botão para atualizar
    if st.button("🔄 Atualizar Dashboard"):
        st.rerun()
