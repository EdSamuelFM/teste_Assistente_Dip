import os
import json
import traceback
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

# Lista de arquivos JSON
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

# Inicializa arquivos se não existirem
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

# Configuração do cliente DeepSeek
deepseek_client = OpenAI(
    api_key="DEEPSEEK_API_KEY",  # SUBSTITUA POR SUA CHAVE REAL
    base_url="https://api.deepseek.com/v1",
    timeout=30
)

# Rotas principais
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/marketing')
def marketing():
    return render_template('marketing.html')

@app.route('/suporte')
def suporte():
    return render_template('suporte.html')

@app.route('/financeiro')
def financeiro():
    return render_template('financeiro.html')

@app.route('/vendas')
def vendas():
    return render_template('vendas.html')

# Rotas de API
@app.route('/chat/historico')
def obter_historico():
    try:
        perfil = request.args.get('perfil', 'geral')
        arquivo_historico = os.path.join(DATA_DIR, ARQUIVOS_JSON['historico'].get(perfil, ARQUIVOS_JSON['historico']['geral']))
        
        if not os.path.exists(arquivo_historico):
            with open(arquivo_historico, 'w', encoding='utf-8') as f:
                json.dump([], f)
        
        with open(arquivo_historico, 'r', encoding='utf-8') as f:
            historico = json.load(f)
        
        return jsonify([{"role": role, "content": content} for role, content in historico])
    
    except Exception as e:
        print(f"Erro ao carregar histórico: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        message = request.form['message']
        perfil = request.form.get('perfil', 'geral')
        
        # Carrega arquivos
        arquivo_historico = os.path.join(DATA_DIR, ARQUIVOS_JSON['historico'].get(perfil, ARQUIVOS_JSON['historico']['geral']))
        arquivo_base = os.path.join(DATA_DIR, ARQUIVOS_JSON['base'].get(perfil, ARQUIVOS_JSON['base']['geral']))
        resumo_path = os.path.join(DATA_DIR, ARQUIVOS_JSON['resumo'])
        
        # Garante que os arquivos existem
        for arquivo in [arquivo_historico, arquivo_base, resumo_path]:
            if not os.path.exists(arquivo):
                with open(arquivo, 'w', encoding='utf-8') as f:
                    json.dump({"conhecimento": []} if "base" in arquivo else [], f)
        
        # Carrega dados
        with open(arquivo_historico, 'r', encoding='utf-8') as f:
            historico = json.load(f)
        
        with open(arquivo_base, 'r', encoding='utf-8') as f:
            base_conhecimento = json.load(f)
        
        with open(resumo_path, 'r', encoding='utf-8') as f:
            resumo_relatorios = json.load(f)
        
        # Adiciona mensagem ao histórico
        historico.append(("user", message))
        
        # Gera resposta
        resposta = gerar_resposta_bot(
            mensagens=historico,
            base_conhecimento=base_conhecimento,
            resumo_relatorios=resumo_relatorios,
            perfil=perfil
        )
        
        # Atualiza histórico
        historico.append(("assistant", resposta))
        
        with open(arquivo_historico, 'w', encoding='utf-8') as f:
            json.dump(historico, f, ensure_ascii=False, indent=4)
        
        return jsonify({"response": resposta})
    
    except Exception as e:
        print(f"ERRO NO CHAT: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat/limpar_historico', methods=['POST'])
def limpar_historico():
    try:
        perfil = request.json.get('perfil', 'geral')
        arquivo_historico = os.path.join(DATA_DIR, ARQUIVOS_JSON['historico'].get(perfil, ARQUIVOS_JSON['historico']['geral']))
        
        with open(arquivo_historico, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Erro ao limpar o histórico: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Funções auxiliares
def gerar_resposta_bot(mensagens: list, base_conhecimento: dict, resumo_relatorios: dict, perfil: str) -> str:
    try:
        # Configura a mensagem do sistema baseada no perfil
        perfis = {
            'marketing': "Você é um assistente especializado em marketing da empresa Diponto. Responda apenas perguntas sobre marketing, campanhas e estratégias.",
            'suporte': "Você é um assistente especializado em suporte técnico da empresa Diponto. Responda apenas perguntas técnicas e de suporte.",
            'vendas': "Você é um assistente especializado em vendas da empresa Diponto. Responda apenas perguntas sobre produtos, serviços e vendas.",
            'financeiro': "Você é um assistente especializado em finanças da empresa Diponto. Responda apenas perguntas sobre relatórios financeiros e contabilidade.",
            'geral': "Você é o assistente geral da empresa Diponto."
        }
        
        mensagem_system = f"""{perfis.get(perfil, perfis['geral'])}
        Use as informações da base de conhecimento fornecida.
        Se não souber a resposta, diga que não tem a informação.
        Dados relevantes serão fornecidos abaixo:"""
        
        # Adiciona base de conhecimento formatada
        if base_conhecimento.get("conhecimento"):
            mensagem_system += "\n\nBase de Conhecimento:\n" + \
                "\n".join([f"Pergunta: {item.get('pergunta', '')}\nResposta: {item.get('resposta', '')}\n" 
                          for item in base_conhecimento["conhecimento"] if item.get('pergunta')])
        
        # Adiciona resumo de relatórios
        if resumo_relatorios:
            mensagem_system += "\n\nResumo de Relatórios:\n" + json.dumps(resumo_relatorios, ensure_ascii=False, indent=2)
        
        # Prepara mensagens para a API
        mensagens_api = [{"role": "system", "content": mensagem_system}]
        
        # Adiciona histórico de conversa
        for role, content in mensagens:
            mensagens_api.append({"role": "assistant" if role == "assistant" else "user", "content": content})
        
        print(f"Enviando para DeepSeek: {json.dumps(mensagens_api, indent=2)}")
        
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=mensagens_api,
            stream=False,
            temperature=0.7
        )
        
        print(f"Resposta da DeepSeek: {response}")
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"ERRO NA GERAÇÃO DE RESPOSTA: {traceback.format_exc()}")
        return "Desculpe, ocorreu um erro ao processar sua solicitação."

# Rota de teste da API
@app.route('/teste-api', methods=['GET'])
def teste_api():
    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Responda com 'OK' se estiver funcionando"}],
            stream=False
        )
        return jsonify({"status": "success", "response": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Rota para resetar arquivos (apenas para desenvolvimento)
@app.route('/reset-arquivos', methods=['POST'])
def reset_arquivos():
    try:
        for perfil in ARQUIVOS_JSON['historico']:
            path = os.path.join(DATA_DIR, ARQUIVOS_JSON['historico'][perfil])
            with open(path, 'w', encoding='utf-8') as f:
                json.dump([], f)
        
        for perfil in ARQUIVOS_JSON['base']:
            path = os.path.join(DATA_DIR, ARQUIVOS_JSON['base'][perfil])
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({"conhecimento": []}, f)
        
        with open(os.path.join(DATA_DIR, ARQUIVOS_JSON['resumo']), 'w', encoding='utf-8') as f:
            json.dump({}, f)
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
