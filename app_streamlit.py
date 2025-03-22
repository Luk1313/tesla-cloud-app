import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from datetime import timedelta

st.set_page_config(layout="wide", page_title="TSLA - Análisis en la Nube")

st.title("📈 Tesla Inc. (TSLA) - Dashboard Automático")

# Leer datos desde archivo CSV interno
df = pd.read_csv("datos_tesla.csv") 
df.columns = df.columns.str.strip().str.lower()
df = df.rename(columns={'último': 'cierre', 'vol.': 'volumen'})
df['fecha'] = pd.to_datetime(df['fecha'])
df = df.dropna(subset=['fecha']).sort_values('fecha')

# Calcular indicadores
df['SMA_20'] = df['cierre'].rolling(window=20).mean()
df['SMA_50'] = df['cierre'].rolling(window=50).mean()
df['EMA_12'] = df['cierre'].ewm(span=12, adjust=False).mean()
df['EMA_26'] = df['cierre'].ewm(span=26, adjust=False).mean()
df['MACD'] = df['EMA_12'] - df['EMA_26']
df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
df['MACD_Hist'] = df['MACD'] - df['Signal']

delta = df['cierre'].diff()
gain = np.where(delta > 0, delta, 0)
loss = np.where(delta < 0, -delta, 0)
avg_gain = pd.Series(gain).rolling(window=14).mean()
avg_loss = pd.Series(loss).rolling(window=14).mean()
rs = avg_gain / avg_loss
df['RSI'] = 100 - (100 / (1 + rs))

df['BB_Middle'] = df['cierre'].rolling(window=20).mean()
df['BB_Std'] = df['cierre'].rolling(window=20).std()
df['BB_Upper'] = df['BB_Middle'] + 2 * df['BB_Std']
df['BB_Lower'] = df['BB_Middle'] - 2 * df['BB_Std']

# Visualización principal
fecha_fin = df['fecha'].max()
fecha_ini = fecha_fin - timedelta(days=180)
df_vis = df[(df['fecha'] >= fecha_ini)]

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_vis['fecha'], y=df_vis['cierre'], name='Cierre', line=dict(color='royalblue')))
fig.add_trace(go.Scatter(x=df_vis['fecha'], y=df_vis['SMA_20'], name='SMA 20', line=dict(color='orange')))
fig.add_trace(go.Scatter(x=df_vis['fecha'], y=df_vis['SMA_50'], name='SMA 50', line=dict(color='purple')))
fig.add_trace(go.Scatter(x=df_vis['fecha'], y=df_vis['BB_Upper'], name='BB Sup', line=dict(color='lightblue', dash='dot')))
fig.add_trace(go.Scatter(x=df_vis['fecha'], y=df_vis['BB_Lower'], name='BB Inf', line=dict(color='lightblue', dash='dot')))
fig.update_layout(title="Gráfico de Precio", height=600, template="plotly_white", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

fig_macd = go.Figure()
fig_macd.add_trace(go.Scatter(x=df_vis['fecha'], y=df_vis['MACD'], name='MACD', line=dict(color='darkcyan')))
fig_macd.add_trace(go.Scatter(x=df_vis['fecha'], y=df_vis['Signal'], name='Signal', line=dict(color='orange')))
fig_macd.add_trace(go.Bar(x=df_vis['fecha'], y=df_vis['MACD_Hist'], name='Histograma',
                          marker_color=np.where(df_vis['MACD_Hist'] >= 0, 'green', 'red')))
fig_macd.update_layout(title="MACD", height=300, template="plotly_white")
st.plotly_chart(fig_macd, use_container_width=True)

fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=df_vis['fecha'], y=df_vis['RSI'], name='RSI', line=dict(color='blue')))
fig_rsi.add_shape(type='line', x0=df_vis['fecha'].min(), x1=df_vis['fecha'].max(), y0=70, y1=70, line=dict(color='red', dash='dash'))
fig_rsi.add_shape(type='line', x0=df_vis['fecha'].min(), x1=df_vis['fecha'].max(), y0=30, y1=30, line=dict(color='green', dash='dash'))
fig_rsi.update_layout(title="RSI", height=300, template="plotly_white")
st.plotly_chart(fig_rsi, use_container_width=True)
