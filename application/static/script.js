$(function() {
    let currentChatId = null;
    
    // 生成唯一ID
    function generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    // 获取所有对话
    function getChats() {
        return JSON.parse(localStorage.getItem('chats') || '[]');
    }

    // 保存对话列表
    function saveChats(chats) {
        localStorage.setItem('chats', JSON.stringify(chats));
    }

    // 获取单个对话内容
    function getChatMessages(chatId) {
        return JSON.parse(localStorage.getItem(`chat_${chatId}`) || '[]');
    }

    // 保存单个对话内容
    function saveChatMessages(chatId, messages) {
        localStorage.setItem(`chat_${chatId}`, JSON.stringify(messages));
    }

    // 渲染对话历史
    function renderChatHistory() {
        const chats = getChats();
        const $history = $('#chat-history');
        
        $history.empty();
        chats.forEach(chat => {
            const $item = $('<div>')
                .addClass('chat-history-item')
                .toggleClass('active', chat.id === currentChatId)
                .append(
                    $('<span>')
                        .addClass('chat-title')
                        .text(chat.isNew ? chat.title : `Old: ${chat.title}`), // 新对话无 Old:
                    $('<button>')
                        .addClass('delete-chat')
                        .html('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>')
                        .on('click', (e) => {
                            e.stopPropagation();
                            deleteChat(chat.id);
                        })
                )
                .on('click', () => {
                    loadChat(chat.id);
                    // 根据是否是老对话隐藏输入框
                    if (chat.isNew) {
                        $('.input-container').show();
                    } else {
                        $('.input-container').hide();
                    }
                });

            $history.append($item);
            
        });

    }

    // 开始新对话
    function startNewChat() {
        const chatId = generateId();
        const newChat = {
            id: chatId,
            title: 'New Chat',
            createdAt: new Date().toISOString(),
            isNew: true // 标记为新对话
        };
        
        const chats = getChats();

        // 将所有现有对话标记为老对话
        chats.forEach(chat => chat.isNew = false);
        chats.push(newChat);
        saveChats(chats);

        saveChatMessages(chatId, [{
            type: 'bot',
            content: 'Hello, anything I can help？😊\n\nPlease upload your file before we can start.',
            timestamp: new Date().toISOString()
        }]);

        $.ajax({
            url: '/kill', // app.py kill
            type: 'POST',        
            success: function(response) {
                alert("New Chat created! Everything reset! History saved.");
            },
            error: function(xhr, status, error) {
                alert("Error: " + error);
                return;
            }
        });

        loadChat(chatId);
        // 显示输入框容器
        $('.input-container').show();

    }

    // 加载对话
    function loadChat(chatId) {
        currentChatId = chatId;
        const messages = getChatMessages(chatId);
        
        const $messages = $('#messages');
        $messages.empty();
        
        messages.forEach(msg => {
            $messages.append(
                $('<div>')
                    .addClass(`message ${msg.type}-message`)
                    .text(msg.content)
            );
        });

        // 显示或隐藏输入框容器
        const chats = getChats();
        const chat = chats.find(chat => chat.id === chatId);
        if (chat && chat.isNew) {
            $('.input-container').show();
        } else {
            $('.input-container').hide();
        }
 
        $('#user-input-text').val('');
        renderChatHistory();
        scrollToBottom();

    }

    // 删除对话
    function deleteChat(chatId) {
        if (!confirm('Really delete this conversation?')) {
            return;
        }
        
        const chats = getChats();
        const index = chats.findIndex(chat => chat.id === chatId);
        if (index !== -1) {
            chats.splice(index, 1);
            saveChats(chats);
            localStorage.removeItem(`chat_${chatId}`);
            
            if (currentChatId === chatId) {
                if (chats.length > 0) {
                    loadChat(chats[chats.length - 1].id);
                } else {
                    startNewChat();
                }
            } else {
                renderChatHistory();
            }
        }
    }

    // 更新对话标题
    function updateChatTitle(chatId, firstMessage) {
        const chats = getChats();
        const chat = chats.find(c => c.id === chatId);
        if (chat) {
            chat.title = firstMessage.slice(0, 20) + (firstMessage.length > 20 ? '...' : '');
            saveChats(chats);
            renderChatHistory();
        }
    }

    // 滚动到底部
    function scrollToBottom() {
        const $messages = $('#messages');
        $messages.animate({ 
            scrollTop: $messages.prop("scrollHeight") 
        }, 1000);
    }

    // 初始化
    function initialize() {
        const chats = getChats();
        if (chats.length > 0) {
            loadChat(chats[chats.length - 1].id);
        } else {
            startNewChat();
        }
    }

    // 事件处理
    $('.new-chat-btn').on('click', startNewChat);

    $('#user-form').on('submit', function(event) {
        event.preventDefault();
        
        const $input = $('#user-input-text');
        const $submit = $('.submit-button');
        const userInput = $input.val().trim();
        
        if (!userInput) return;

        // 禁用输入和提交按钮
        $input.prop('disabled', true);
        $submit.prop('disabled', true);

        // 获取当前对话的消息
        const messages = getChatMessages(currentChatId);
        
        // 添加用户消息
        const userMessage = {
            type: 'user',
            content: userInput,
            timestamp: new Date().toISOString()
        };
        messages.push(userMessage);

        // 如果是第一条用户消息，更新对话标题
        if (messages.filter(m => m.type === 'user').length === 1) {
            updateChatTitle(currentChatId, userInput);
        }

        // 更新界面
        $('#messages').append(
            $('<div>')
                .addClass('message user-message')
                .text(userInput)
        );

        // 添加思考中消息
        const $thinkingMsg = $('<div>')
            .addClass('message bot-message')
            .text('Thinking...');
        $('#messages').append($thinkingMsg);

        scrollToBottom();

        // 发送到后端
        $.ajax({
            type: 'POST',
            url: '/get_response',
            data: { user_input: userInput },
            success: function(response) {
                // 移除思考中消息
                $thinkingMsg.remove();

                // 添加机器人回复
                const botMessage = {
                    type: 'bot',
                    content: response,
                    timestamp: new Date().toISOString()
                };
                messages.push(botMessage);
                
                // 保存消息
                saveChatMessages(currentChatId, messages);
                
                // 更新界面
                $('#messages').append(
                    $('<div>')
                        .addClass('message bot-message')
                        .text(response)
                );
                
                scrollToBottom();
            },
            error: function() {
                $thinkingMsg.text('Failed to send message，please retry');
            },
            complete: function() {
                // 重新启用输入和提交按钮
                $input.prop('disabled', false).val('').focus();
                $submit.prop('disabled', false);
            }
        });
    });

    // 自动调整输入框高度
    $('#user-input-text').on('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // 初始化应用
    initialize();
});

$(document).ready(function() {
    const dropZone = $('#drop-zone');
    const fileList = $('.file-list');
    const progressBar = $('#progress-bar')
    let files = [];

    // 切换拖拽区域显示
    $('.input-container').on('click', '.toggle-upload', function() {
        dropZone.toggleClass('visible');
    });

    // 阻止默认拖拽行为
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone[0].addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // 拖拽效果
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone[0].addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone[0].addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.addClass('drag-over');
    }

    function unhighlight(e) {
        dropZone.removeClass('drag-over');
    }

    // 处理文件拖放
    dropZone[0].addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const newFiles = [...dt.files];
        handleFiles(newFiles);
    }

    // 处理文件
    function handleFiles(newFiles) {
        files = [...files, ...newFiles];
        updateFileList();
    }

    // 更新文件列表显示
    function updateFileList() {
        fileList.empty();
        files.forEach((file, index) => {
            const li = $('<li>').addClass('file-item');
            li.append(
                $('<span>').text(file.name),
                $('<span>').addClass('remove-file')
                    .text('×')
                    .on('click', () => removeFile(index))
            );
            fileList.append(li);
        });
    }

    // 移除文件
    function removeFile(index) {
        files.splice(index, 1);
        updateFileList();
    }

    // // 添加上传按钮到输入区域
    // $('.input-container').prepend(
    //     $('<button>')
    //         .addClass('toggle-upload')
    //         .text('📎 上传文件')
    // );

    // 添加消息到对话框
    function addMessage(content, isUser = false) {
        const messageDiv = $('<div>').addClass('message');
        if (isUser) {
            messageDiv.addClass('user-message');
        } else {
            messageDiv.addClass('bot-message');
        }
        messageDiv.text(content);
        $('#messages').append(messageDiv);
        
        // 滚动到最新消息
        $('#messages').scrollTop($('#messages')[0].scrollHeight);
    }

    // // 生成文件上传消息内容
    // function generateFileMessage(files) {
    //     if (files.length === 1) {
    //         return `File "${files[0].name}" has been uploaded successfully!`;
    //     } else {
    //         const fileNames = files.map(file => `"${file.name}"`).join('、');
    //         return `The follwing files have been uploaded succesfully：${fileNames}`;
    //     }
    // }

    // upload
    function uploadFiles() {
        if (files.length === 0) {
            alert('Please select file first！');
            return;
        }

        // no empty file
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (file.size == 0){
                alert(`Please upload no empty file: ${file.name}`);
                return;                
            }
        }

        const formData = new FormData();
        const uploadedFiles = [...files]; // 保存当前的文件列表副本
        files.forEach(file => {
            formData.append('file', file);
        });

        // 添加用户上传文件的消息
        addMessage(`Uploading ${files.length} files...`, true);

        $.ajax({
            url: '/save_upload',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            xhr: function() {
                const xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener('progress', function(e) {
                    if (e.lengthComputable) {
                        const percent = (e.loaded / e.total) * 100;
                        progressBar.css('width', percent + '%');
                    }
                }, false);
                return xhr;
            },
            success: function(response) {
                console.log("Upload successful:", response); // 添加日志
                // 添加系统回复消息
                // const successMessage = generateFileMessage(uploadedFiles);
                const successMessage = response.message;
                addMessage(successMessage, false);

                // 清理上传状态
                files = [];
                updateFileList();
                progressBar.css('width', '0%');
                dropZone.removeClass('visible')
            },
            error: function(error) {
                // 添加错误消息
                addMessage(`Upload Failed：${error}`, false);
                progressBar.css('width', '0%');
            }
        });
    }

    // 取消上传
    function cancelUpload() {
        files = [];
        updateFileList();
        progressBar.css('width', '0%');
        dropZone.removeClass('visible');
    }

    // 绑定上传和取消按钮事件
    $('.upload-btn').on('click', uploadFiles);
    $('.cancel-btn').on('click', cancelUpload);

    // 添加上传按钮到输入区域
    $('.input-container').prepend(
        $('<button>')
            .addClass('toggle-upload')
            .text('📎 File Upload')
    );

    function triggerToggleUpload() {
        $('#toggle-upload').trigger('click');
    }

});
