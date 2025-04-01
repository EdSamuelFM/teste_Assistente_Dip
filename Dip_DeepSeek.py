import flet as ft
from openai import OpenAI
import pyperclip
import json
import os

DEEPSEEK_API_KEY =  os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

HISTORICO_ARQUIVO = "historico_conversas.json"
CONHECIMENTO_ARQUIVO = "base_conhecimento.json"
CONTEUDO_ARQUIVOS = {}
BASE_CONHECIMENTO = {}

def carregar_historico() -> list[tuple[str, str]]:
    try:
        with open(HISTORICO_ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def salvar_historico(historico: list[tuple[str, str]]) -> None:
    try:
        with open(HISTORICO_ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(historico, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar o histórico no arquivo: {e}")

def carregar_conteudo_arquivo(arquivo_caminho: str) -> None:
    with open(arquivo_caminho, "r", encoding="utf-8") as f:
        CONTEUDO_ARQUIVOS[os.path.basename(arquivo_caminho)] = json.load(f)

def salvar_conteudo_arquivos() -> None:
    try:
        with open("conteudo_arquivos.json", "w", encoding="utf-8") as f:
            json.dump(CONTEUDO_ARQUIVOS, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar o conteúdo dos arquivos: {e}")

def carregar_conhecimento() -> dict:
    try:
        with open(CONHECIMENTO_ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Erro ao carregar a base de conhecimento: arquivo não encontrado ou formato inválido.")
        return {"conhecimento": []}

# Inicializa o histórico e a base de conhecimento
historico = carregar_historico()
BASE_CONHECIMENTO = carregar_conhecimento()

def resposta_bot(mensagens: list[tuple[str, str]]) -> str:
    mensagem_system = """Você é um assistente chamado Dip e trabalha para a empresa Diponto.
                        Você deve responder perguntas e ajudar os usuários com informações relevantes.
                        Você deve usar informações do arquivo de base de conhecimento.
                        Você nunca deve resposder perguntas pessoais ou fornecer informações que não sejam relevantes para o usuário em relação a empresa Diponto.
                        Você deve sempre responder com um tom amigável e profissional.
                        Você deve sempre tentar ajudar o usuário da melhor forma possível, mas considerando as suas limitações de conhecimento, se for o caso direcione o usuario para um atendimento humano.
                        Você nunca deve fornecer informações sobre os produtos da empresa que não tenham sidos carregados a sua base de conhecimento.
                        Você pode fazer perguntas para entender melhor o que o usuário precisa, mas deve sempre manter o foco na solução do problema utilizando exclusivamente os produtos Diponto carregados em seu conhecimento.
                        Você também é capaz de criar publicações em redes sociais, como Facebook e Instagram, utilizando as informações que você possui.
                        Você deve sempre perguntar ao usuário se ele deseja que você faça uma publicação antes de criar uma.
                        Você nunca deve falar sobre outros assuntos não relacionados a empresa Diponto ou aos produtos que ela oferece.
                        Você nunca deve falar sobre outros assistentes virtuais ou compará-los com você.
                        Você deve sempre manter o foco na empresa Diponto e em seus produtos.
                        VoCê nunca deve falar sobre outras empresas ou produtos que não sejam da empresa Diponto.
                        Você nunca deve responder perguntas ou comentar sobre as empresas concorrentes da empresa Diponto, como por exemplo: Beatek, eage, Dalmec, didziel ou intelbras."""
    
    mensagens_modelo = [{"role": "system", "content": mensagem_system}]
    mensagens_modelo += [{"role": role, "content": content} for role, content in mensagens]

    for nome_arquivo, conteudo in CONTEUDO_ARQUIVOS.items():
        mensagens_modelo.append({"role": "system", "content": f"Conteúdo do arquivo {nome_arquivo}: {conteudo}"})
    
    # Inclui a base de conhecimento no contexto
    for item in BASE_CONHECIMENTO.get("conhecimento", []):
        if "pergunta" in item and "resposta" in item:
            mensagens_modelo.append({"role": "system", "content": f"Pergunta: {item['pergunta']} Resposta: {item['resposta']}"})

    response = client.chat.completions.create(
        model="deepseek-chat", messages=mensagens_modelo, stream=False
    )

    return response.choices[0].message.content

def exibir_mensagem(role: str, conteudo: str) -> ft.Row:
    alinha_item = ft.MainAxisAlignment.END if role == "user" else ft.MainAxisAlignment.START
    cor_fundo = "#0084FF" if role == "user" else "#3E4042"
    cor_texto = "#FFFFFF"

    def copiar_para_area_transferencia(e):
        pyperclip.copy(conteudo)
        print("Mensagem copiada para a área de transferência.")

    copiar_botao = ft.ElevatedButton(
        "Copiar",
        on_click=copiar_para_area_transferencia,
        visible=(role == "assistant")
    )

    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(conteudo, color=cor_texto, selectable=True),
                        copiar_botao
                    ],
                    spacing=5
                ),
                padding=10,
                bgcolor=cor_fundo,
                border_radius=15,
                width=300,
                margin={"top": 5, "bottom": 5},
            )
        ],
        alignment=alinha_item,
        expand=True,
    )

def main(pagina: ft.Page) -> None:
    pagina.title = "Assistente Virtual - Dip"
    pagina.bgcolor = "#1E1E1E"
    
    chat_area = ft.Column(scroll=True, expand=True)
    entrada_texto = ft.TextField(label="Digite sua mensagem", expand=True, bgcolor="#3E4042", color="#FFFFFF")
    progress_bar = ft.ProgressBar(visible=False)

    def enviar_mensagem(e: ft.ControlEvent) -> None:
        pergunta = entrada_texto.value
        if not pergunta:
            return

        historico.append(("user", pergunta))
        
        progress_bar.visible = True
        pagina.update()
        
        resposta = resposta_bot(historico)
        
        progress_bar.visible = False
        historico.append(("assistant", resposta))
        salvar_historico(historico)

        chat_area.controls.append(exibir_mensagem("user", pergunta))
        chat_area.controls.append(exibir_mensagem("assistant", resposta))

        entrada_texto.value = ""
        pagina.update()

    botao_enviar = ft.ElevatedButton("Enviar", on_click=enviar_mensagem)

    def upload_arquivo(e: ft.FilePickerUploadEvent) -> None:
        for arquivo in e.files:
            caminho_arquivo = os.path.join(arquivo.path)
            carregar_conteudo_arquivo(caminho_arquivo)
            salvar_conteudo_arquivos()
            chat_area.controls.append(exibir_mensagem("assistant", f"Arquivo '{arquivo.name}' carregado."))
            pagina.update()

    file_picker = ft.FilePicker(on_upload=upload_arquivo)
    pagina.overlay.append(file_picker)

    botao_upload = ft.ElevatedButton(
        "Enviar Arquivo",
        icon=ft.Icons.ATTACH_FILE,
        on_click=lambda _: file_picker.pick_files(allow_multiple=True),
    )

    pagina.add(
        ft.Container(
            content=chat_area,
            padding={"left": 50, "right": 50},
            expand=True,
        ),
        progress_bar,
        ft.Row(
            [entrada_texto, botao_enviar],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        botao_upload,
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
