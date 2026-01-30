import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

st.set_page_config(page_title="Radar Estável VVG", layout="wide")

def buscar_dados(intervalo):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?interval={intervalo}&range=1d"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        r = res.json()['chart']['result'][0]
        df = pd.DataFrame(r['indicators']['quote'][0])
        return df.dropna()
    except: return None

def calcular_status_estavel(df):
    if df is None or len(df) < 30: return 0
    c = df['close']
    # Médias mais longas para evitar mudanças frenéticas
    ema_curta = c.ewm(span=20).mean().iloc[-1]
    ema_longa = c.ewm(span=50).mean().iloc[-1]
    
    if c.iloc[-1] > ema_curta and ema_curta > ema_longa: return 1 # Compra Forte
    if c.iloc[-1] < ema_curta and ema_curta < ema_longa: return -1 # Venda Forte
    return 0 # Neutro (Aguardar)

st.title("🛡️ RADAR DE ALTA PRECISÃO - EUR/USD")
espaco = st.empty()

while True:
    df_5m = buscar_dados("5m")
    df_15m = buscar_dados("15m") # Mudamos para 15M para filtrar o ruído
    
    s1 = calcular_status_estavel(df_5m)
    s2 = calcular_status_estavel(df_15m)
    
    with espaco.container():
        if df_5m is not None:
            st.subheader(f"Preço Atual: {df_5m['close'].iloc[-1]:.5f}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("### TENDÊNCIA 5M")
            if s1 == 1: st.success("🟢 ALTA")
            elif s1 == -1: st.error("🔴 BAIXA")
            else: st.warning("🟡 NEUTRO")
            
        with col2:
            st.write("### TENDÊNCIA 15M")
            if s2 == 1: st.success("🟢 ALTA")
            elif s2 == -1: st.error("🔴 BAIXA")
            else: st.warning("🟡 NEUTRO")
            
        st.markdown("---")
        # Só dá o sinal se 5M e 15M estiverem idênticos e fortes
        if s1 == s2 and s1 != 0:
            msg = "🚀 OPORTUNIDADE DE COMPRA" if s1 == 1 else "📉 OPORTUNIDADE DE VENDA"
            st.button(msg, use_container_width=True)
        else:
            st.info("⌛ MERCADO SEM DIREÇÃO CLARA - NÃO OPERE")
            
        st.caption(f"Dados filtrados às: {datetime.now().strftime('%H:%M:%S')}")
    
    time.sleep(10) # Aumentamos para 10s para você ter tempo de pensar
        
