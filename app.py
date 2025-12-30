import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="ERP Loja de Grife", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS (SEM LINK NO CÓDIGO) ---
# O sistema vai buscar o link automaticamente lá nos Secrets que você salvou.
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🔐 Login Administrativo")
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if u == "admin" and p == "loja20anos":
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("Acesso Negado")
    st.stop()

# --- CARREGAMENTO DE DADOS ---
# Note que aqui NÃO usamos o 'spreadsheet=url', apenas o nome da aba.
try:
    df_mov = conn.read(worksheet="movimentacoes", ttl="0")
    df_cli = conn.read(worksheet="clientes", ttl="0")
except Exception as e:
    st.error(f"Erro de Conexão: O sistema não encontrou as abas. Verifique se o nome é 'movimentacoes' (sem espaço).")
    st.stop()

# --- MENU LATERAL ---
with st.sidebar:
    st.title("💎 Loja Digital")
    menu = st.radio("Navegação:", ["💰 Caixa", "👗 Condicionais", "👥 Clientes"])
    st.divider()
    if st.button("Sair"):
        st.session_state['auth'] = False
        st.rerun()

# --- ABA CAIXA ---
if menu == "💰 Caixa":
    st.header("💰 Lançamentos de Caixa")
    
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            tipo = st.selectbox("Tipo", ["Entrada (Venda)", "Saída (Gasto)"])
            cliente_v = st.selectbox("Cliente", ["Consumidor Geral"] + df_cli['nome'].tolist())
            valor = st.number_input("Valor R$", min_value=0.0, step=0.01)
        with c2:
            metodo = st.selectbox("Forma", ["Pix", "Dinheiro", "Cartão Crédito", "Cartão Débito"])
            parc = st.number_input("Parcelas", 1, 12, 1) if "Crédito" in metodo else 1
            desc = st.text_area("Descrição das Peças")
        
        if st.button("✅ Salvar no Google Sheets"):
            nova_linha = pd.DataFrame([{
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "tipo": tipo, "cliente": cliente_v, "descricao": desc,
                "valor": valor, "metodo": metodo, "parcelas": parc
            }])
            # Atualizando a planilha
            df_atualizado = pd.concat([df_mov, nova_linha], ignore_index=True)
            conn.update(worksheet="movimentacoes", data=df_atualizado)
            st.success("Dados enviados para a planilha com sucesso!")
            st.rerun()

    st.subheader("📋 Histórico no Drive")
    st.dataframe(df_mov, use_container_width=True)

# --- ABA CLIENTES ---
elif menu == "👥 Clientes":
    st.header("👥 Cadastro de Clientes")
    with st.form("f_cli"):
        n = st.text_input("Nome")
        t = st.text_input("WhatsApp")
        o = st.text_area("Notas")
        if st.form_submit_button("Salvar Cliente"):
            novo_c = pd.DataFrame([{"nome": n, "telefone": t, "anotacoes": o}])
            df_cli_at = pd.concat([df_cli, novo_c], ignore_index=True)
            conn.update(worksheet="clientes", data=df_cli_at)
            st.success("Cliente salvo no Drive!")
            st.rerun()
    st.dataframe(df_cli, use_container_width=True)












