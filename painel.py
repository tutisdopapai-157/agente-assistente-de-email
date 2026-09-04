import streamlit as st
import requests

LINK_WEBHOOK = st.secrets["LINK_PLANILHA"]
SENHA_DO_ADMIN = st.secrets["SENHA_ADMIN"]

st.set_page_config(page_title="Painel Interno", page_icon="⚙️", layout="wide") # Mudei pra 'wide' pra caber tudo

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

st.title("⚙️ Painel de Chamados - Nexus")

col1, col2 = st.columns(2)
with col1:
    if st.button("Atualizar Fila 🔄", use_container_width=True):
        st.rerun()
with col2:
    if st.button("Sair (Bloquear Tela) 🔒", use_container_width=True):
        st.session_state.logado = False
        st.rerun()

with st.spinner("Buscando chamados..."):
    try:
        resposta = requests.get(LINK_WEBHOOK)
        chamados = resposta.json()
    except:
        st.error("Erro ao conectar com a planilha.")
        chamados = []

st.write("---")

# --- CONTAGENS ATUALIZADAS ---
total_chamados = len(chamados)
total_urgentes = sum(1 for c in chamados if "Urgente" in c.get('prioridade', ''))
total_bugs = sum(1 for c in chamados if "BUG" in c.get('prioridade', '').upper())

# Agora temos 3 colunas de métricas!
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Total 📋", total_chamados)
with m2:
    st.metric("🚨 Urgentes", total_urgentes)
with m3:
    st.metric("🐞 Bugs Relatados", total_bugs)

st.write("---")
termo_busca = st.text_input("🔍 Buscar por nome do cliente:")

if termo_busca:
    chamados_filtrados = [c for c in chamados if termo_busca.lower() in c['nome'].lower()]
else:
    chamados_filtrados = chamados

st.write("---")

if len(chamados_filtrados) == 0:
    st.success("🎉 A fila está limpa.")
else:
    for chamado in chamados_filtrados:
        with st.expander(f"{chamado['prioridade']} | 👤 {chamado['nome']} ({chamado['data']})"):
            # Exibindo o novo campo de contato!
            st.write(f"📞 **Contato:** {chamado.get('contato', 'Não informado')}")
            st.write(f"**Mensagem:** {chamado['mensagem']}")
            
            if st.button("✅ Marcar como Resolvido", key=f"btn_{chamado['linha']}"):
                with st.spinner("Apagando..."):
                    requests.post(LINK_WEBHOOK, json={"acao": "apagar", "linha": chamado['linha']})
                    st.success("Removido!")
                    st.rerun()
