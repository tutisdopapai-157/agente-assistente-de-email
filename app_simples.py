import streamlit as st
from google import genai

# --- 1. PUXANDO AS SENHAS DO COFRE DA NUVEM ---
# O código agora vai buscar as senhas de forma invisível!
MINHA_CHAVE_API = st.secrets["CHAVE_API"]
SENHA_DO_ADMIN = st.secrets["SENHA_ADMIN"]
# ----------------------------------------------

st.set_page_config(page_title="Gerador de Respostas", page_icon="📝", layout="centered")

# --- 2. SISTEMA DE LOGIN (CADEADO) ---
if "logado" not in st.session_state:
    st.session_state.logado = False

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

# --- 3. APLICATIVO PRINCIPAL ---
st.title("📝 Gerador Rápido de Respostas")
if st.button("Sair (Bloquear Tela) 🔒"):
    st.session_state.logado = False
    st.rerun()

st.write("---")
nome_empresa = st.text_input("🏢 Nome da Empresa:", placeholder="Sua Empresa")
texto_email = st.text_area("📩 Mensagem do cliente:", height=200)

col1, col2 = st.columns(2)
with col1:
    btn_gerar = st.button("Gerar Resposta ✨", use_container_width=True)
with col2:
    btn_analista = st.button("Falar com Analista 💬", use_container_width=True)

if btn_analista:
    st.info("**WhatsApp:** [(11) 99999-9999](https://wa.me/5511999999999) | **E-mail:** contato@empresa.com")

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
                st.error(f"Erro: {e}")
