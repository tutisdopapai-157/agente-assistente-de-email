import streamlit as st
from google import genai
from datetime import datetime

# --- 1. PUXANDO AS SENHAS DO COFRE DA NUVEM ---
MINHA_CHAVE_API = st.secrets["CHAVE_API"]
SENHA_DO_ADMIN = st.secrets["SENHA_ADMIN"]
# ----------------------------------------------

st.set_page_config(page_title="Sistema de Atendimento", page_icon="📝", layout="centered")

# --- 2. GERENCIADOR DE MEMÓRIA E LOGIN ---
if "logado" not in st.session_state:
    st.session_state.logado = False

# Criando a memória para guardar os chamados (nossa lista de problemas)
if "chamados" not in st.session_state:
    st.session_state.chamados = []

# Tela de bloqueio
if not st.session_state.logado:
    st.title("🔒 Acesso Restrito")
    senha_digitada = st.text_input("Senha de Acesso:", type="password")
    
    if st.button("Entrar"):
        if senha_digitada == SENHA_DO_ADMIN:
            st.session_state.logado = True
            st.rerun() 
        else:
            st.error("❌ Senha incorreta!")
    st.stop() 


# =====================================================================
# --- 3. MENU DE NAVEGAÇÃO LATERAL (SÓ APARECE DEPOIS DE LOGAR) ---
# =====================================================================
st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Escolha a tela:", ["📝 Agente de Respostas", "🚨 Painel de Chamados"])

st.sidebar.write("---")
if st.sidebar.button("Sair (Bloquear Tela) 🔒"):
    st.session_state.logado = False
    st.rerun()


# =====================================================================
# --- TELA 1: AGENTE DE RESPOSTAS ---
# =====================================================================
if pagina == "📝 Agente de Respostas":
    st.title("📝 Gerador Rápido de Respostas")
    st.write("Gere a resposta com IA ou encaminhe para um analista humano.")
    st.write("---")
    
    nome_empresa = st.text_input("🏢 Nome da Empresa:", placeholder="Sua Empresa")
    texto_email = st.text_area("📩 Mensagem do cliente:", height=200)

    # Nossos botões lado a lado
    col1, col2 = st.columns(2)
    with col1:
        btn_gerar = st.button("Gerar Resposta ✨", use_container_width=True)
    with col2:
        btn_chamado = st.button("Encaminhar para Analista 🚨", use_container_width=True)

    # Lógica de enviar para o analista
    if btn_chamado:
        if not nome_empresa or not texto_email:
            st.warning("⚠️ Preencha a empresa e a mensagem antes de encaminhar o chamado.")
        else:
            # Salva o problema na memória do aplicativo
            novo_chamado = {
                "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "empresa": nome_empresa,
                "mensagem": texto_email
            }
            st.session_state.chamados.append(novo_chamado)
            st.success("✅ Chamado enviado com sucesso! Os analistas já podem ver isso no Painel.")

    # Lógica da IA (Gerar Resposta)
    if btn_gerar:
        if not nome_empresa or not texto_email:
            st.warning("⚠️ Preencha os campos!")
        else:
            with st.spinner("Analisando..."):
                try:
                    client = genai.Client(api_key=MINHA_CHAVE_API)
                    prompt = f"""Você é o atendimento da empresa {nome_empresa}.
                    MENSAGEM: \"\"\"{texto_email}\"\"\"
                    Retorne:
                    🔴 URGÊNCIA: 
                    🏷️ CATEGORIA: 
                    📌 RESUMO: 
                    ✉️ RESPOSTA: (Fale em nome de {nome_empresa})"""
                    
                    response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
                    st.success("Sucesso!")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Erro na IA: {e}")


# =====================================================================
# --- TELA 2: PAINEL DE CHAMADOS (ANALISTAS) ---
# =====================================================================
elif pagina == "🚨 Painel de Chamados":
    st.title("🚨 Fila de Atendimento Humano")
    st.write("Casos em que a IA não resolveu e exigem análise de um humano.")
    st.write("---")
    
    # Verifica se a lista de chamados está vazia
    if len(st.session_state.chamados) == 0:
        st.info("🎉 Nenhum chamado pendente no momento! A fila está limpa.")
    else:
        # Cria uma "caixinha" expansível para cada chamado
        for index, chamado in enumerate(st.session_state.chamados):
            with st.expander(f"Chamado de: {chamado['empresa']} - (Aberto em {chamado['data_hora']})"):
                st.write("**Mensagem original do cliente:**")
                st.write(chamado['mensagem'])
                
                # Botão para o analista resolver e tirar o problema da lista
                if st.button(f"Marcar como Resolvido ✔️", key=f"btn_resolver_{index}"):
                    st.session_state.chamados.pop(index) # Remove da lista
                    st.rerun() # Atualiza a tela na hora
