import os
import json
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Configurações de caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'static', 'json')

# Verifica e cria diretório se não existir
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Lista de todos os seus arquivos JSON
ARQUIVOS_JSON = {
    'resumo': 'Resumo_dos_relatórios.json',
    'base': {
        'geral': 'base_conhecimento.json',
        'financeiro': 'base_conhecimento_financeiro.json',
        'marketing': 'base_conhecimento_marketing.json',
        'suporte': 'base_conhecimento_suporte.json',
        'vendas': 'base_conhecimento_vendas.json'
    },
    'historico': {
        'geral': 'historico_conversas.json',
        'financeiro': 'historico_conversas_financeiro.json',
        'marketing': 'historico_conversas_marketing.json',
        'suporte': 'historico_conversas_suporte.json',
        'vendas': 'historico_conversas_vendas.json'
    }
}

# Cria arquivos se não existirem
for perfil, arquivo in ARQUIVOS_JSON['historico'].items():
    path = os.path.join(DATA_DIR, arquivo)
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([], f)

for perfil, arquivo in ARQUIVOS_JSON['base'].items():
    path = os.path.join(DATA_DIR, arquivo)
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"conhecimento": []}, f)

resumo_path = os.path.join(DATA_DIR, ARQUIVOS_JSON['resumo'])
if not os.path.exists(resumo_path):
    with open(resumo_path, 'w', encoding='utf-8') as f:
        json.dump({}, f)

# Variável global para controle
HISTORICO_ARQUIVO = os.path.join(DATA_DIR, ARQUIVOS_JSON['historico']['geral'])
BASE_CONHECIMENTO_ARQUIVO = os.path.join(DATA_DIR, ARQUIVOS_JSON['base']['geral'])
RESUMO_ARQUIVO = os.path.join(DATA_DIR, ARQUIVOS_JSON['resumo'])

@app.route('/chat/historico')
def obter_historico():
    try:
        # Verifica qual perfil está ativo (você precisará implementar essa lógica)
        perfil = request.args.get('perfil', 'geral')
        arquivo_historico = HISTORICO_ARQUIVOS.get(perfil, HISTORICO_ARQUIVOS['geral'])
        
        if not os.path.exists(arquivo_historico):
            with open(arquivo_historico, 'w', encoding='utf-8') as f:
                json.dump([], f)
        
        with open(arquivo_historico, 'r', encoding='utf-8') as f:
            historico = json.load(f)
        
        if not isinstance(historico, list):
            historico = []
            
        return jsonify([{"role": role, "content": content} for role, content in historico])
    
    except Exception as e:
        print(f"Erro ao carregar histórico: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        message = request.form['message']
        
        # Carrega histórico atual
        with open(HISTORICO_ARQUIVO, 'r', encoding='utf-8') as f:
            historico = json.load(f)
        
        # Adiciona nova mensagem
        historico.append(("user", message))
        
        # Gera resposta (implemente sua lógica com OpenAI aqui)
        resposta = "Esta é uma resposta de exemplo"
        historico.append(("assistant", resposta))
        
        # Salva histórico atualizado
        with open(HISTORICO_ARQUIVO, 'w', encoding='utf-8') as f:
            json.dump(historico, f, ensure_ascii=False, indent=4)
        
        return jsonify({"response": resposta})
    
    except Exception as e:
        print(f"Erro no chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

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

def carregar_historico() -> list:
    try:
        with open(HISTORICO_ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

@app.route('/chat/historico')
def obter_historico():
    try:
        historico = carregar_historico()
        historico_formatado = [{"role": role, "content": content} for role, content in historico]
        return jsonify(historico_formatado)
    except Exception as e:
        print(f"Erro ao carregar histórico: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

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
    # Garante que os arquivos existam
    for arquivo in HISTORICO_ARQUIVOS.values():
        if not os.path.exists(arquivo):
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
