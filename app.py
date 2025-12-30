import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Lojinha da Ro", layout="wide")

# --- CSS PARA O LAYOUT PROFISSIONAL ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #007bff; color: white; }
    div[data-testid="metric-container"] {
        background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE DADOS (MEMÓRIA) ---
if 'vendas' not in st.session_state:
    st.session_state['vendas'] = pd.DataFrame(columns=['data', 'tipo', 'cliente', 'descricao', 'valor', 'metodo'])
if 'clientes' not in st.session_state:
    st.session_state['clientes'] = pd.DataFrame(columns=['nome', 'telefone', 'anotacoes'])
if 'condicionais' not in st.session_state:
    st.session_state['condicionais'] = pd.DataFrame(columns=['id', 'cliente', 'itens', 'status'])

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🔐 Acesso Administrativo")
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    if st.button("Entrar no Sistema"):
        if u == "admin" and p == "lojinha123":
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("Acesso Negado")
    st.stop()

# --- MENU LATERAL ---
with st.sidebar:
    st.title("💎 Loja Digital")
    st.write(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
    st.divider()
    menu = st.radio("Navegação:", ["💰 Fluxo de Caixa", "👗 Em Condições", "👥 Clientes", "📊 Relatórios"])
    st.divider()
    
    st.subheader("💾 Backup dos Dados")
    csv = st.session_state['vendas'].to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Vendas (CSV)", csv, "vendas_loja.csv", "text/csv")
    
    if st.button("Sair"):
        st.session_state['auth'] = False
        st.rerun()

# --- ABA 1: FLUXO DE CAIXA ---
if menu == "💰 Fluxo de Caixa":
    st.title("💰 Gestão de Caixa")
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            tipo = st.selectbox("Operação", ["Entrada (Venda)", "Saída (Gasto)"])
            cliente = st.text_input("Nome do Cliente/Fornecedor")
            valor = st.number_input("Valor R$", min_value=0.0)
        with c2:
            metodo = st.selectbox("Forma", ["Pix", "Dinheiro", "Cartão Crédito", "Cartão Débito"])
            desc = st.text_area("Descrição das Peças")
        
        if st.button("✅ Registrar Movimentação"):
            nova = pd.DataFrame([{"data": datetime.now().strftime("%d/%m/%Y %H:%M"), "tipo": tipo, "cliente": cliente, "descricao": desc, "valor": valor, "metodo": metodo}])
            st.session_state['vendas'] = pd.concat([st.session_state['vendas'], nova], ignore_index=True)
            st.success("Lançamento realizado!")

    st.subheader("📋 Histórico Recente")
    st.dataframe(st.session_state['vendas'], use_container_width=True)

# --- ABA 2: CONDICIONAIS ---
elif menu == "👗 Condicionais":
    st.title("👗 Controle de Condicionais (Sacolas)")
    with st.expander("📝 Nova Saída de Peças"):
        cli_c = st.text_input("Nome da Cliente")
        itens_c = st.text_area("O que ela está levando?")
        if st.button("🟠 Registrar Saída"):
            novo_con = pd.DataFrame([{"id": len(st.session_state['condicionais'])+1, "cliente": cli_c, "itens": itens_c, "status": "Pendente"}])
            st.session_state['condicionais'] = pd.concat([st.session_state['condicionais'], novo_con], ignore_index=True)
            st.success("Condicional registrado!")

    st.subheader("⚠️ Pendentes de Devolução/Compra")
    st.table(st.session_state['condicionais'][st.session_state['condicionais']['status'] == "Pendente"])

# --- ABA 3: CLIENTES ---
elif menu == "👥 Clientes":
    st.title("👥 Banco de Clientes")
    with st.form("f_cli"):
        n = st.text_input("Nome")
        t = st.text_input("WhatsApp")
        o = st.text_area("Observações de Gosto")
        if st.form_submit_button("💾 Salvar Cadastro"):
            nc = pd.DataFrame([{"nome": n, "telefone": t, "anotacoes": o}])
            st.session_state['clientes'] = pd.concat([st.session_state['clientes'], nc], ignore_index=True)
            st.success("Cliente cadastrado!")
    st.dataframe(st.session_state['clientes'], use_container_width=True)

# --- ABA 4: RELATÓRIOS ---
elif menu == "📊 Relatórios":
    st.title("📊 Resumo de Resultados")
    df = st.session_state['vendas']
    if not df.empty:
        v = df[df['tipo'] == "Entrada (Venda)"]['valor'].sum()
        g = df[df['tipo'] == "Saída (Gasto)"]['valor'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Vendas", f"R$ {v:.2f}")
        c2.metric("Total de Gastos", f"R$ {g:.2f}")
        c3.metric("Saldo em Caixa", f"R$ {v-g:.2f}", delta=f"{v-g:.2f}")
    else:
        st.info("Aguardando primeiros lançamentos para gerar gráficos.")






