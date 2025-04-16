document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatContainer = document.getElementById('chat-container');
    const clearHistoryButton = document.getElementById('clear-history-button');

    // Função para lidar com a troca de perfil
    function handleProfileChange(e) {
        e.preventDefault();
        window.location.href = this.href;
    }

    // Configura os listeners para os links de perfil
    document.querySelectorAll('.agente_mk, .agente_sp, .agente_vd, .agente_fc').forEach(link => {
        link.addEventListener('click', handleProfileChange);
    });

    // Listener para o botão de limpar histórico
    clearHistoryButton.addEventListener('click', function() {
        fetch('/chat/limpar_historico', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                chatContainer.innerHTML = '';
                alert('Histórico limpo com sucesso!');
            } else {
                alert('Erro ao limpar o histórico: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao limpar o histórico.');
        });
    });

    // Carrega o histórico ao iniciar
    carregarHistorico();

    function carregarHistorico() {
        fetch('/chat/historico')
            .then(response => response.json())
            .then(data => {
                data.forEach(msg => {
                    addMessage(msg.role === 'user' ? 'user' : 'bot', msg.content);
                });
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
        texto = texto.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        texto = texto.replace(/\*(.*?)\*/g, '<em>$1</em>');
        texto = texto.replace(/_(.*?)_/g, '<em>$1</em>');
        texto = texto.replace(/`(.*?)`/g, '<code>$1</code>');
        texto = texto.replace(/\n/g, '<br>');
        texto = texto.replace(/</g, '&lt;').replace(/>/g, '&gt;');
        
        const allowedTags = {
            '&lt;strong&gt;': '<strong>',
            '&lt;/strong&gt;': '</strong>',
            '&lt;em&gt;': '<em>',
            '&lt;/em&gt;': '</em>',
            '&lt;code&gt;': '<code>',
            '&lt;/code&gt;': '</code>',
            '&lt;br&gt;': '<br>'
        };
        
        Object.keys(allowedTags).forEach(escaped => {
            texto = texto.replace(new RegExp(escaped, 'g'), allowedTags[escaped]);
        });
        
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

    // Listener para o botão de enviar
    sendButton.addEventListener('click', enviarMensagem);

    // Listener para tecla Enter
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            enviarMensagem();
        }
    });

    function enviarMensagem() {
        const message = chatInput.value.trim();
        if (message) {
            addMessage('user', message);
            chatInput.value = '';

            const typingDiv = addTypingIndicator();

            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `message=${encodeURIComponent(message)}`
            })
            .then(response => response.json())
            .then(data => {
                typingDiv.remove();
                addMessage('bot', data.response);
            })
            .catch(error => {
                console.error('Erro:', error);
                typingDiv.remove();
                addMessage('bot', 'Desculpe, ocorreu um erro ao processar sua mensagem.');
            });
        }
    }
});
