import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO INICIAL ---
if not os.path.exists('fichas'): os.makedirs('fichas')

def iniciar_banco():
    conn = sqlite3.connect('caixa_loja.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, telefone TEXT, anotacoes TEXT, foto_ficha TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS movimentacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, tipo TEXT, cliente TEXT, descricao TEXT, valor REAL, metodo TEXT, parcelas INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS condicional (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, itens TEXT, data_saida TEXT, status TEXT)')
    conn.commit()
    conn.close()

iniciar_banco()

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; transition: 0.3s; }
    .stDownloadButton>button { width: 100%; }
    div[data-testid="metric-container"] {
        background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

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

# --- NAVEGAÇÃO LATERAL ---
with st.sidebar:
    st.title("💎 Loja Digital")
    st.write(f"Bem-vindo, {datetime.now().strftime('%d/%m/%Y')}")
    st.divider()
    menu = st.radio("Navegação:", ["💰 Fluxo de Caixa", "👗 Condicionais", "👥 Meus Clientes", "📊 Relatórios Diários"])
    st.divider()
    if st.button("Sair do Sistema"):
        st.session_state['autenticado'] = False
        st.rerun()

# --- CONEXÃO AUXILIAR ---
def get_clientes():
    conn = sqlite3.connect('caixa_loja.db')
    df = pd.read_sql_query("SELECT nome FROM clientes", conn)
    conn.close()
    return ["Consumidor Geral"] + df['nome'].tolist()

# --- TELAS ---
if menu == "💰 Fluxo de Caixa":
    st.title("💰 Gestão de Caixa")
    
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            tipo = st.selectbox("Tipo de Operação", ["Entrada (Venda)", "Saída (Pagamento)"])
            cliente_sel = st.selectbox("Cliente", get_clientes())
            valor = st.number_input("Valor da Operação R$", min_value=0.0, step=0.01)
        with c2:
            metodo = st.selectbox("Forma de Recebimento", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"])
            parc = st.number_input("Parcelas", 1, 12, 1) if "Crédito" in metodo else 1
            desc = st.text_area("Roupas/Marcas/Detalhes:")
        
        if st.button("✅ Registrar Movimentação", use_container_width=True):
            if valor > 0 and desc:
                conn = sqlite3.connect('caixa_loja.db')
                conn.execute('INSERT INTO movimentacoes (data, tipo, cliente, descricao, valor, metodo, parcelas) VALUES (?,?,?,?,?,?,?)',
                          (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tipo, cliente_sel, desc, valor, metodo, parc))
                conn.commit(); conn.close()
                st.success("Registrado no caixa com sucesso!")
                st.rerun()

    st.divider()
    conn = sqlite3.connect('caixa_loja.db')
    df_mov = pd.read_sql_query("SELECT * FROM movimentacoes ORDER BY id DESC", conn)
    conn.close()
    st.dataframe(df_mov, use_container_width=True)
    
    with st.expander("🗑️ Excluir Lançamento Incorreto"):
        id_del = st.number_input("ID do registro:", min_value=0, step=1)
        if st.button("🔥 Apagar Permanentemente", type="primary"):
            conn = sqlite3.connect('caixa_loja.db'); conn.execute('DELETE FROM movimentacoes WHERE id=?', (id_del,)); conn.commit(); conn.close()
            st.rerun()

elif menu == "👗 Condicionais":
    st.title("👗 Controle de Sacola Condicional")
    with st.expander("Nova Saída (Sacoleiro)"):
        cli_c = st.selectbox("Cliente:", get_clientes())
        itens_c = st.text_area("Descreva as peças que o cliente está levando:")
        if st.button("🟠 Registrar Saída de Peças"):
            conn = sqlite3.connect('caixa_loja.db')
            conn.execute("INSERT INTO condicional (cliente, itens, data_saida, status) VALUES (?,?,?,?)",
                         (cli_c, itens_c, datetime.now().strftime("%d/%m/%Y %H:%M"), "Pendente"))
            conn.commit(); conn.close()
            st.rerun()

    st.subheader("⚠️ Itens em posse de clientes")
    conn = sqlite3.connect('caixa_loja.db')
    df_p = pd.read_sql_query("SELECT * FROM condicional WHERE status='Pendente'", conn)
    conn.close()
    st.table(df_p)
    
    col_a, col_b = st.columns(2)
    id_c = col_a.number_input("ID do Condicional:", min_value=0, step=1)
    if col_b.button("✅ Baixar (Devolvido/Comprado)"):
        conn = sqlite3.connect('caixa_loja.db'); conn.execute("UPDATE condicional SET status='Finalizado' WHERE id=?", (id_c,)); conn.commit(); conn.close()
        st.success("Status atualizado!")
        st.rerun()

elif menu == "👥 Meus Clientes":
    st.title("👥 Banco de Dados de Clientes")
    with st.expander("📝 Cadastrar Novo Cliente"):
        n = st.text_input("Nome Completo"); t = st.text_input("WhatsApp"); o = st.text_area("Perfil/Gostos")
        f = st.file_uploader("Foto da Ficha Antiga", type=['jpg','png'])
        if st.button("💾 Salvar Cliente"):
            path = f"fichas/{n}.jpg" if f else ""
            if f:
                with open(path, "wb") as file: file.write(f.getbuffer())
            conn = sqlite3.connect('caixa_loja.db'); conn.execute("INSERT INTO clientes (nome,telefone,anotacoes,foto_ficha) VALUES (?,?,?,?)",(n,t,o,path)); conn.commit(); conn.close()
            st.rerun()

    conn = sqlite3.connect('caixa_loja.db')
    df_clis = pd.read_sql_query("SELECT * FROM clientes", conn)
    for i, r in df_clis.iterrows():
        with st.expander(f"👤 {r['nome']}"):
            st.write(f"**Contato:** {r['telefone']} | **Obs:** {r['anotacoes']}")
            if r['foto_ficha'] and os.path.exists(r['foto_ficha']): st.image(r['foto_ficha'], width=250)

elif menu == "📊 Relatórios Diários":
    st.title("📊 Fechamento e Resultados")
    dia = st.date_input("Selecione o dia:", datetime.now())
    conn = sqlite3.connect('caixa_loja.db')
    df_dia = pd.read_sql_query(f"SELECT * FROM movimentacoes WHERE data LIKE '{dia.strftime('%Y-%m-%d')}%'", conn)
    conn.close()
    
    if not df_dia.empty:
        v = df_dia[df_dia['tipo']=='Entrada (Venda)']['valor'].sum()
        g = df_dia[df_dia['tipo']=='Saída (Pagamento)']['valor'].sum()
        c1, c2, c3 = st.columns(3)
        c1.metric("Vendas Brutas", f"R$ {v:.2f}")
        c2.metric("Despesas", f"R$ {g:.2f}")
        c3.metric("Lucro Líquido", f"R$ {v-g:.2f}")
        
        st.subheader("Vendas por Método")
        st.bar_chart(df_dia[df_dia['tipo']=='Entrada (Venda)'].groupby('metodo')['valor'].sum())
    else: st.info("Nenhuma movimentação neste dia.")