import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

# Configurações do Site
st.set_page_config(page_title="Radar Forex VVG", layout="wide")

def buscar_dados(intervalo):
    # Usamos um link que foca no dado mais recente possível
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?interval={intervalo}&range=1d"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=3)
        r = res.json()['chart']['result'][0]
        df = pd.DataFrame(r['indicators']['quote'][0])
        return df.dropna()
    except: return None

def calcular_status(df):
    if df is None or len(df) < 20: return None
    c = df['close']
    ema9 = c.ewm(span=9).mean().iloc[-1]
    ema21 = c.ewm(span=21).mean().iloc[-1]
    return 1 if c.iloc[-1] > ema9 and c.iloc[-1] > ema21 else -1

st.title("📈 RADAR TURBO - EUR/USD")
espaco = st.empty()

# Loop de atualização ultra rápida
while True:
    dados_recentes = buscar_dados("1m")
    sinal_1m = calcular_status(dados_recentes)
    sinal_5m = calcular_status(buscar_dados("5m"))
    
    if dados_recentes is not None:
        preco = dados_recentes['close'].iloc[-1]
        
        with espaco.container():
            st.subheader(f"Preço Atual (2s): {preco:.5f}")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### 1 MINUTO")
                if sinal_1m == 1: st.success("🟢 COMPRA")
                else: st.error("🔴 VENDA")
                
            with col2:
                st.write("### 5 MINUTOS")
                if sinal_5m == 1: st.success("🟢 COMPRA")
                else: st.error("🔴 VENDA")
            
            st.markdown("---")
            if sinal_1m == sinal_5m:
                st.warning("🔥 CONFLUÊNCIA DETECTADA!")
            else:
                st.info("⚠️ AGUARDAR - DIVERGÊNCIA")
                
            st.caption(f"Sincronizado às: {datetime.now().strftime('%H:%M:%S')}")
    
    # Reduzido para 2 segundos conforme solicitado
    time.sleep(2) 
                    
