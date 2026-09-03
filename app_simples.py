import streamlit as st
from google import genai
import requests

MINHA_CHAVE_API = st.secrets["CHAVE_API"]
LINK_WEBHOOK = st.secrets["LINK_PLANILHA"]
NOME_DA_SUA_EMPRESA = "Sua Empresa" 

st.set_page_config(page_title="Central de Atendimento", page_icon="🎧", layout="centered")

st.title(f"🎧 Atendimento - {NOME_DA_SUA_EMPRESA}")
st.write("Bem-vindo! Nossa IA pode responder na hora, ou você pode abrir um chamado.")
st.write("---")

nome_cliente = st.text_input("👤 Qual é o seu nome?")
mensagem_cliente = st.text_area("📩 Como podemos ajudar?", height=150)

# --- A NOVIDADE AQUI: CAMPO DE URGÊNCIA ---
prioridade = st.selectbox(
    "⚠️ Qual a urgência deste assunto?",
    ["🟢 Baixa", "🟡 Média", "🟠 Alta", "🔴 Urgente"]
)

st.write("---")

col1, col2 = st.columns(2)
with col1:
    btn_ia = st.button("Resposta Imediata (IA) ✨", use_container_width=True)
with col2:
    btn_humano = st.button("Enviar para Analista 🚨", use_container_width=True)

if btn_humano:
    if not nome_cliente or not mensagem_cliente:
        st.warning("⚠️ Preencha seu nome e a mensagem.")
    else:
        with st.spinner("Enviando chamado para a equipe..."):
            try:
                # Agora a "caixa" de dados inclui a prioridade!
                dados = {
                    "nome": nome_cliente,
                    "mensagem": mensagem_cliente,
                    "prioridade": prioridade
                }
                
                resposta = requests.post(LINK_WEBHOOK, json=dados)
                
                if resposta.status_code == 200:
                    st.success(f"✅ Chamado enviado, {nome_cliente}! (Urgência: {prioridade})")
                else:
                    st.error("❌ Ocorreu um problema ao enviar.")
            except Exception as e:
                st.error(f"Erro de conexão: {e}")

if btn_ia:
    if not nome_cliente or not mensagem_cliente:
        st.warning("⚠️ Preencha seu nome e a mensagem.")
    else:
        with st.spinner("Analisando..."):
            try:
                client = genai.Client(api_key=MINHA_CHAVE_API)
                prompt = f"""Você é o assistente virtual da empresa {NOME_DA_SUA_EMPRESA}.
                Fale com o cliente {nome_cliente}.
                MENSAGEM: \"\"\"{mensagem_cliente}\"\"\"
                Escreva uma resposta direta para tentar resolver. Se for complexo, avise-o para clicar no botão "Enviar para Analista"."""
                
                response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
                st.info(f"**Resposta Virtual:**")
                st.write(response.text)
            except Exception as e:
                st.error("Erro na IA.")
