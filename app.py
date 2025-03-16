import os
from flask import Flask, render_template, request
import google.generativeai as genai
import wikipediaapi
import requests
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Configurar a chave da API do Gemini
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# Escolher o modelo correto do Gemini
modelo = genai.GenerativeModel("gemini-2.0-flash")

# Inicializa o Flask
app = Flask(__name__)

# Configurar a API da Wikipédia com um User-Agent válido
wiki_api = wikipediaapi.Wikipedia(
    language="pt",
    user_agent="OrionBot/1.0 (contato: rccalcini@gmail.com)"
)

# Configurar a API de Notícias (NewsAPI)
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = f"https://newsapi.org/v2/top-headlines?country=br&apiKey={NEWS_API_KEY}"

# Página inicial
@app.route("/", methods=["GET", "POST"])
def index():
    resposta = ""

    if request.method == "POST":
        pergunta = request.form.get("pergunta")
        if pergunta:
            # Verifica se a pergunta é sobre notícias
            if "notícia" in pergunta.lower() or "notícias" in pergunta.lower():
                resposta = "📰 **Notícias Recentes:**\n\n" + buscar_noticias()
            # Verifica se a pergunta é sobre Wikipédia
            elif "wikipedia" in pergunta.lower():
                termo = pergunta.replace("wikipedia", "").strip()
                resposta = f"📖 **Fonte: Wikipédia ({termo})**\n\n" + buscar_wikipedia(termo)
            else:
                resposta = "🤖 **Resposta da IA:**\n\n" + buscar_gemini(pergunta)

    return render_template("index.html", resposta=resposta)

# Função para buscar resposta no Gemini
def buscar_gemini(pergunta):
    try:
        resposta = modelo.generate_content(pergunta).text
        return resposta
    except Exception as e:
        return f"Erro ao buscar resposta na IA: {str(e)}"

# Função para buscar artigos na Wikipédia
def buscar_wikipedia(termo):
    try:
        pagina = wiki_api.page(termo)
        if pagina.exists():
            return pagina.summary[:1000] + "..."
        else:
            return "Não encontrei nada sobre esse assunto na Wikipédia."
    except Exception as e:
        return f"Erro ao buscar na Wikipédia: {str(e)}"

# Função para buscar notícias recentes
def buscar_noticias():
    try:
        response = requests.get(NEWS_API_URL)
        dados = response.json()
        artigos = dados.get("articles", [])

        if not artigos:
            return "Nenhuma notícia encontrada no momento."

        # Formata as notícias principais
        noticias_formatadas = ""
        for artigo in artigos[:5]:  # Pega apenas as 5 primeiras notícias
            noticias_formatadas += f"📰 {artigo['title']} - {artigo['source']['name']}\n🔗 {artigo['url']}\n\n"

        return noticias_formatadas
    except Exception as e:
        return f"Erro ao buscar notícias: {str(e)}"

# Executa o app
if __name__ == "__main__":
    app.run(debug=True)
