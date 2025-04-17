document.addEventListener('DOMContentLoaded', function() {
    // Obter o perfil atual baseado na URL
    const path = window.location.pathname;
    let perfil = 'geral'; // padrão
    
    if (path.includes('marketing')) perfil = 'marketing';
    else if (path.includes('suporte')) perfil = 'suporte';
    else if (path.includes('vendas')) perfil = 'vendas';
    else if (path.includes('financeiro')) perfil = 'financeiro';

    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatContainer = document.getElementById('chat-container');
    const clearHistoryButton = document.getElementById('clear-history-button');

    // Tratamento de erros de extensões
    window.addEventListener('error', function(e) {
        if (e.message.includes('lastError') || e.message.includes('message port closed')) {
            e.preventDefault();
            return false;
        }
    });

    // Função para lidar com a troca de perfil
    function handleProfileChange(e) {
        try {
            e.preventDefault();
            const href = this.getAttribute('href');
            const newPerfil = href.replace('/', '');
            perfil = newPerfil;
            carregarHistorico(perfil);
            window.history.pushState({}, '', href);
            
            // Atualiza a classe 'active' nos links
            document.querySelectorAll('.agente_mk, .agente_sp, .agente_vd, .agente_fc').forEach(link => {
                link.classList.remove('active');
            });
            this.classList.add('active');
        } catch (error) {
            console.error('Erro ao mudar perfil:', error);
        }
    }

    // Configura os listeners para os links de perfil
    document.querySelectorAll('.agente_mk, .agente_sp, .agente_vd, .agente_fc').forEach(link => {
        link.addEventListener('click', handleProfileChange);
    });

    // Listener para o botão de limpar histórico
    clearHistoryButton.addEventListener('click', function() {
        try {
            if (!confirm('Tem certeza que deseja limpar todo o histórico de conversas?')) {
                return;
            }
            
            fetch('/chat/limpar_historico', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ perfil: perfil })
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
        } catch (error) {
            console.error('Erro no click handler:', error);
        }
    });

    // Carrega o histórico ao iniciar
    carregarHistorico(perfil);

    function carregarHistorico(perfil) {
        try {
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
        } catch (error) {
            console.error('Erro em carregarHistorico:', error);
        }
    }

    function addMessage(sender, message) {
        try {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            messageDiv.innerHTML = formatarMensagem(message);
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        } catch (error) {
            console.error('Erro ao adicionar mensagem:', error);
        }
    }

    function formatarMensagem(texto) {
        try {
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
        } catch (error) {
            console.error('Erro ao formatar mensagem:', error);
            return texto || '';
        }
    }

    function addTypingIndicator() {
        try {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot typing-indicator';
            typingDiv.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
            chatContainer.appendChild(typingDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return typingDiv;
        } catch (error) {
            console.error('Erro ao adicionar indicador de digitação:', error);
            return null;
        }
    }

    function showLoadingIndicator() {
        // Implemente conforme necessário
    }

    function hideLoadingIndicator() {
        // Implemente conforme necessário
    }

    function showToast(message, type = 'success') {
        console.log(`${type}: ${message}`);
        // Implemente um sistema de toast melhor se necessário
        alert(message);
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
        try {
            const message = chatInput.value.trim();
            if (!message) return;

            addMessage('user', message);
            chatInput.value = '';

            const typingDiv = addTypingIndicator();

            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `message=${encodeURIComponent(message)}&perfil=${perfil}`
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

            if (typingDiv) {
                typingDiv.remove();
            }
            addMessage('bot', data.response);
            
        } catch (error) {
            console.error('Erro:', error);
            const typingDiv = document.querySelector('.typing-indicator');
            if (typingDiv) {
                typingDiv.remove();
            }
            addMessage('bot', `Desculpe, ocorreu um erro: ${error.message}`);
        }
    }
});
