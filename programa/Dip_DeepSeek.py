from flask import Flask, render_template, request, jsonify
import json
import os
from openai import OpenAI
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    Dimension,
    Metric,
    DateRange,
)

# Configuração do Flask
app = Flask(__name__)

# Configuração com variáveis de ambiente
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# Caminhos relativos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'static', 'json')

# Configurações de arquivos
HISTORICO_ARQUIVOS = {
    "geral": os.path.join(DATA_DIR, "historico_conversas.json"),
    "marketing": os.path.join(DATA_DIR, "historico_conversas_marketing.json"),
    "suporte": os.path.join(DATA_DIR, "historico_conversas_suporte.json"),
    "vendas": os.path.join(DATA_DIR, "historico_conversas_vendas.json"),
    "financeiro": os.path.join(DATA_DIR, "historico_conversas_financeiro.json")
}

CONHECIMENTO_ARQUIVOS = {
    "geral": os.path.join(DATA_DIR, "base_conhecimento.json"),
    "marketing": os.path.join(DATA_DIR, "base_conhecimento_marketing.json"),
    "suporte": os.path.join(DATA_DIR, "base_conhecimento_suporte.json"),
    "vendas": os.path.join(DATA_DIR, "base_conhecimento_vendas.json"),
    "financeiro": os.path.join(DATA_DIR, "base_conhecimento_financeiro.json")
}

# Variáveis globais
BASE_CONHECIMENTO = {}
RESUMO_RELATORIOS = {}

# Função unificada para carregar dados
def carregar_dados_iniciais(perfil="geral"):
    global BASE_CONHECIMENTO, RESUMO_RELATORIOS
    
    conhecimento_arquivo = CONHECIMENTO_ARQUIVOS.get(perfil)
    historico_arquivo = HISTORICO_ARQUIVOS.get(perfil)
    
    try:
        with open(conhecimento_arquivo, "r", encoding="utf-8") as f:
            BASE_CONHECIMENTO = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        BASE_CONHECIMENTO = {"conhecimento": []}
    
    try:
        with open(os.path.join(DATA_DIR, "Resumo_dos_relatórios.json"), "r", encoding="utf-8") as f:
            RESUMO_RELATORIOS = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        RESUMO_RELATORIOS = {}

# Rotas
@app.route('/')
def home():
    carregar_dados_iniciais("geral")
    return render_template('index.html')

# ... (mantenha as outras rotas como estão)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
