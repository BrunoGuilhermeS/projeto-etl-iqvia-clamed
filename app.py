import streamlit as st

# Título da página
st.title("Meu primeiro App com Streamlit! 🚀")

# Texto simples
st.write("Olá, mundo! Este é um exemplo simples de como o Streamlit funciona.")

# Adicionando um widget (botão)
if st.button("Clique aqui para uma surpresa"):
    st.balloons()
    st.success("Você descobriu como o Streamlit é interativo!")