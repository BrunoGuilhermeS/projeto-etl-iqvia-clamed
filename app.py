import streamlit as st
import pandas as pd
import plotly.express as px
from src.queries.queries import get_volume_com_dimensoes as fetch_data

# 1. Configurações da Página
st.set_page_config(page_title="Dashboard Executivo Clamed", layout="wide")

@st.cache_data(ttl=60)
def carregar_dados():
    df = fetch_data()
    
    # Garantimos que o período seja datetime e criamos a string de mês
    df['periodo'] = pd.to_datetime(df['periodo'])
    df['mes_str'] = df['periodo'].dt.strftime('%Y-%m')
    
    # Criamos o identificador único para os produtos (evita agrupar "Sem Nome")
    # Se 'nome_produto' ou 'ean_produto' não existirem, tratamos para não quebrar
    if 'nome_produto' in df.columns and 'ean_produto' in df.columns:
        df['produto_label'] = df['nome_produto'].astype(str) + " (" + df['ean_produto'].astype(str) + ")"
    else:
        df['produto_label'] = "SKU " + df['sk_produto'].astype(str)

    # Cálculos de colunas de apoio (Vendas PP vs Concorrência)
    df['vendas_pp'] = df.apply(lambda x: x['volume_venda'] if x['tipo_bandeira'] == 'PP' else 0, axis=1)
    df['vendas_concorrência'] = df.apply(lambda x: x['volume_venda'] if x['tipo_bandeira'] != 'PP' else 0, axis=1)
    
    return df

df = carregar_dados()

# --- SIDEBAR: Filtros Dinâmicos ---
st.sidebar.header("⚙️ Filtros do Dashboard")

# 1. Filtro por Região
lista_regiao = sorted(df['regiao'].unique().tolist())
filtro_regiao = st.sidebar.multiselect("Selecione a Região:", lista_regiao, default=lista_regiao)

# 2. Filtro por Bandeira
lista_bandeira = sorted(df['bandeira'].unique().tolist())
filtro_bandeira = st.sidebar.multiselect("Selecione a Bandeira:", lista_bandeira, default=lista_bandeira)

# 3. Filtro por Produto (Usando o Label Único)
lista_produto = sorted(df['produto_label'].unique().tolist())
filtro_produto = st.sidebar.multiselect("Produto (EAN):", lista_produto)

# 4. Filtro por Mês
lista_mes = sorted(df['mes_str'].unique().tolist(), reverse=True)
filtro_mes = st.sidebar.multiselect("Período (Mês):", lista_mes, default=lista_mes[:6])

# --- APLICAÇÃO DOS FILTROS ---
mascara = (
    (df['regiao'].isin(filtro_regiao)) &
    (df['bandeira'].isin(filtro_bandeira)) &
    (df['mes_str'].isin(filtro_mes))
)

# Filtro de produto só aplica se algo for selecionado
if filtro_produto:
    mascara = mascara & (df['produto_label'].isin(filtro_produto))

df_filtrado = df[mascara]

# --- ESTILIZAÇÃO CSS ---
cor_barra_verde = "#2D724F"
cor_texto_branco = "#FFFFFF"

st.markdown(f"""
<style>
    .title-bar {{
        background-color: {cor_barra_verde};
        color: {cor_texto_branco};
        padding: 1.5rem;
        margin-top: -3.5rem;
        margin-left: -1rem; 
        margin-right: -1rem;
        border-radius: 0.5rem;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    }}
    .title-bar h1 {{ font-size: 2.2rem; color: white !important; display: inline; }}
    
    /* Estilo das Métricas */
    [data-testid="stMetric"] {{
        background-color: #e6fffa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #b2f5ea;
    }}

    /* Tags dos Filtros em VERDE */
    span[data-baseweb="tag"] {{
        background-color: {cor_barra_verde} !important;
        color: white !important;
    }}
    span[data-baseweb="tag"] svg {{ fill: white !important; }}
</style>

<div class="title-bar">
    <span>📊</span><h1>Dashboard Executivo Clamed</h1>
</div>
<br>
""", unsafe_allow_html=True)

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
else:
    # --- KPIs ---
    st.subheader("Indicadores de Desempenho")
    c1, c2, c3 = st.columns(3)
    
    vol_total = df_filtrado['volume_venda'].sum()
    vol_pp = df_filtrado['vendas_pp'].sum()
    share_pp = (vol_pp / vol_total * 100) if vol_total > 0 else 0
    
    vol_pp_serie = df_filtrado[df_filtrado['tipo_bandeira'] == 'PP']['volume_venda']
    vol_conv_serie = df_filtrado[df_filtrado['tipo_bandeira'] != 'PP']['volume_venda']
    
    vol_medio_pp = vol_pp_serie.median() if not vol_pp_serie.empty else 0
    vol_medio_conv = vol_conv_serie.median() if not vol_conv_serie.empty else 0
    
    gap_vol = vol_medio_pp - vol_medio_conv
    
    regiao_potencial = df_filtrado.groupby('regiao')['volume_venda'].sum().idxmax()

    c1.metric("Market Share (PP)", f"{share_pp:.1f}%")
    c2.metric("Gap de Volume Médio", f"{gap_vol:.2f}")
    c3.metric("Filial Potencial", regiao_potencial)

    st.divider()

    # --- GRID DE GRÁFICOS (LINHA 1) ---
    col_v1, col_v2 = st.columns([2, 3])

    with col_v1:
        st.subheader("📍 Performance por Bandeira")
        df_tree = df_filtrado.groupby('bandeira')['volume_venda'].sum().reset_index()
        fig_tree = px.treemap(df_tree, path=['bandeira'], values='volume_venda',
                               color='volume_venda', color_continuous_scale='Greens')
        st.plotly_chart(fig_tree, use_container_width=True)

    with col_v2:
        st.subheader("📈 Evolução: PP vs Mercado")
        df_evolucao = df_filtrado.groupby('mes_str')[['vendas_pp', 'vendas_concorrência']].sum().reset_index().sort_values('mes_str')
        fig_line = px.line(df_evolucao, x='mes_str', y=['vendas_pp', 'vendas_concorrência'],
                           markers=True, color_discrete_map={'vendas_pp': '#2D724F', 'vendas_concorrência': '#EF553B'})
        st.plotly_chart(fig_line, use_container_width=True)

    # --- GRID DE GRÁFICOS (LINHA 2) ---
    col_v3, col_v4 = st.columns(2)

    with col_v3:
        st.subheader("🗺️ Market Share por Região")
        df_share = df_filtrado.groupby(['regiao', 'tipo_bandeira'])['volume_venda'].sum().reset_index()
        
        # 1. Criamos o gráfico SEM o barnorm aqui dentro
        fig_share = px.bar(df_share, 
                           y='regiao', 
                           x='volume_venda', 
                           color='tipo_bandeira', 
                           orientation='h', 
                           barmode='relative',
                           color_discrete_map={'PP': '#2D724F', 'Concorrente': '#EF553B'},
                           labels={'volume_venda': 'Market Share (%)', 'regiao': 'Região'})
        
        # 2. Aplicamos a normalização para 100% no layout
        fig_share.update_layout(barnorm='percent')
        
        st.plotly_chart(fig_share, use_container_width=True)

    with col_v4:
        st.subheader("🏆 Top 10 Produtos (Volume PP)")
        # Aqui usamos o PRODUTO_LABEL para diferenciar os "Sem Nome"
        df_top = df_filtrado[df_filtrado['tipo_bandeira'] == 'PP'].groupby('produto_label')['volume_venda'].sum().nlargest(10).reset_index()
        fig_top = px.bar(df_top.sort_values('volume_venda'), x='volume_venda', y='produto_label', 
                         orientation='h', color_discrete_sequence=['#2D724F'])
        st.plotly_chart(fig_top, use_container_width=True)