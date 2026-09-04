import streamlit as st
import requests

# Puxamos as senhas do mesmo cofre!
LINK_WEBHOOK = st.secrets["LINK_PLANILHA"]
SENHA_DO_ADMIN = st.secrets["SENHA_ADMIN"]

st.set_page_config(page_title="Painel Interno", page_icon="⚙️", layout="centered")

# --- SISTEMA DE LOGIN PARA PROTEGER OS DADOS ---
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔒 Área Restrita da Equipe")
    senha_digitada = st.text_input("Senha de Acesso:", type="password")
    
    if st.button("Entrar"):
        if senha_digitada == SENHA_DO_ADMIN:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("❌ Senha incorreta!")
    st.stop()

# --- TELA DO PAINEL DE CHAMADOS ---
st.title("⚙️ Painel de Chamados")
st.write("Gerencie e resolva os tickets abertos pelos clientes.")

# Botões de controle
col1, col2 = st.columns(2)
with col1:
    if st.button("Atualizar Fila 🔄", use_container_width=True):
        st.rerun()
with col2:
    if st.button("Sair (Bloquear Tela) 🔒", use_container_width=True):
        st.session_state.logado = False
        st.rerun()

# 1. Pede para a planilha enviar a lista de chamados
with st.spinner("Buscando chamados..."):
    try:
        resposta = requests.get(LINK_WEBHOOK)
        chamados = resposta.json()
    except:
        st.error("Erro ao conectar com a planilha.")
        chamados = []

# ==========================================
# --- A NOVIDADE: MINI PAINEL DE ESTATÍSTICAS ---
# ==========================================
st.write("---")

# O Python faz as contas para você
total_chamados = len(chamados)
total_urgentes = sum(1 for chamado in chamados if "Urgente" in chamado.get('prioridade', ''))

# Mostra os números grandes na tela
metrica1, metrica2 = st.columns(2)
with metrica1:
    st.metric("Total de Chamados 📋", total_chamados)
with metrica2:
    st.metric("🚨 Casos Urgentes", total_urgentes)
# ==========================================

# ==========================================
# --- BARRA DE PESQUISA ---
# ==========================================
st.write("---")
termo_busca = st.text_input("🔍 Buscar por nome do cliente:", placeholder="Digite o nome para filtrar...")

if termo_busca:
    chamados_filtrados = [c for c in chamados if termo_busca.lower() in c['nome'].lower()]
else:
    chamados_filtrados = chamados
# ==========================================

st.write("---")

# 2. Mostra os chamados na tela 
if len(chamados_filtrados) == 0:
    if termo_busca:
        st.warning(f"Nenhum chamado encontrado para '{termo_busca}'.")
    else:
        st.success("🎉 Nenhum chamado pendente! A fila está limpa.")
else:
    for chamado in chamados_filtrados:
        with st.expander(f"{chamado['prioridade']} | 👤 {chamado['nome']} ({chamado['data']})"):
            st.write(f"**Mensagem:** {chamado['mensagem']}")
            
            if st.button("✅ Marcar como Resolvido", key=f"btn_{chamado['linha']}"):
                with st.spinner("Apagando..."):
                    requests.post(LINK_WEBHOOK, json={"acao": "apagar", "linha": chamado['linha']})
                    st.success("Resolvido! O chamado foi removido.")
                    st.rerun()
