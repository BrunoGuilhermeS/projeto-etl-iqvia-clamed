import streamlit as st
from src.queries.queries import get_volume_com_dimensoes

st.set_page_config(page_title="Dashboard Clamed", layout="wide")

@st.cache_data(ttl=3600)
def carregar_dados():
    # Chama a função que agora não precisa de argumentos
    return get_volume_com_dimensoes()

st.title("📊 Volume e Dimensões")

with st.spinner('Buscando dados no banco...'):
    df = carregar_dados()

if df is not None and not df.empty:
    st.success(f"Sucesso! Foram carregadas {len(df)} linhas.")
    st.dataframe(df)
    st.line_chart(df) # Cuidado: se o df for muito grande, o gráfico pode ficar pesado
else:
    st.warning("Não há dados disponíveis ou ocorreu um erro na conexão.")