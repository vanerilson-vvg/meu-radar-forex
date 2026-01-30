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
        # Pega dados extras do mercado para a variação %
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

st.title("🛡️ RADAR DE ALTA PRECISÃO")
espaco = st.empty()

while True:
    df_5m, preco, fecho = buscar_dados("5m")
    df_15m, _, _ = buscar_dados("15m")
    
    s1 = calcular_status_estavel(df_5m)
    s2 = calcular_status_estavel(df_15m)
    
    with espaco.container():
        # Exibição do Preço e Variação % (Como no Yahoo)
        var_nom = preco - fecho
        var_per = (var_nom / fecho) * 100
        cor_var = "green" if var_nom >= 0 else "red"
        st.markdown(f"## {preco:.5f} <span style='color:{cor_var}; font-size: 0.6em;'>{var_nom:+.5f} ({var_per:+.2f}%)</span>", unsafe_allow_html=True)
        
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
        # CORREÇÃO DO ERRO: Adicionamos o key="botao_sinal"
        if s1 == s2 and s1 != 0:
            msg = "🚀 OPORTUNIDADE DE COMPRA" if s1 == 1 else "📉 OPORTUNIDADE DE VENDA"
            st.info(f"### {msg}") # Usando info em vez de button para evitar o erro de ID
        else:
            st.info("⌛ MERCADO SEM DIREÇÃO CLARA")
            
        st.caption(f"Última filtragem: {datetime.now().strftime('%H:%M:%S')}")
    
    time.sleep(10)
    
