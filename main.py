import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

# Configurações do Site
st.set_page_config(page_title="Radar Forex VVG", layout="wide")

def buscar_dados(intervalo):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?interval={intervalo}&range=1d"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        r = res.json()['chart']['result'][0]
        df = pd.DataFrame(r['indicators']['quote'][0])
        df['high'] = r['indicators']['quote'][0]['high']
        df['low'] = r['indicators']['quote'][0]['low']
        return df.dropna()
    except: return None

def calcular_status(df):
    if df is None or len(df) < 30: return None
    c = df['close']
    ema9 = c.ewm(span=9).mean().iloc[-1]
    ema21 = c.ewm(span=21).mean().iloc[-1]
    
    score = 0
    score += 1 if c.iloc[-1] > ema9 else -1
    score += 1 if c.iloc[-1] > ema21 else -1
    
    return {"preco": c.iloc[-1], "score": score}

st.title("📈 MEU RADAR FOREX - EUR/USD")
espaco = st.empty()

while True:
    d1 = calcular_status(buscar_dados("1m"))
    d5 = calcular_status(buscar_dados("5m"))
    
    if d1 and d5:
        with espaco.container():
            st.subheader(f"Preço Atual: {d1['preco']:.5f}")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### TEMPO 1M")
                if d1['score'] > 0: st.success("🟢 COMPRA")
                else: st.error("🔴 VENDA")
                
            with col2:
                st.write("### TEMPO 5M")
                if d5['score'] > 0: st.success("🟢 COMPRA")
                else: st.error("🔴 VENDA")
                
            if d1['score'] == d5['score']:
                st.warning(f"🔥 CONFLUÊNCIA DETECTADA!")
            st.caption(f"Atualizado em: {datetime.now().strftime('%H:%M:%S')}")
    
    time.sleep(10)
