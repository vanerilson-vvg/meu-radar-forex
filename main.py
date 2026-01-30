import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

# Configuração da página
st.set_page_config(page_title="Radar VVG Pro", layout="wide")

def buscar_dados(intervalo):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?interval={intervalo}&range=1d"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        r = res.json()['chart']['result'][0]
        df = pd.DataFrame(r['indicators']['quote'][0])
        meta = r['meta']
        return df.dropna(), meta['regularMarketPrice'], meta['previousClose']
    except: return None, 0, 0

def calcular_status_estavel(df):
    if df is None or len(df) < 30: return 0
    c = df['close']
    ema_curta = c.ewm(span=20).mean().iloc[-1]
    ema_longa = c.ewm(span=50).mean().iloc[-1]
    if c.iloc[-1] > ema_curta and ema_curta > ema_longa: return 1
    if c.iloc[-1] < ema_curta and ema_curta < ema_longa: return -1
    return 0

# --- CRIAÇÃO DOS ESPAÇOS FIXOS (FORA DO LOOP) ---
st.title("🛡️ RADAR DE ALTA PRECISÃO")
container_preco = st.empty()
col1, col2 = st.columns(2)
espaco_5m = col1.empty()
espaco_15m = col2.empty()
container_aviso = st.empty()
container_tempo = st.empty()

# --- LOOP DE ATUALIZAÇÃO ---
while True:
    df_5m, preco, fecho = buscar_dados("5m")
    df_15m, _, _ = buscar_dados("15m")
    s1 = calcular_status_estavel(df_5m)
    s2 = calcular_status_estavel(df_15m)
    
    # 1. Atualiza Preço e Variação Diária
    var_nom = preco - fecho
    var_per = (var_nom / fecho) * 100
    cor_var = "green" if var_nom >= 0 else "red"
    container_preco.markdown(f"## {preco:.5f} <span style='color:{cor_var}; font-size: 0.6em;'>{var_nom:+.5f} ({var_per:+.2f}%)</span>", unsafe_allow_html=True)
    
    # 2. Atualiza Tendência 5M
    with espaco_5m.container():
        st.write("### TENDÊNCIA 5M")
        if s1 == 1: st.success("ALTA")
        elif s1 == -1: st.error("BAIXA")
        else: st.warning("NEUTRO")
        
    # 3. Atualiza Tendência 15M
    with espaco_15m.container():
        st.write("### TENDÊNCIA 15M")
        if s2 == 1: st.success("ALTA")
        elif s2 == -1: st.error("BAIXA")
        else: st.warning("NEUTRO")
        
    # 4. Atualiza Aviso de Oportunidade
    with container_aviso.container():
        st.markdown("---")
        if s1 == s2 and s1 != 0:
            tipo = "OPORTUNIDADE DE COMPRA 🚀" if s1 == 1 else "OPORTUNIDADE DE VENDA 📉"
            st.info(f"## {tipo}")
        else:
            st.info("## ⌛ AGUARDANDO CONFLUÊNCIA")
            
    container_tempo.caption(f"Última filtragem: {datetime.now().strftime('%H:%M:%S')}")
    
    time.sleep(10)
    
