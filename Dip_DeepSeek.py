import flet as ft
from openai import OpenAI
import json
import os

DEEPSEEK_API_KEY = "DEEPSEEK_API_KEY"
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

HISTORICO_ARQUIVO = "historico_conversas.json"
CONTEUDO_ARQUIVOS = {}

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

historico = carregar_historico()

def resposta_bot(mensagens: list[tuple[str, str]]) -> str:
    mensagem_system = """Você é um assistente chamado Dip e trabalha para a empresa Diponto."""
    
    mensagens_modelo = [{"role": "system", "content": mensagem_system}]
    mensagens_modelo += [{"role": role, "content": content} for role, content in mensagens]
    
    for nome_arquivo, conteudo in CONTEUDO_ARQUIVOS.items():
        mensagens_modelo.append({"role": "system", "content": f"Conteúdo do arquivo {nome_arquivo}: {conteudo}"})

    response = client.chat.completions.create(
        model="deepseek-chat", messages=mensagens_modelo, stream=False
    )

    return response.choices[0].message.content

def exibir_mensagem(role: str, conteudo: str) -> ft.Row:
    alinha_item = ft.MainAxisAlignment.CENTER
    cor_fundo = "#0084FF" if role == "user" else "#3E4042"
    cor_texto = "#FFFFFF"

    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(conteudo, color=cor_texto),
                padding=10,
                bgcolor=cor_fundo,
                border_radius=15,
                width=700,  # Ajuste a largura para centralizar melhor
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
        chat_area,
        progress_bar,
        ft.Row(
            [entrada_texto, botao_enviar],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        botao_upload,
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
