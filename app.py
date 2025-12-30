import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Sistema Comercial Bianca", layout="wide")

# --- CONEXÃO DIRETA PELO ID ---
# O sistema vai pegar o ID que você salvou nos Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🔐 Login Administrativo")
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    if st.button("Acessar"):
        if u == "admin" and p == "loja20anos":
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("Acesso Negado")
    st.stop()

# --- LEITURA DOS DADOS ---
try:
    # ttl=0 garante que ele busque o dado MAIS NOVO do Google
    df_mov = conn.read(worksheet="movimentacoes", ttl=0)
    df_cli = conn.read(worksheet="clientes", ttl=0)
except Exception as e:
    st.error("O Google recusou a conexão. Verifique se a planilha está compartilhada como 'Qualquer pessoa com o link'!")
    st.stop()

# --- MENU ---
menu = st.sidebar.radio("Navegação:", ["💰 Fluxo de Caixa", "👥 Clientes"])

if menu == "💰 Fluxo de Caixa":
    st.header("💰 Gestão de Caixa")
    st.dataframe(df_mov, use_container_width=True)
    
    with st.expander("➕ Novo Lançamento"):
        val = st.number_input("Valor R$", min_value=0.0)
        desc = st.text_input("Descrição")
        if st.button("Salvar no Google"):
            nova_linha = pd.DataFrame([{"data": datetime.now().strftime("%d/%m/%Y"), "tipo": "Entrada", "valor": val, "descricao": desc}])
            df_atualizado = pd.concat([df_mov, nova_linha], ignore_index=True)
            conn.update(worksheet="movimentacoes", data=df_atualizado)
            st.success("Salvo com sucesso!")
            st.rerun()

elif menu == "👥 Clientes":
    st.header("👥 Seus Clientes")
    st.dataframe(df_cli, use_container_width=True)













