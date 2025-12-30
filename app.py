import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Caixa Virtual", layout="wide")

# Inicializar dados na memória se não existirem
if 'dados_caixa' not in st.session_state:
    st.session_state['dados_caixa'] = pd.DataFrame(columns=['data', 'tipo', 'cliente', 'descricao', 'valor', 'metodo'])
if 'dados_clientes' not in st.session_state:
    st.session_state['dados_clientes'] = pd.DataFrame(columns=['nome', 'telefone', 'anotacoes'])

# --- LOGIN ---
if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False
if not st.session_state['autenticado']:
    st.title("🔐 Login - Sistema Comercial")
    user = st.text_input("Usuário")
    pw = st.text_input("Senha", type="password")
    if st.button("Acessar Painel"):
        if user == "lojarosi" and pw == "lojinha123":
            st.session_state['autenticado'] = True
            st.rerun()
        else: st.error("Acesso Negado")
    st.stop()

# --- NAVEGAÇÃO ---
with st.sidebar:
    st.title("💎 Loja Digital")
    menu = st.radio("Navegação:", ["💰 Caixa", "👥 Clientes", "📊 Relatórios"])
    st.divider()
    
    # BOTÃO DE SEGURANÇA: Baixar tudo antes de fechar o site
    st.subheader("💾 Backup Diário")
    csv = st.session_state['dados_caixa'].to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Vendas (CSV)", csv, "vendas_dia.csv", "text/csv")
    
    if st.button("Sair"):
        st.session_state['autenticado'] = False
        st.rerun()

# --- ABA 1: CAIXA ---
if menu == "💰 Caixa":
    st.title("💰 Lançamentos de Caixa")
    
    with st.expander("➕ Nova Venda/Gasto", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            tipo = st.selectbox("Tipo", ["Entrada (Venda)", "Saída (Pagamento)"])
            cli = st.text_input("Nome do Cliente")
            val = st.number_input("Valor R$", min_value=0.0)
        with c2:
            met = st.selectbox("Forma", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"])
            desc = st.text_area("Descrição:")
        
        if st.button("✅ Registrar"):
            nova_venda = pd.DataFrame([{
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "tipo": tipo, "cliente": cli, "descricao": desc, "valor": val, "metodo": met
            }])
            st.session_state['dados_caixa'] = pd.concat([st.session_state['dados_caixa'], nova_venda], ignore_index=True)
            st.success("Registrado com sucesso!")

    st.subheader("Histórico do Dia")
    st.dataframe(st.session_state['dados_caixa'], use_container_width=True)

# --- ABA 2: CLIENTES ---
elif menu == "👥 Clientes":
    st.title("👥 Cadastro de Clientes")
    with st.form("novo_cli"):
        n = st.text_input("Nome")
        t = st.text_input("WhatsApp")
        o = st.text_area("Notas")
        if st.form_submit_button("Salvar Cliente"):
            novo_c = pd.DataFrame([{"nome": n, "telefone": t, "anotacoes": o}])
            st.session_state['dados_clientes'] = pd.concat([st.session_state['dados_clientes'], novo_c], ignore_index=True)
            st.success("Cliente salvo!")
    
    st.dataframe(st.session_state['dados_clientes'], use_container_width=True)

# --- ABA 3: RELATÓRIOS ---
elif menu == "📊 Relatórios":
    st.title("📊 Resumo Financeiro")
    df = st.session_state['dados_caixa']
    if not df.empty:
        vendas = df[df['tipo'] == "Entrada (Venda)"]['valor'].sum()
        gastos = df[df['tipo'] == "Saída (Pagamento)"]['valor'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Vendas", f"R$ {vendas:.2f}")
        c2.metric("Gastos", f"R$ {gastos:.2f}")
        c3.metric("Saldo", f"R$ {vendas-gastos:.2f}")
    else:
        st.info("Nenhuma venda registrada ainda.")






