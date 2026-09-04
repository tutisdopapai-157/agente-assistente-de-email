import streamlit as st
from google import genai
import requests
import re # <-- Ferramenta nova para validar e-mails e números

MINHA_CHAVE_API = st.secrets["CHAVE_API"]
LINK_WEBHOOK = st.secrets["LINK_PLANILHA"]
NOME_DA_SUA_EMPRESA = "Nexus" 

st.set_page_config(page_title="Central de Atendimento", page_icon="🎧", layout="centered")

# --- FUNÇÃO DE VALIDAÇÃO ---
def contato_valido(texto):
    if "@" in texto and "." in texto:
        return True # Parece ser um e-mail válido
    numeros = re.sub(r'\D', '', texto)
    if len(numeros) >= 8:
        return True # Parece ser um telefone (tem pelo menos 8 números)
    return False

st.title(f"🎧 Atendimento - {NOME_DA_SUA_EMPRESA}")
st.write("Bem-vindo! Nossa IA pode responder na hora, ou você pode abrir um chamado.")
st.write("---")

nome_cliente = st.text_input("👤 Qual é o seu nome?")
contato_cliente = st.text_input("📧 Seu E-mail ou Telefone:")
mensagem_cliente = st.text_area("📩 Como podemos ajudar?", height=150)

prioridade = st.selectbox(
    "⚠️ Qual a urgência deste assunto?",
    ["🟢 Baixa", "🟡 Média", "🟠 Alta", "🔴 Urgente"]
)

st.write("---")

# Agora temos 3 botões divididos na tela
col1, col2, col3 = st.columns(3)
with col1:
    btn_ia = st.button("Resposta Imediata (IA) ✨", use_container_width=True)
with col2:
    btn_humano = st.button("Enviar para Analista 🚨", use_container_width=True)
with col3:
    btn_bug = st.button("Relatar um Bug 🐞", use_container_width=True)

# Função unificada para não repetirmos código
def enviar_para_planilha(prioridade_escolhida):
    if not nome_cliente or not mensagem_cliente or not contato_cliente:
        st.warning("⚠️ Preencha nome, contato e a mensagem.")
        return
        
    if not contato_valido(contato_cliente):
        st.error("❌ Por favor, digite um E-mail válido ou um Telefone correto.")
        return
        
    with st.spinner("Enviando para a equipe..."):
        try:
            dados = {
                "nome": nome_cliente,
                "mensagem": mensagem_cliente,
                "prioridade": prioridade_escolhida,
                "contato": contato_cliente
            }
            resposta = requests.post(LINK_WEBHOOK, json=dados)
            if resposta.status_code == 200:
                st.success(f"✅ Enviado com sucesso, {nome_cliente}! Entraremos em contato.")
            else:
                st.error("❌ Ocorreu um problema ao enviar.")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")

# Lógica dos botões de envio
if btn_humano:
    enviar_para_planilha(prioridade)

if btn_bug:
    enviar_para_planilha("🐞 BUG RELATADO")

# Lógica da IA
if btn_ia:
    if not nome_cliente or not mensagem_cliente:
        st.warning("⚠️ Preencha seu nome e a mensagem.")
    else:
        with st.spinner("A IA está analisando..."):
            try:
                client = genai.Client(api_key=MINHA_CHAVE_API)
                prompt = f"Você é o assistente virtual da Nexus. Responda amigavelmente o cliente {nome_cliente}. Mensagem: {mensagem_cliente}"
                response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
                st.info(f"**Resposta Virtual:**")
                st.write(response.text)
            except Exception as e:
                st.error(f"❌ Ocorreu um erro na IA: {e}")
