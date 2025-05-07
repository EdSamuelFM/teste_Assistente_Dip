document.addEventListener('DOMContentLoaded', function() {
    // Obter o perfil atual baseado na URL
    const path = window.location.pathname;
    let perfil = 'geral'; // padrão
    
    if (path.includes('marketing')) perfil = 'marketing';
    else if (path.includes('suporte')) perfil = 'suporte';
    else if (path.includes('vendas')) perfil = 'vendas';
    else if (path.includes('financeiro')) perfil = 'financeiro';
    else if (path.includes('dev')) perfil = 'dev';

    // Variáveis de controle de áudio
    window.audioContext = null;
    window.audioBufferSource = null;
    window.isAudioPlaying = false;
    
    // Ativar o link correspondente ao perfil atual
    document.querySelectorAll('.agente_mk, .agente_sp, .agente_vd, .agente_dv, .agente_fc').forEach(link => {
        link.classList.remove('active');
        if ((perfil === 'marketing' && link.classList.contains('agente_mk')) ||
            (perfil === 'suporte' && link.classList.contains('agente_sp')) ||
            (perfil === 'vendas' && link.classList.contains('agente_vd')) ||
            (perfil === 'financeiro' && link.classList.contains('agente_fc')) ||
            (perfil === 'dev' && link.classList.contains('agente_dv'))) {
            link.classList.add('active');
        }
    });
    
    // Elementos da interface
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatContainer = document.getElementById('chat-container');
    const clearHistoryButton = document.getElementById('clear-history-button');
    
    // Função para lidar com a troca de perfil
    function handleProfileChange(e) {
        try {
            e.preventDefault();
            const href = this.getAttribute('href');
            const newPerfil = href.replace('/', '');
            
            document.querySelectorAll('.agente_mk, .agente_sp, .agente_vd, .agente_dv, .agente_fc').forEach(link => {
                link.classList.remove('active');
            });
            this.classList.add('active');
            
            window.location.href = href;
        } catch (error) {
            console.error('Erro ao mudar perfil:', error);
        }
    }
    
    // Configura os listeners para os links de perfil
    document.querySelectorAll('.agente_mk, .agente_sp, .agente_vd, .agente_dv, .agente_fc').forEach(link => {
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
            
            const timeMatch = message.match(/\[Tempo de resposta: (.*?)\]/);
            let cleanMessage = message;
            let timeText = '';
            
            if (timeMatch) {
                cleanMessage = message.split('[Tempo de resposta:')[0].trim();
                timeText = `<div class="response-time">${timeMatch[0]}</div>`;
            }
            
            messageDiv.innerHTML = `
                <div class="message-content">${formatarMensagem(cleanMessage)}</div>
                ${timeText}
                ${sender === 'bot' ? '<div class="audio-control"><i class="fas fa-play"></i></div>' : ''}
            `;
            
            // Adiciona o event listener para o botão de áudio
            if (sender === 'bot') {
                const audioButton = messageDiv.querySelector('.audio-control');
                audioButton.addEventListener('click', function() {
                    playTextAsAudio(this);
                });
            }
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        } catch (error) {
            console.error('Erro ao adicionar mensagem:', error);
        }
    }

    // Função para reproduzir áudio
    window.playTextAsAudio = async function(element) {
        try {
            // Se já está tocando, para a reprodução
            if (window.isAudioPlaying) {
                if (window.audioBufferSource) {
                    window.audioBufferSource.stop();
                    window.audioContext.close();
                }
                element.innerHTML = '<i class="fas fa-play"></i>';
                window.isAudioPlaying = false;
                return;
            }
            
            element.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            const messageContent = element.parentElement.querySelector('.message-content').textContent;
            const cleanText = messageContent.replace(/\[.*?\]/g, '').trim();
            
            // Inicializa o contexto de áudio
            window.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Faz a requisição para o áudio
            const response = await fetch('/generate_audio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: cleanText })
            });
            
            if (!response.ok) {
                throw new Error('Erro ao gerar áudio');
            }
            
            const audioData = await response.arrayBuffer();
            const audioBuffer = await window.audioContext.decodeAudioData(audioData);
            
            // Cria e configura a fonte de áudio
            window.audioBufferSource = window.audioContext.createBufferSource();
            window.audioBufferSource.buffer = audioBuffer;
            window.audioBufferSource.connect(window.audioContext.destination);
            
            // Configura eventos
            window.audioBufferSource.onended = () => {
                element.innerHTML = '<i class="fas fa-play"></i>';
                window.isAudioPlaying = false;
                window.audioContext.close();
            };
            
            // Inicia reprodução
            window.audioBufferSource.start();
            element.innerHTML = '<i class="fas fa-stop"></i>';
            window.isAudioPlaying = true;
            
        } catch (error) {
            console.error('Erro ao reproduzir áudio:', error);
            element.innerHTML = '<i class="fas fa-play"></i>';
            showToast('Erro ao reproduzir mensagem: ' + error.message, 'error');
            
            if (window.audioContext) {
                window.audioContext.close();
            }
        }
    };
    // Função para parar a reprodução de áudio
    function stopAudio() {
        if (window.audioBufferSource) {
            window.audioBufferSource.stop();
            window.audioBufferSource.disconnect();
            window.audioBufferSource = null;
        }
        window.isAudioPlaying = false;
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
