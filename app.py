import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Lojinha da Ro", layout="wide")

# Inicialização da Memória
if 'movimentacoes' not in st.session_state:
    st.session_state['movimentacoes'] = pd.DataFrame(columns=['data', 'tipo', 'cliente', 'descricao', 'valor', 'metodo', 'parcelas'])
if 'clientes' not in st.session_state:
    st.session_state['clientes'] = pd.DataFrame(columns=['nome', 'telefone', 'anotacoes'])
if 'condicional' not in st.session_state:
    st.session_state['condicional'] = pd.DataFrame(columns=['id', 'data', 'cliente', 'itens', 'status'])

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🔐 Login Administrativo")
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    if st.button("Acessar"):
        if u == "admin" and p == "lojinha123":
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("Incorreto")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.title("💎 Loja Digital")
    menu = st.radio("Ir para:", ["💰 Fluxo de Caixa", "👗 Condicionais", "👥 Clientes"])
    st.divider()
    
    st.subheader("💾 Exportar para Excel")
    # Agora o download usa ponto e vírgula para abrir direto no Excel do Brasil
    csv_data = st.session_state['movimentacoes'].to_csv(index=False, sep=';').encode('utf-8-sig')
    st.download_button("📥 Baixar Planilha do Dia", csv_data, "vendas_loja.csv", "text/csv")
    
    if st.button("Sair"):
        st.session_state['auth'] = False
        st.rerun()

# --- FLUXO DE CAIXA ---
if menu == "💰 Fluxo de Caixa":
    st.header("💰 Gestão de Caixa")
    
    lista_clis = ["Consumidor Geral"] + st.session_state['clientes']['nome'].tolist()
    
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            tipo = st.selectbox("Operação", ["Entrada (Venda)", "Saída (Pagamento)"])
            cli = st.selectbox("Cliente", lista_clis)
            val = st.number_input("Valor R$", min_value=0.0, step=0.01)
        with c2:
            met = st.selectbox("Forma", ["Pix", "Dinheiro", "Cartão Crédito", "Cartão Débito"])
            par = st.number_input("Parcelas", 1, 12, 1) if "Crédito" in met else 1
            desc = st.text_area("Descrição (Marcas/Peças)")
        
        if st.button("✅ Registrar e Salvar"):
            nova_linha = pd.DataFrame([{
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "tipo": tipo, "cliente": cli, "descricao": desc,
                "valor": val, "metodo": met, "parcelas": par
            }])
            st.session_state['movimentacoes'] = pd.concat([st.session_state['movimentacoes'], nova_linha], ignore_index=True)
            st.success("Venda registrada! Clique no botão azul na esquerda para baixar seu backup.")

    st.subheader("📋 Histórico Registrado")
    st.dataframe(st.session_state['movimentacoes'], use_container_width=True)

# --- CLIENTES ---
elif menu == "👥 Clientes":
    st.header("👥 Cadastro de Clientes")
    with st.form("cad_cli"):
        n = st.text_input("Nome")
        t = st.text_input("Telefone")
        o = st.text_area("Notas")
        if st.form_submit_button("Salvar"):
            nc = pd.DataFrame([{"nome": n, "telefone": t, "anotacoes": o}])
            st.session_state['clientes'] = pd.concat([st.session_state['clientes'], nc], ignore_index=True)
            st.success("Cliente cadastrado!")
    st.dataframe(st.session_state['clientes'], use_container_width=True)

# --- CONDICIONAIS ---
elif menu == "👗 Condicionais":
    st.header("👗 Controle de Condicionais")
    with st.expander("Registrar Saída de Sacola"):
        cli_c = st.selectbox("Cliente:", ["Consumidor Geral"] + st.session_state['clientes']['nome'].tolist())
        it = st.text_area("Itens na sacola")
        if st.button("Lançar Condicional"):
            nova_c = pd.DataFrame([{"id": len(st.session_state['condicional'])+1, "data": datetime.now().strftime("%d/%m/%Y"), "cliente": cli_c, "itens": it, "status": "Pendente"}])
            st.session_state['condicional'] = pd.concat([st.session_state['condicional'], nova_c], ignore_index=True)
            st.rerun()
    st.table(st.session_state['condicional'][st.session_state['condicional']['status'] == 'Pendente'])









