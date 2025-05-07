import os
import time
import json
import traceback
from flask import Flask, make_response, render_template, request, jsonify, send_from_directory
from openai import OpenAI
from transformers import AutoProcessor, BarkModel
import torch
from scipy.io.wavfile import write as write_wav
import numpy as np
from datetime import datetime
import io
import wave
import numpy as np
import soundfile as sf




app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')



processor = None
bark_model = None
def load_bark_model():
    global processor, bark_model
    if processor is None or bark_model is None:
        print("Carregando modelo Bark...")
        processor = AutoProcessor.from_pretrained("suno/bark-small")
        bark_model = BarkModel.from_pretrained("suno/bark-small").to("cuda" if torch.cuda.is_available() else "cpu")
        print("Modelo Bark carregado!")

# Carrega o modelo e o processador Bark
processor = AutoProcessor.from_pretrained("suno/bark-small")
bark_model = BarkModel.from_pretrained("suno/bark-small").to("cuda" if torch.cuda.is_available() else "cpu")

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
        'vendas': 'base_conhecimento_vendas.json',
        'dev': 'base_conhecimento_dev.json'    
    },
    'historico': {
        'geral': 'historico_conversas.json',
        'financeiro': 'historico_conversas_financeiro.json',
        'marketing': 'historico_conversas_marketing.json',
        'suporte': 'historico_conversas_suporte.json',
        'vendas': 'historico_conversas_vendas.json',
        'dev': 'historico_conversas_dev.json'
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

# Configuração do DeepSeek
deepseek_client = OpenAI(
    api_key="sk-88c90c0c91c94912b276f19234eacc51",  
    base_url="https://api.deepseek.com/v1",
    timeout=20
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

@app.route('/dev')
def dev():
    return render_template('dev.html')

# Rota para evitar erro 404 do Flutter
@app.route('/flutter_service_worker.js')
def flutter_sw():
    return '', 204

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
        start_time = datetime.now()  # Inicia o timer
        
        message = request.form['message']
        perfil = request.form.get('perfil', 'geral')
        
        # Carrega arquivos
        arquivo_historico = os.path.join(DATA_DIR, ARQUIVOS_JSON['historico'].get(perfil, ARQUIVOS_JSON['historico']['geral']))
        arquivo_base = os.path.join(DATA_DIR, ARQUIVOS_JSON['base'].get(perfil, ARQUIVOS_JSON['base']['geral']))
        resumo_path = os.path.join(DATA_DIR, ARQUIVOS_JSON['resumo'])
        
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
        
        # Calcula o tempo de resposta
        response_time = (datetime.now() - start_time).total_seconds()
        
        # Adiciona tempo de resposta à mensagem
        resposta_com_tempo = f"{resposta}\n\n[Tempo de resposta: {response_time:.2f} segundos]"
        
        
        # Atualiza histórico
        historico.append(("assistant", resposta_com_tempo))
        
        with open(arquivo_historico, 'w', encoding='utf-8') as f:
            json.dump(historico, f, ensure_ascii=False, indent=4)
        
        return jsonify({
            "response": resposta_com_tempo,
            "response_time": response_time
        })
    
    except Exception as e:
        print(f"ERRO NO CHAT: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    try:
        load_bark_model()  # Carrega o modelo na primeira chamada
        
        text = request.json.get('text', '')
        clean_text = text.split('[Tempo de resposta:')[0].strip()
        
        if not clean_text:
            return jsonify({"error": "Texto não fornecido"}), 400
        
        # Gera áudio com Bark
        inputs = processor(clean_text, voice_preset="v2/pt_speaker_8", return_tensors="pt")
        audio_array = bark_model.generate(**inputs)
        audio_array = audio_array.cpu().numpy().squeeze()
        
        # Converte para formato compatível com navegadores
        buffer = io.BytesIO()
        sf.write(buffer, audio_array, bark_model.generation_config.sample_rate, format='WAV')
        buffer.seek(0)
        
        # Retorna o áudio
        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'audio/wav'
        response.headers['Content-Disposition'] = 'attachment; filename=speech.wav'
        return response
        
    except Exception as e:
        print(f"ERRO NA GERAÇÃO DE ÁUDIO: {traceback.format_exc()}")
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
            'marketing': "Você é um assistente especializado em marketing da empresa Diponto.",
            'suporte': "Você é um assistente especializado em suporte técnico da empresa Diponto.",
            'vendas': "Você é um assistente especializado em vendas da empresa Diponto.",
            'financeiro': "Você é um assistente especializado em finanças da empresa Diponto.",
            'geral': "Você é o assistente geral da empresa Diponto.",
            'dev': "Você é um assistente especializado em desenvolvimento de landing pagesdos produtos Diponto."
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
            temperature=0.7,
            timeout=300.0
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
            max_tokens=10
        )
        return jsonify({"status": "success", "response": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
