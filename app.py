import streamlit as st
from src.queries.queries import get_volume_com_dimensoes

st.set_page_config(page_title="Dashboard Clamed", layout="wide")

# Decorador de cache para não rodar a consulta toda hora
@st.cache_data(ttl=3600) # Cache de 1 hora
def get_volume_com_dimensoes():
    try:
        # Chamada da sua função existente
        df = get_volume_com_dimensoes() 
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados do banco: {e}")
        return None

# --- Layout do App ---
st.title("📊 Volume e Dimensões")

# Spinner para mostrar que está carregando
with st.spinner('Buscando dados no banco...'):
    df = get_volume_com_dimensoes()

# Verificação de segurança
if df is not None and not df.empty:
    st.success("Dados carregados com sucesso!")
    
    # Exemplo de uso no Streamlit
    st.dataframe(df.head()) # Mostra uma tabela interativa
    
    # Exemplo de gráfico baseado no dataframe
    st.line_chart(df) 
else:
    st.warning("Não há dados disponíveis.")

@st.cache_data(ttl=3600)
def get_volume_com_dimensoes(data_inicial, data_final):
    return get_volume_com_dimensoes(data_inicial, data_final)

# No Streamlit:
inicio = st.date_input("Início")
fim = st.date_input("Fim")
df = get_volume_com_dimensoes(inicio, fim)