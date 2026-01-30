import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

# Configurações do Site
st.set_page_config(page_title="Radar Turbo VVG", layout="wide")

def buscar_dados_completos():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?interval=1m&range=1d"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        r = res.json()['chart']['result'][0]
        df = pd.DataFrame(r['indicators']['quote'][0])
        meta = r['meta']
        
        # Cálculos de Variação (conforme a imagem do Yahoo Finance)
        preco_atual = meta['regularMarketPrice']
        preco_fechamento_ontem = meta['previousClose']
        variacao_nominal = preco_atual - preco_fechamento_ontem
        variacao_percentual = (variacao_nominal / preco_fechamento_ontem) * 100
        
        return df.dropna(), preco_atual, variacao_nominal, variacao_percentual
    except: return None, 0, 0, 0

def calcular_status(df):
    if df is None or len(df) < 20: return None
    c = df['close']
    ema9 = c.ewm(span=9).mean().iloc[-1]
    ema21 = c.ewm(span=21).mean().iloc[-1]
    return 1 if c.iloc[-1] > ema9 and c.iloc[-1] > ema21 else -1

st.title("📈 RADAR PROFISSIONAL - EUR/USD")
espaco = st.empty()

while True:
    df_1m, preco, var_nom, var_per = buscar_dados_completos()
    sinal_1m = calcular_status(df_1m)
    
    # Busca 5M separadamente para o status
    res_5m = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?interval=5m&range=1d", headers={'User-Agent': 'Mozilla/5.0'}).json()
    df_5m = pd.DataFrame(res_5m['chart']['result'][0]['indicators']['quote'][0]).dropna()
    sinal_5m = calcular_status(df_5m)
    
    with espaco.container():
        # EXIBIÇÃO DOS NÚMEROS DIÁRIOS (O QUE VOCÊ PEDIU)
        cor = "red" if var_nom < 0 else "green"
        st.markdown(f"### Preço: {preco:.5f} <span style='color:{cor}; font-size: 0.8em;'> {var_nom:+.5f} ({var_per:+.2f}%)</span>", unsafe_allow_html=True)
        
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
            
        st.caption(f"Sincronizado: {datetime.now().strftime('%H:%M:%S')}")
    
    time.sleep(2) # Mantive os 2 segundos de turbo
                
