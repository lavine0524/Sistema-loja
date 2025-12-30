import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="ERP Loja de Grife - Cloud", layout="wide")

# --- LOGIN ---
if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False
if not st.session_state['autenticado']:
    st.title("🔐 Login - Sistema Comercial")
    user = st.text_input("Usuário")
    pw = st.text_input("Senha", type="password")
    if st.button("Acessar Painel"):
        if user == "admin" and pw == "loja20anos":
            st.session_state['autenticado'] = True
            st.rerun()
        else: st.error("Acesso Negado")
    st.stop()

# --- CONEXÃO COM GOOGLE SHEETS ---
url = "https://docs.google.com/spreadsheets/d/1bj24FG-Qe5mZmEPLjlnav1uuN4v-o43atSE1Pz0zzt0/export?format=csv"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAVEGAÇÃO ---
with st.sidebar:
    st.title("💎 Loja Digital")
    menu = st.radio("Navegação:", ["💰 Caixa", "👥 Clientes", "📊 Relatórios"])
    if st.button("Sair"):
        st.session_state['autenticado'] = False
        st.rerun()

# --- ABA 1: CAIXA ---
if menu == "💰 Caixa":
    st.title("💰 Lançamentos de Caixa")
    
    # Carregar dados existentes
    df_mov = conn.read(spreadsheet=url, worksheet="movimentacoes")
    
    with st.expander("➕ Nova Venda/Gasto", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            tipo = st.selectbox("Tipo", ["Entrada (Venda)", "Saída (Pagamento)"])
            cliente = st.text_input("Nome do Cliente")
            valor = st.number_input("Valor R$", min_value=0.0)
        with c2:
            metodo = st.selectbox("Forma", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"])
            desc = st.text_area("Descrição das Peças:")
        
        if st.button("✅ Salvar na Planilha"):
            nova_linha = pd.DataFrame([{
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "tipo": tipo,
                "cliente": cliente,
                "descricao": desc,
                "valor": valor,
                "metodo": metodo,
                "parcelas": 1
            }])
            df_final = pd.concat([df_mov, nova_linha], ignore_index=True)
            conn.update(spreadsheet=url, worksheet="movimentacoes", data=df_final)
            st.success("Dados enviados para o Google Sheets!")
            st.rerun()

    st.subheader("Histórico Recente (Direto do Google)")
    st.dataframe(df_mov.tail(10), use_container_width=True)

# --- ABA 2: CLIENTES ---
elif menu == "👥 Clientes":
    st.title("👥 Cadastro de Clientes")
    df_cli = conn.read(spreadsheet=url, worksheet="clientes")
    
    with st.form("novo_cli"):
        nome = st.text_input("Nome")
        tel = st.text_input("WhatsApp")
        obs = st.text_area("Notas")
        if st.form_submit_button("Salvar Cliente"):
            novo_c = pd.DataFrame([{"nome": nome, "telefone": tel, "anotacoes": obs}])
            df_f = pd.concat([df_cli, novo_c], ignore_index=True)
            conn.update(spreadsheet=url, worksheet="clientes", data=df_f)
            st.success("Cliente salvo!")
            st.rerun()
    
    st.dataframe(df_cli, use_container_width=True)

# --- ABA 3: RELATÓRIOS ---
elif menu == "📊 Relatórios":
    st.title("📊 Resumo Financeiro")
    df_mov = conn.read(spreadsheet=url, worksheet="movimentacoes")
    if not df_mov.empty:
        total_vendas = df_mov[df_mov['tipo'] == "Entrada (Venda)"]['valor'].sum()
        st.metric("Total de Vendas Acumulado", f"R$ {total_vendas:.2f}")
        st.line_chart(df_mov.set_index('data')['valor'])

