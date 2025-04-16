from flask import Flask, render_template, request, jsonify
import json
import os
from openai import OpenAI


app = Flask(__name__)

GA_PROPERTY_ID = "358341825"

# Configuração do DeepSeek
DEEPSEEK_API_KEY = "sk-88c90c0c91c94912b276f19234eacc51"
deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# Caminhos relativos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(BASE_DIR, 'data', 'json')

# Configurações de arquivos - atualize para incluir os diferentes perfis
HISTORICO_ARQUIVOS = {
    "geral": r"C:\Users\Comercial\Desktop\Programação\Python\programa\data\historico_conversas.json",
    "marketing": r"C:\Users\Comercial\Desktop\Programação\Python\programa\data\historico_conversas_marketing.json",
    "suporte": r"C:\Users\Comercial\Desktop\Programação\Python\programa\data\historico_conversas_suporte.json",
    "vendas": r"C:\Users\Comercial\Desktop\Programação\Python\programa\data\historico_conversas_vendas.json",
    "financeiro": r"C:\Users\Comercial\Desktop\Programação\Python\programa\data\historico_conversas_financeiro.json"
}

CONHECIMENTO_ARQUIVOS = {
    "geral": r"C:\Users\Comercial\Desktop\Programação\Python\programa\data\base_conhecimento.json",
    "marketing": r"C:\Users\Comercial\Desktop\Programação\Python\programa\data\base_conhecimento_marketing.json",
    "suporte": r"C:\Users\Comercial\Desktop\Programação\Python\programa\data\base_conhecimento_suporte.json",
    "vendas": r"C:\Users\Comercial\Desktop\Programação\Python\programa\data\base_conhecimento_vendas.json",
    "financeiro": r"C:\Users\Comercial\Desktop\Programação\Python\programa\data\base_conhecimento_financeiro.json"
}

# Variáveis globais
CONTEUDO_ARQUIVOS = {}
BASE_CONHECIMENTO = {}
RESUMO_RELATORIOS = {}

# Carrega os dados iniciais
# Função para carregar dados (unificada)
def carregar_dados_iniciais(perfil="geral"):
    global BASE_CONHECIMENTO, CONHECIMENTO_ARQUIVO, HISTORICO_ARQUIVO
    
    CONHECIMENTO_ARQUIVO = CONHECIMENTO_ARQUIVOS.get(perfil)
    HISTORICO_ARQUIVO = HISTORICO_ARQUIVOS.get(perfil)
    
    try:
        with open(CONHECIMENTO_ARQUIVO, "r", encoding="utf-8") as f:
            BASE_CONHECIMENTO = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        BASE_CONHECIMENTO = {"conhecimento": []}
        
    try:
        with open(r"C:\Users\Comercial\Desktop\Programação\Python\programa\data\Resumo_dos_relatórios.json", "r", encoding="utf-8") as f:
            RESUMO_RELATORIOS = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        RESUMO_RELATORIOS = {}
        
def carregar_dados_iniciais(perfil="marketing"):
    global BASE_CONHECIMENTO, RESUMO_RELATORIOS, CONHECIMENTO_ARQUIVO, HISTORICO_ARQUIVO
    
    # Define os arquivos corretos para o perfil
    CONHECIMENTO_ARQUIVO = CONHECIMENTO_ARQUIVOS.get(perfil, CONHECIMENTO_ARQUIVOS["marketing"])
    HISTORICO_ARQUIVO = HISTORICO_ARQUIVOS.get(perfil, HISTORICO_ARQUIVOS["marketing"])
    
    try:
        with open(CONHECIMENTO_ARQUIVO, "r", encoding="utf-8") as f:
            BASE_CONHECIMENTO = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        BASE_CONHECIMENTO = {"conhecimento": []}
    
    try:
        with open(r"C:\Users\Comercial\Desktop\Programação\Python\programa\data\Resumo_dos_relatórios.json", "r", encoding="utf-8") as f:
            RESUMO_RELATORIOS = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        RESUMO_RELATORIOS = {}
        
def carregar_dados_iniciais(perfil="suporte"):
    global BASE_CONHECIMENTO, RESUMO_RELATORIOS, CONHECIMENTO_ARQUIVO, HISTORICO_ARQUIVO
    
    # Define os arquivos corretos para o perfil
    CONHECIMENTO_ARQUIVO = CONHECIMENTO_ARQUIVOS.get(perfil, CONHECIMENTO_ARQUIVOS["suporte"])
    HISTORICO_ARQUIVO = HISTORICO_ARQUIVOS.get(perfil, HISTORICO_ARQUIVOS["suporte"])
    
    try:
        with open(CONHECIMENTO_ARQUIVO, "r", encoding="utf-8") as f:
            BASE_CONHECIMENTO = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        BASE_CONHECIMENTO = {"conhecimento": []}   
     
def carregar_dados_iniciais(perfil="vendas"):
    global BASE_CONHECIMENTO, RESUMO_RELATORIOS, CONHECIMENTO_ARQUIVO, HISTORICO_ARQUIVO
    
    # Define os arquivos corretos para o perfil
    CONHECIMENTO_ARQUIVO = CONHECIMENTO_ARQUIVOS.get(perfil, CONHECIMENTO_ARQUIVOS["vendas"])
    HISTORICO_ARQUIVO = HISTORICO_ARQUIVOS.get(perfil, HISTORICO_ARQUIVOS["vendas"])
    
    try:
        with open(CONHECIMENTO_ARQUIVO, "r", encoding="utf-8") as f:
            BASE_CONHECIMENTO = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        BASE_CONHECIMENTO = {"conhecimento": []}
        
def carregar_dados_iniciais(perfil="financeiro"):
    global BASE_CONHECIMENTO, RESUMO_RELATORIOS, CONHECIMENTO_ARQUIVO, HISTORICO_ARQUIVO
    
    # Define os arquivos corretos para o perfil
    CONHECIMENTO_ARQUIVO = CONHECIMENTO_ARQUIVOS.get(perfil, CONHECIMENTO_ARQUIVOS["financeiro"])
    HISTORICO_ARQUIVO = HISTORICO_ARQUIVOS.get(perfil, HISTORICO_ARQUIVOS["financeiro"])
    
    try:
        with open(CONHECIMENTO_ARQUIVO, "r", encoding="utf-8") as f:
            BASE_CONHECIMENTO = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        BASE_CONHECIMENTO = {"conhecimento": []}
    
    try:
        with open(r"C:\Users\Comercial\Desktop\Programação\Python\programa\data\Resumo_dos_relatórios.json", "r", encoding="utf-8") as f:
            RESUMO_RELATORIOS = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        RESUMO_RELATORIOS = {}                  

carregar_dados_iniciais()

# Rota principal
@app.route('/')
def home():
    carregar_dados_iniciais("geral")
    return render_template('index.html')

@app.route('/marketing')
def marketing():
    carregar_dados_iniciais("marketing")
    return render_template('marketing.html')

@app.route('/suporte')
def suporte():
    carregar_dados_iniciais("suporte")
    return render_template('suporte.html')

@app.route('/financeiro')
def financeiro():
    carregar_dados_iniciais("financeiro")
    return render_template('financeiro.html')

@app.route('/vendas')
def vendas():
    carregar_dados_iniciais("vendas")
    return render_template('vendas.html')

# Rota para o chat
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message']
    historico = carregar_historico()
    
    # Adiciona a nova mensagem ao histórico
    historico.append(("user", user_message))
    
    # Obtém a resposta do bot
    bot_response = gerar_resposta_bot(historico)
    historico.append(("assistant", bot_response))
    
    # Salva o histórico atualizado
    salvar_historico(historico)
    
    return jsonify({'response': bot_response})

@app.route('/chat/limpar_historico', methods=['POST'])
def limpar_historico():
    try:
        # Limpa o arquivo do histórico
        with open(HISTORICO_ARQUIVO, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Erro ao limpar o histórico: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    

@app.route('/chat/historico')
def obter_historico():
    historico = carregar_historico()
    # Formata o histórico para o frontend
    historico_formatado = [{"role": role, "content": content} for role, content in historico]
    return jsonify(historico_formatado)

def carregar_historico() -> list:
    try:
        with open(HISTORICO_ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def salvar_historico(historico: list) -> None:
    try:
        with open(HISTORICO_ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(historico, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar o histórico: {e}")

def obter_dados_google_analytics():
    try:
        request = RunReportRequest(
            property=f"properties/{GA_PROPERTY_ID}",
            dimensions=[Dimension(name="city")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")]
        )
        response = ga_client.run_report(request)
        
        dados_formatados = []
        for row in response.rows:
            cidade = row.dimension_values[0].value
            usuarios = row.metric_values[0].value
            dados_formatados.append(f"{cidade}: {usuarios} usuários ativos")
        
        return "\n".join(dados_formatados)
    except Exception as e:
        print(f"Erro ao obter dados do Google Analytics: {e}")
        return None

def gerar_resposta_bot(mensagens: list) -> str:
    mensagem_system = """Você é um assistente chamado Dip e trabalha para a empresa Diponto.
                         Você tem 4 perfis diferentes: marketing, suporte, vendas e financeiro, respondas as perguntas do usuario de acordo com o perfil.
                         No perfil de marketing, você deve responder perguntas relacionadas a marketing, campanhas e estratégias de vendas, não responda perguntas sobre suporte, vendas ou financeiro.
                         No perfil de suporte, você deve responder perguntas relacionadas a suporte técnico e atendimento ao cliente, não responda perguntas sobre marketing, vendas ou financeiro.
                         No perfil de vendas, você deve responder perguntas relacionadas a vendas, produtos e serviços, não responda perguntas sobre marketing, suporte ou financeiro.
                         No perfil financeiro, você deve responder perguntas relacionadas a finanças, contabilidade e relatórios financeiros, não responda perguntas sobre marketing, suporte ou vendas.
                         Você deve responder perguntas e ajudar os usuários com informações relevantes.
                         Você deve sempre usar informações do arquivo de base de conhecimento, se fazem uma pergunta que a resposta não esteja na sua base de conhecimento, diga que não tem a resposta ou peça para que o usuario troque para o perfil mais adequado com a pergunta.
                         Você tem acesso a dados do Google Analytics atualizados.
                         Você nunca deve responder perguntas pessoais ou fornecer informações que não sejam relevantes.
                         Dados recentes do Google Analytics serão fornecidos abaixo:"""
    dados_ga = obter_dados_google_analytics()
    if dados_ga:
        mensagem_system += f"\n{dados_ga}"
    
    mensagens_modelo = [{"role": "system", "content": mensagem_system}]
    mensagens_modelo += [{"role": role, "content": content} for role, content in mensagens]

    # Adicionar base de conhecimento
    for item in BASE_CONHECIMENTO.get("conhecimento", []):
        if "pergunta" in item and "resposta" in item:
            mensagens_modelo.append({"role": "system", "content": f"Pergunta: {item['pergunta']} Resposta: {item['resposta']}"})
    
    # Adicionar dados do Resumo_dos_relatórios.json
    if RESUMO_RELATORIOS:
        mensagens_modelo.append({"role": "system", "content": f"Dados do Resumo dos Relatórios: {json.dumps(RESUMO_RELATORIOS, ensure_ascii=False)}"})

    response = deepseek_client.chat.completions.create(
        model="deepseek-chat", 
        messages=mensagens_modelo, 
        stream=False
    )

    return response.choices[0].message.content

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)