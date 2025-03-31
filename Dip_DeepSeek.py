import flet as ft
from openai import OpenAI
import json
import os

# Chave da API da DeepSeek
DEEPSEEK_API_KEY = "sk-88c90c0c91c94912b276f19234eacc51"
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# Arquivo para histórico
HISTORICO_ARQUIVO = "historico_conversas.json"
CONTEUDO_ARQUIVOS = {}

def carregar_historico() -> list[tuple[str, str]]:
    """Carrega o histórico de conversas de um arquivo JSON."""
    try:
        with open(HISTORICO_ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(
            f"Arquivo de histórico '{HISTORICO_ARQUIVO}' não encontrado."
            " Iniciando com histórico vazio."
        )
        return []
    except json.JSONDecodeError:
        print(
            f"Erro ao decodificar o arquivo JSON '{HISTORICO_ARQUIVO}'."
            " Verifique se o arquivo está formatado corretamente."
        )
        return []

def salvar_historico(historico: list[tuple[str, str]]) -> None:
    """Salva o histórico de conversas em um arquivo JSON."""
    try:
        with open(HISTORICO_ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(historico, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar o histórico no arquivo: {e}")

def carregar_conteudo_arquivo(arquivo_caminho: str) -> None:
    """Carrega o conteúdo de um arquivo JSON e armazena em CONTEUDO_ARQUIVOS."""
    with open(arquivo_caminho, "r", encoding="utf-8") as f:
        CONTEUDO_ARQUIVOS[os.path.basename(arquivo_caminho)] = json.load(f)

def salvar_conteudo_arquivos() -> None:
    """Salva o conteúdo dos arquivos em um arquivo JSON."""
    try:
        with open("conteudo_arquivos.json", "w", encoding="utf-8") as f:
            json.dump(CONTEUDO_ARQUIVOS, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar o conteúdo dos arquivos: {e}")

# Inicializa o histórico
historico = carregar_historico()

def resposta_bot(mensagens: list[tuple[str, str]]) -> str:
    """Gera uma resposta do bot usando a API da DeepSeek."""
    mensagem_system = """Você é um assistente chamado Dip e trabalha para a empresa Diponto.
    Suas respostas não devem ser imaginativas, se baseie apenas em seu conhecimento.
    Suas publicações devem variar entre publicações divertidas, informativas, objetivas e raramente genéricas, não deve ultrapassar 15 linhas e nunca repetir uma publicação que você já criou."""

    mensagens_modelo = [{"role": "system", "content": mensagem_system}]
    mensagens_modelo += [
        {"role": role, "content": content} for role, content in mensagens
    ]
    # Adiciona o conteúdo dos arquivos ao contexto
    for nome_arquivo, conteudo in CONTEUDO_ARQUIVOS.items():
        mensagens_modelo.append({"role": "system", "content": f"Conteúdo do arquivo {nome_arquivo}: {conteudo}"})

    response = client.chat.completions.create(
        model="deepseek-chat", messages=mensagens_modelo, stream=False
    )

    return response.choices[0].message.content

def exibir_mensagem(role: str, conteudo: str) -> ft.Row:
    """Cria uma caixa de diálogo estilizada para as mensagens distribuídas na tela."""
    alinha_item = ft.MainAxisAlignment.END if role == "user" else ft.MainAxisAlignment.START
    cor_fundo = "#D3D3D3" if role == "user" else "#FFB700"

    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(conteudo),
                padding=10,
                bgcolor=cor_fundo,
                border_radius=5,
                width=300,  # Ajusta a largura das mensagens
            )
        ],
        alignment=alinha_item,
        expand=True,
    )

def main(pagina: ft.Page) -> None:
    """Configura a interface gráfica do assistente virtual."""
    pagina.title = "Assistente Virtual - Dip"

    # Interface do chat
    chat_area = ft.Column(scroll=True, expand=True)

    # Campo de entrada para o usuário
    entrada_texto = ft.TextField(label="Digite sua mensagem", expand=True)

    def enviar_mensagem(e: ft.ControlEvent) -> None:
        """Envia a mensagem do usuário e exibe a resposta do bot."""
        pergunta = entrada_texto.value
        if not pergunta:
            return

        historico.append(("user", pergunta))
        resposta = resposta_bot(historico)
        historico.append(("assistant", resposta))
        salvar_historico(historico)

        # Adiciona as mensagens na interface
        chat_area.controls.append(exibir_mensagem("user", pergunta))
        chat_area.controls.append(exibir_mensagem("assistant", resposta))

        entrada_texto.value = ""
        pagina.update()

    # Botão para enviar a mensagem
    botao_enviar = ft.ElevatedButton("Enviar", on_click=enviar_mensagem)

    # Campo de upload de arquivos
    def upload_arquivo(e: ft.FilePickerUploadEvent) -> None:
        """Carrega o conteúdo do arquivo enviado."""
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

    # Layout da página
    pagina.add(
        chat_area,
        ft.Row(
            [entrada_texto, botao_enviar],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        botao_upload,
    )

# Inicializa o aplicativo Flet
if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
