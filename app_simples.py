import streamlit as st
from google import genai

# --- 1. PUXANDO A CHAVE DO COFRE ---
MINHA_CHAVE_API = st.secrets["CHAVE_API"]
NOME_DA_SUA_EMPRESA = "Sua Empresa" # Coloque o nome do seu negócio aqui
# ----------------------------------

st.set_page_config(page_title="Central de Atendimento", page_icon="🎧", layout="centered")

st.title(f"🎧 Atendimento - {NOME_DA_SUA_EMPRESA}")
st.write("Bem-vindo! Como podemos te ajudar hoje? Nossa IA pode responder na hora, ou você pode abrir um chamado para nossa equipe.")
st.write("---")

# --- CAMPOS PARA O CLIENTE ---
nome_cliente = st.text_input("👤 Qual é o seu nome?", placeholder="Digite seu nome...")
mensagem_cliente = st.text_area("📩 Como podemos ajudar?", height=150, placeholder="Descreva sua dúvida ou problema aqui...")

st.write("---")

col1, col2 = st.columns(2)
with col1:
    btn_ia = st.button("Resposta Imediata (IA) ✨", use_container_width=True)
with col2:
    btn_humano = st.button("Enviar para Analista 🚨", use_container_width=True)

# --- LÓGICA DO BOTÃO HUMANO ---
if btn_humano:
    if not nome_cliente or not mensagem_cliente:
        st.warning("⚠️ Por favor, preencha seu nome e a mensagem para enviarmos o chamado.")
    else:
        # AQUI ENTRARÁ A CONEXÃO COM O BANCO DE DADOS NO FUTURO
        st.success(f"✅ Obrigado, {nome_cliente}! Seu chamado foi enviado para a nossa equipe. Em breve um analista entrará em contato.")

# --- LÓGICA DO BOTÃO IA ---
if btn_ia:
    if not nome_cliente or not mensagem_cliente:
        st.warning("⚠️ Por favor, preencha seu nome e a mensagem.")
    else:
        with st.spinner("Nossa IA está lendo sua mensagem..."):
            try:
                client = genai.Client(api_key=MINHA_CHAVE_API)
                
                # Prompt ajustado para falar DIRETAMENTE com o cliente
                prompt = f"""
                Você é o assistente virtual amigável da empresa {NOME_DA_SUA_EMPRESA}.
                Você está falando diretamente com um cliente chamado {nome_cliente}.
                
                MENSAGEM DO CLIENTE:
                \"\"\"{mensagem_cliente}\"\"\"
                
                Escreva uma resposta direta para o cliente, tentando resolver a dúvida dele da melhor forma possível, de forma educada e empática. 
                Se for um problema complexo que só um humano pode resolver, avise-o para clicar no botão "Enviar para Analista".
                """
                
                response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
                
                st.info(f"**Resposta Virtual para {nome_cliente}:**")
                st.write(response.text)
                
            except Exception as e:
                st.error("Ocorreu um erro ao conectar com a IA. Tente novamente.")
