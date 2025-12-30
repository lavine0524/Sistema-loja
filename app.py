import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Lojinha da Ro", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS ---
# Ele vai procurar o link nos "Secrets" que configuramos antes
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🔐 Login Administrativo")
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    if st.button("Acessar Sistema"):
        if u == "admin" and p == "lojinha123":
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("Acesso Negado")
    st.stop()

# --- CARREGAR DADOS ---
# Lendo as abas da sua planilha "Banco_dados_loja"
try:
    df_vendas = conn.read(worksheet="movimentacoes")
    df_clientes = conn.read(worksheet="clientes")
except:
    st.error("Erro ao ler a planilha. Verifique se as abas 'movimentacoes' e 'clientes' existem.")
    st.stop()

# --- MENU LATERAL ---
with st.sidebar:
    st.title("💎 Gestão de Grife")
    menu = st.radio("Menu:", ["💰 Fluxo de Caixa", "👗 Condicionais", "👥 Meus Clientes"])
    st.divider()
    if st.button("Sair"):
        st.session_state['auth'] = False
        st.rerun()

# --- FLUXO DE CAIXA ---
if menu == "💰 Fluxo de Caixa":
    st.header("💰 Registro de Vendas e Gastos")
    
    lista_clientes = ["Consumidor Geral"] + df_clientes['nome'].tolist()
    
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            tipo = st.selectbox("Operação", ["Entrada (Venda)", "Saída (Pagamento)"])
            cliente = st.selectbox("Selecione o Cliente", lista_clientes)
            valor = st.number_input("Valor R$", min_value=0.0, step=0.01)
        with c2:
            metodo = st.selectbox("Forma", ["Pix", "Dinheiro", "Cartão Crédito", "Cartão Débito"])
            parcelas = st.number_input("Parcelas", 1, 12, 1) if "Crédito" in metodo else 1
            desc = st.text_area("Descrição das Peças")
        
        if st.button("✅ Gravar na Planilha"):
            nova_venda = pd.DataFrame([{
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "tipo": tipo, "cliente": cliente, "descricao": desc,
                "valor": valor, "metodo": metodo, "parcelas": parcelas
            }])
            # Atualiza a planilha no Google Drive
            df_atualizado = pd.concat([df_vendas, nova_venda], ignore_index=True)
            conn.update(worksheet="movimentacoes", data=df_atualizado)
            st.success("Salvo com sucesso no Google Drive!")
            st.rerun()

    st.subheader("📋 Histórico (Direto do Drive)")
    st.dataframe(df_vendas, use_container_width=True)

# --- MEUS CLIENTES ---
elif menu == "👥 Meus Clientes":
    st.header("👥 Cadastro Eterno de Clientes")
    with st.form("novo_cli"):
        n = st.text_input("Nome Completo")
        t = st.text_input("WhatsApp")
        o = st.text_area("Observações")
        if st.form_submit_button("💾 Salvar Cliente"):
            novo_c = pd.DataFrame([{"nome": n, "telefone": t, "anotacoes": o}])
            df_cli_at = pd.concat([df_clientes, novo_c], ignore_index=True)
            conn.update(worksheet="clientes", data=df_cli_at)
            st.success("Cliente guardado para sempre!")
            st.rerun()
    
    st.dataframe(df_clientes, use_container_width=True)










