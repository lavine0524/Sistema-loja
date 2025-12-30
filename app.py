import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Lojinha da Ro", layout="wide")

# --- INICIALIZAÇÃO (MEMÓRIA SEGURA) ---
if 'clientes' not in st.session_state:
    st.session_state['clientes'] = pd.DataFrame(columns=['nome', 'telefone', 'anotacoes'])
if 'movimentacoes' not in st.session_state:
    st.session_state['movimentacoes'] = pd.DataFrame(columns=['data', 'tipo', 'cliente', 'descricao', 'valor', 'metodo', 'parcelas'])
if 'condicional' not in st.session_state:
    st.session_state['condicional'] = pd.DataFrame(columns=['id', 'cliente', 'itens', 'data_saida', 'status'])

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🔐 Login - Sistema Comercial")
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    if st.button("Acessar Painel"):
        if u == "admin" and p == "lojinha123":
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("Acesso Negado")
    st.stop()

# --- NAVEGAÇÃO LATERAL ---
with st.sidebar:
    st.title("💎 Loja Digital")
    menu = st.radio("Navegação:", ["💰 Fluxo de Caixa", "👗 Condicionais", "👥 Meus Clientes", "📊 Relatórios"])
    st.divider()
    # BACKUP ESSENCIAL
    st.subheader("💾 Backup Diário")
    csv = st.session_state['movimentacoes'].to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Dados (CSV)", csv, "caixa_loja.csv", "text/csv")
    if st.button("Sair"):
        st.session_state['auth'] = False
        st.rerun()

# --- FUNÇÃO AUXILIAR PARA PEGAR CLIENTES ---
def lista_clientes():
    return ["Consumidor Geral"] + st.session_state['clientes']['nome'].tolist()

# --- TELAS ---
if menu == "💰 Fluxo de Caixa":
    st.title("💰 Gestão de Caixa")
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            tipo = st.selectbox("Tipo de Operação", ["Entrada (Venda)", "Saída (Pagamento)"])
            cliente_sel = st.selectbox("Cliente", lista_clientes())
            valor = st.number_input("Valor R$", min_value=0.0, step=0.01)
        with c2:
            metodo = st.selectbox("Forma", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"])
            parc = st.number_input("Parcelas", 1, 12, 1) if "Crédito" in metodo else 1
            desc = st.text_area("Descrição das Peças:")
        
        if st.button("✅ Registrar Movimentação"):
            nova = pd.DataFrame([{
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "tipo": tipo, "cliente": cliente_sel, "descricao": desc,
                "valor": valor, "metodo": metodo, "parcelas": parc
            }])
            st.session_state['movimentacoes'] = pd.concat([st.session_state['movimentacoes'], nova], ignore_index=True)
            st.success("Registrado!")

    st.divider()
    st.dataframe(st.session_state['movimentacoes'], use_container_width=True)

elif menu == "👗 Condicionais":
    st.title("👗 Controle de Sacola Condicional")
    with st.expander("Nova Saída"):
        cli_c = st.selectbox("Cliente:", lista_clientes())
        itens_c = st.text_area("O que o cliente está levando?")
        if st.button("🟠 Registrar Saída"):
            novo_id = len(st.session_state['condicional']) + 1
            novo_cond = pd.DataFrame([{"id": novo_id, "cliente": cli_c, "itens": itens_c, "data_saida": datetime.now().strftime("%d/%m/%Y"), "status": "Pendente"}])
            st.session_state['condicional'] = pd.concat([st.session_state['condicional'], novo_cond], ignore_index=True)
            st.rerun()

    st.subheader("⚠️ Itens com Clientes")
    df_p = st.session_state['condicional'][st.session_state['condicional']['status'] == 'Pendente']
    st.table(df_p)
    
    if not df_p.empty:
        id_c = st.number_input("ID para dar baixa:", min_value=1, step=1)
        if st.button("✅ Marcar como Finalizado"):
            st.session_state['condicional'].loc[st.session_state['condicional']['id'] == id_c, 'status'] = 'Finalizado'
            st.success("Baixa realizada!")
            st.rerun()

elif menu == "👥 Meus Clientes":
    st.title("👥 Cadastro de Clientes")
    with st.form("novo_cliente"):
        n = st.text_input("Nome Completo")
        t = st.text_input("WhatsApp")
        o = st.text_area("Perfil/Gostos")
        if st.form_submit_button("💾 Salvar Cliente"):
            novo_cli = pd.DataFrame([{"nome": n, "telefone": t, "anotacoes": o}])
            st.session_state['clientes'] = pd.concat([st.session_state['clientes'], novo_cli], ignore_index=True)
            st.success("Cliente salvo!")

    st.dataframe(st.session_state['clientes'], use_container_width=True)

elif menu == "📊 Relatórios":
    st.title("📊 Resultados Diários")
    df = st.session_state['movimentacoes']
    if not df.empty:
        v = df[df['tipo'] == 'Entrada (Venda)']['valor'].sum()
        g = df[df['tipo'] == 'Saída (Pagamento)']['valor'].sum()
        c1, c2, c3 = st.columns(3)
        c1.metric("Vendas", f"R$ {v:.2f}")
        c2.metric("Saídas", f"R$ {g:.2f}")
        c3.metric("Líquido", f"R$ {v-g:.2f}")
    else:
        st.info("Sem dados.")








