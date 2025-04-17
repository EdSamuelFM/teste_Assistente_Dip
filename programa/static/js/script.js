document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatContainer = document.getElementById('chat-container');
    const clearHistoryButton = document.getElementById('clear-history-button');

function handleProfileChange(e) {
    e.preventDefault();
    const href = this.getAttribute('href');
    const perfil = href.replace('/', ''); // Extrai o perfil da URL
    carregarHistorico(perfil);
    window.history.pushState({}, '', href);
    // Atualiza a classe 'active' nos links
    document.querySelectorAll('.agente_mk, .agente_sp, .agente_vd, .agente_fc').forEach(link => {
        link.classList.remove('active');
    });
    this.classList.add('active');
}
 // Obter o perfil atual baseado na URL
    const path = window.location.pathname;
    let perfil = 'geral'; // padrão
    
    if (path.includes('marketing')) perfil = 'marketing';
    else if (path.includes('suporte')) perfil = 'suporte';
    else if (path.includes('vendas')) perfil = 'vendas';
    else if (path.includes('financeiro')) perfil = 'financeiro';
    
    
    
    // Configura os listeners para os links de perfil
    document.querySelectorAll('.agente_mk, .agente_sp, .agente_vd, .agente_fc').forEach(link => {
        link.addEventListener('click', handleProfileChange);
    });

    // Listener para o botão de limpar histórico
    clearHistoryButton.addEventListener('click', function() {
        if (!confirm('Tem certeza que deseja limpar todo o histórico de conversas?')) {
            return;
        }
        
        fetch('/chat/limpar_historico', {
            method: 'POST',
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao limpar histórico');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === "success") {
                chatContainer.innerHTML = '';
                showToast('Histórico limpo com sucesso!');
            } else {
                throw new Error(data.message || 'Erro desconhecido');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            showToast('Erro ao limpar o histórico: ' + error.message, 'error');
        });
    });

    // Carrega o histórico ao iniciar
    carregarHistorico(perfil);

    function carregarHistorico(perfil) {
        showLoadingIndicator();
        
        fetch(`/chat/historico?perfil=${perfil}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao carregar histórico');
            }
            return response.json();
        })
        .then(data => {
            if (!Array.isArray(data)) {
                throw new Error('Formato de histórico inválido');
            }
            
            chatContainer.innerHTML = '';
            data.forEach(msg => {
                if (msg.role && msg.content) {
                    addMessage(msg.role, msg.content);
                }
            });
        })
        .catch(error => {
            console.error('Erro ao carregar histórico:', error);
            addMessage('bot', 'Não foi possível carregar o histórico de conversas.');
        })
        .finally(() => {
            hideLoadingIndicator();
        });
}

    function addMessage(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.innerHTML = formatarMensagem(message);
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function formatarMensagem(texto) {
        if (!texto) return '';
        
        // Proteção XSS primeiro
        texto = texto.toString()
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        
        // Formatação de markdown
        texto = texto
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/_(.*?)_/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
        
        return texto;
    }

    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot typing-indicator';
        typingDiv.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
        chatContainer.appendChild(typingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return typingDiv;
    }

    function showLoadingIndicator() {
        // Implemente um indicador de carregamento se necessário
    }

    function hideLoadingIndicator() {
        // Implemente a ocultação do indicador
    }

    function showToast(message, type = 'success') {
        // Implemente um sistema de notificação/toast
        console.log(`${type}: ${message}`);
        alert(message); // Temporário - substitua por um toast bonito
    }

    // Listener para o botão de enviar
    sendButton.addEventListener('click', enviarMensagem);

    // Listener para tecla Enter
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            enviarMensagem();
        }
    });

    async function enviarMensagem() {
        const message = chatInput.value.trim();
        if (!message) return;

        addMessage('user', message);
        chatInput.value = '';

        const typingDiv = addTypingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `message=${encodeURIComponent(message)}`
            });

            if (!response.ok) {
                throw new Error('Erro no servidor');
            }

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            if (!data.response) {
                throw new Error('Resposta inválida do servidor');
            }

            typingDiv.remove();
            addMessage('bot', data.response);
            
        } catch (error) {
            console.error('Erro:', error);
            typingDiv.remove();
            addMessage('bot', `Desculpe, ocorreu um erro: ${error.message}`);
        }
    }
});
