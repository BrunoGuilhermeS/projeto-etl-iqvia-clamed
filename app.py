import streamlit as st
import pandas as pd
import plotly.express as px
from src.queries.queries import get_volume_com_dimensoes as fetch_data

# 1. Configurações da Página
st.set_page_config(page_title="Dashboard Executivo Clamed", layout="wide")

@st.cache_data(ttl=60)
def carregar_dados():
    df = fetch_data()
    df['periodo'] = pd.to_datetime(df['periodo'])
    df['mes_str'] = df['periodo'].dt.strftime('%Y-%m')
    
    # Criamos colunas auxiliares para facilitar os cálculos
    # Vendas PP (Clamed)
    df['vendas_pp'] = df.apply(lambda x: x['volume_venda'] if x['tipo_bandeira'] == 'PP' else 0, axis=1)
    # Vendas Concorrência (Tudo que não é PP)
    df['vendas_concorrência'] = df.apply(lambda x: x['volume_venda'] if x['tipo_bandeira'] != 'PP' else 0, axis=1)
    
    return df

df = carregar_dados()

# --- SIDEBAR: Filtros Dinâmicos ---
st.sidebar.header("⚙️ Filtros do Dashboard")

# Filtro por Categoria (Nota: Se sua query usar 'categoria' para Região, 
# você pode precisar adicionar a categoria real do produto no SQL depois)
lista_cat = sorted(df['categoria'].unique().tolist())
filtro_cat = st.sidebar.multiselect("Categoria de Produto/Região:", lista_cat, default=lista_cat)

# Filtro por Brick (Bandeira)
lista_brick = sorted(df['brick'].unique().tolist())
filtro_brick = st.sidebar.multiselect("Selecione o Brick:", lista_brick, default=lista_brick)

# Filtro por Mês
lista_mes = sorted(df['mes_str'].unique().tolist(), reverse=True)
filtro_mes = st.sidebar.multiselect("Período (Mês):", lista_mes, default=lista_mes[:6]) # Padrão últimos 6 meses

# Aplicação dos Filtros
df_filtrado = df[
    (df['categoria'].isin(filtro_cat)) &
    (df['brick'].isin(filtro_brick)) &
    (df['mes_str'].isin(filtro_mes))
]

# --- PAINEL PRINCIPAL ---
st.title("📊 Dashboard de Performance Clamed")

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
else:
    # --- CÁLCULOS DOS KPIs ---
    
    # 1. Market Share PP
    vol_total = df_filtrado['volume_venda'].sum()
    vol_pp = df_filtrado['vendas_pp'].sum()
    share_pp = (vol_pp / vol_total * 100) if vol_total > 0 else 0
    
    # 2. Gap de Preço Médio
    vol_medio_pp = df_filtrado[df_filtrado['tipo_bandeira'] == 'PP']['volume_venda'].mean()
    vol_medio_conv = df_filtrado[df_filtrado['tipo_bandeira'] != 'PP']['volume_venda'].mean()
    
    # Ajuste o cálculo abaixo conforme sua necessidade de negócio
    gap_vol = vol_medio_pp - vol_medio_conv
    # ---------------------------------------------------------

    # 3. Brick Potencial
    brick_potencial = df_filtrado.groupby('brick')['volume_venda'].sum().idxmax()

    # Exibição (Aqui você usa as variáveis calculadas acima)
    c1, c2, c3 = st.columns(3)
    c1.metric("Market Share (PP)", f"{share_pp:.1f}%")
    c2.metric("Gap de Volume Médio", f"{gap_vol:.2f}") # O valor muda aqui
    c3.metric("Brick Potencial", brick_potencial)

    st.markdown("---")

    # --- VISÕES OBRIGATÓRIAS ---
    col_v1, col_v2 = st.columns([2, 3]) # Diferentes larguras para melhor estética

    with col_v1:
        st.subheader("📍 Volume de Vendas por Brick")
        # Treemap: Tamanho do quadrado é o volume total
        df_tree = df_filtrado.groupby('brick')['volume_venda'].sum().reset_index()
        fig_tree = px.treemap(df_tree, path=['brick'], values='volume_venda',
                             color='volume_venda', color_continuous_scale='RdBu')
        st.plotly_chart(fig_tree, use_container_width=True)

    with col_v2:
        st.subheader("📈 Evolução: PP vs Concorrência")
        # Agrupamos por mês para ver a linha do tempo
        df_evolucao = df_filtrado.groupby('mes_str')[['vendas_pp', 'vendas_concorrência']].sum().reset_index()
        # Ordenar meses cronologicamente
        df_evolucao = df_evolucao.sort_values('mes_str')
        
        fig_line = px.line(df_evolucao, x='mes_str', 
                           y=['vendas_pp', 'vendas_concorrência'],
                           labels={'value': 'Volume de Vendas', 'mes_str': 'Mês'},
                           markers=True,
                           color_discrete_map={'vendas_pp': '#00CC96', 'vendas_concorrência': '#EF553B'})
        
        st.plotly_chart(fig_line, use_container_width=True)