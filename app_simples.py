import streamlit as st
from google import genai
import requests  # <-- Ferramenta para conversar com a planilha

# --- 1. PUXANDO AS INFORMAÇÕES DO COFRE ---
MINHA_CHAVE_API = st.secrets["CHAVE_API"]
LINK_WEBHOOK = st.secrets["LINK_PLANILHA"]
NOME_DA_SUA_EMPRESA = "Sua Empresa" 
# ------------------------------------------

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


# --- LÓGICA DO BOTÃO HUMANO (CONEXÃO COM PLANILHA) ---
if btn_humano:
    if not nome_cliente or not mensagem_cliente:
        st.warning("⚠️ Por favor, preencha seu nome e a mensagem para enviarmos o chamado.")
    else:
        with st.spinner("Enviando chamado para a equipe..."):
            try:
                # 1. Prepara a "caixa" com os dados do cliente
                dados = {
                    "nome": nome_cliente,
                    "mensagem": mensagem_cliente
                }
                
                # 2. Envia a caixa para o seu link do Google Planilhas
                resposta = requests.post(LINK_WEBHOOK, json=dados)
                
                # 3. Avisa se deu tudo certo
                if resposta.status_code == 200:
                    st.success(f"✅ Obrigado, {nome_cliente}! Seu chamado foi enviado para a nossa equipe. Em breve um analista entrará em contato.")
                else:
                    st.error("❌ Ocorreu um problema ao enviar. Tente novamente.")
                    
            except Exception as e:
                st.error(f"Ocorreu um erro de conexão: {e}")


# --- LÓGICA DO BOTÃO IA ---
if btn_ia:
    if not nome_cliente or not mensagem_cliente:
        st.warning("⚠️ Por favor, preencha seu nome e a mensagem.")
    else:
        with st.spinner("Nossa IA está lendo sua mensagem..."):
            try:
                client = genai.Client(api_key=MINHA_CHAVE_API)
                prompt = f"""
                Você é o assistente virtual da empresa {NOME_DA_SUA_EMPRESA}.
                Fale diretamente com um cliente chamado {nome_cliente}.
                MENSAGEM: \"\"\"{mensagem_cliente}\"\"\"
                Escreva uma resposta direta para tentar resolver a dúvida de forma empática. 
                Se for complexo, avise-o para clicar em "Enviar para Analista".
                """
                
                response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
                
                st.info(f"**Resposta Virtual para {nome_cliente}:**")
                st.write(response.text)
                
            except Exception as e:
                st.error("Ocorreu um erro ao conectar com a IA. Tente novamente.")
