// 全局状态
let socket = null;
let currentUserId = null;
let currentUserName = null;
let currentConversationId = null;
let currentReceiverId = null; 
let currentUserIsAdmin = false;

// DOM元素引用（在DOMContentLoaded中初始化）
let messageArea, messageInput, sendButton, conversationList, contactNameDisplay;
let loginScreen, chatApp, loginButton, loginUsername, loginPassword;
let logoutButton, searchFriendInput, addFriendButton;
// 注册相关元素
let loginTab, registerTab, loginForm, registerForm, registerButton;
let registerUsername, registerPassword, registerConfirmPassword;
// 管理员相关元素
let adminPanelButton, adminPanel, closeAdminPanelButton, userTableBody;
// 清空聊天记录按钮
let clearChatButton;

// 初始化事件监听
document.addEventListener('DOMContentLoaded', () => {
    // 初始化DOM元素引用
    messageArea = document.getElementById('message-area');
    messageInput = document.getElementById('message-input');
    sendButton = document.getElementById('send-button');
    conversationList = document.getElementById('conversation-list');
    contactNameDisplay = document.getElementById('current-contact-name');
    loginScreen = document.getElementById('login-screen');
    chatApp = document.getElementById('chat-app');
    loginButton = document.getElementById('login-button');
    loginUsername = document.getElementById('login-username');
    loginPassword = document.getElementById('login-password');
    logoutButton = document.getElementById('logout-button');
    searchFriendInput = document.getElementById('search-friend');
    addFriendButton = document.getElementById('add-friend-button');
    
    // 初始化注册相关DOM元素
    loginTab = document.getElementById('login-tab');
    registerTab = document.getElementById('register-tab');
    loginForm = document.getElementById('login-form');
    registerForm = document.getElementById('register-form');
    registerButton = document.getElementById('register-button');
    registerUsername = document.getElementById('register-username');
    registerPassword = document.getElementById('register-password');
    registerConfirmPassword = document.getElementById('register-confirm-password');
    
    // 初始化管理员相关DOM元素
    adminPanelButton = document.getElementById('admin-panel-button');
    adminPanel = document.getElementById('admin-panel');
    closeAdminPanelButton = document.getElementById('close-admin-panel');
    userTableBody = document.getElementById('user-table-body');
    
    // 初始化清空聊天记录按钮
    clearChatButton = document.getElementById('clear-chat-button');
    
    // 添加事件监听
    loginButton.addEventListener('click', handleLogin);
    logoutButton.addEventListener('click', handleLogout);
    addFriendButton.addEventListener('click', handleAddFriend);
    clearChatButton.addEventListener('click', handleClearChat);
    
    // 注册相关事件监听
    loginTab.addEventListener('click', () => switchTab('login'));
    registerTab.addEventListener('click', () => switchTab('register'));
    registerButton.addEventListener('click', handleRegister);
    
    // 按下Enter键也可以登录或注册
    loginPassword.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleLogin();
        }
    });
    registerConfirmPassword.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleRegister();
        }
    });
    
    // 管理员面板相关事件监听
    adminPanelButton.addEventListener('click', openAdminPanel);
    closeAdminPanelButton.addEventListener('click', closeAdminPanel);
    
    // 消息发送事件监听
    sendButton.addEventListener('click', handleSendMessage);
    // 回车键发送消息
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    });
});

// --- 注册相关功能 ---
function switchTab(tabName) {
    // 重置所有标签和表单
    loginTab.classList.remove('bg-blue-500', 'text-white');
    loginTab.classList.add('bg-gray-200', 'text-gray-700');
    registerTab.classList.remove('bg-blue-500', 'text-white');
    registerTab.classList.add('bg-gray-200', 'text-gray-700');
    loginForm.classList.add('hidden');
    registerForm.classList.add('hidden');
    
    // 激活选中的标签和表单
    if (tabName === 'login') {
        loginTab.classList.add('bg-blue-500', 'text-white');
        loginTab.classList.remove('bg-gray-200', 'text-gray-700');
        loginForm.classList.remove('hidden');
    } else if (tabName === 'register') {
        registerTab.classList.add('bg-blue-500', 'text-white');
        registerTab.classList.remove('bg-gray-200', 'text-gray-700');
        registerForm.classList.remove('hidden');
    }
}

async function handleRegister() {
    const username = registerUsername.value.trim();
    const password = registerPassword.value.trim();
    const confirmPassword = registerConfirmPassword.value.trim();
    
    // 表单验证
    if (!username || !password || !confirmPassword) {
        alert('请填写所有字段');
        return;
    }
    
    if (password !== confirmPassword) {
        alert('两次输入的密码不一致');
        return;
    }
    
    if (password.length < 3) {
        alert('密码长度不能少于3个字符');
        return;
    }
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, password: password })
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log(`User ${username} registered successfully.`);
            
            // 注册成功后自动切换到登录表单
            switchTab('login');
            alert('注册成功，请登录');
            
            // 清空注册表单
            registerUsername.value = '';
            registerPassword.value = '';
            registerConfirmPassword.value = '';
            
            // 自动填充用户名到登录表单
            loginUsername.value = username;
        } else {
            const error = await response.json();
            alert(`注册失败: ${error.message}`);
        }
    } catch (error) {
        console.error('Register error:', error);
        alert('注册时发生错误，请检查服务器连接');
    }
}

// --- 辅助函数：登录/初始化 ---
async function handleLogin() {
    const username = loginUsername.value.trim();
    const password = loginPassword.value.trim();
    
    if (!username || !password) {
        alert('请输入用户名和密码');
        return;
    }
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, password: password })
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log(`User ${username} logged in successfully.`);
            currentUserId = data.user_id;
            currentUserName = data.username;
            currentUserIsAdmin = data.is_admin;
            
            // 隐藏登录界面，显示聊天界面
            loginScreen.classList.add('hidden');
            chatApp.classList.remove('hidden');
            
            // 更新当前用户名显示
            document.getElementById('current-user-name').textContent = currentUserName;
            
            // 根据管理员状态显示或隐藏管理员面板按钮
            if (currentUserIsAdmin) {
                adminPanelButton.classList.remove('hidden');
            } else {
                adminPanelButton.classList.add('hidden');
            }
            
            // 初始化Socket和加载会话
            if (socket) socket.disconnect();
            initSocket();
            await loadConversations();
            
            // 清空登录表单
            loginUsername.value = '';
            loginPassword.value = '';
            
            // 启用发送按钮
            sendButton.disabled = false;
        } else {
            alert('登录失败，请检查用户名和密码');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('登录时发生错误，请检查服务器连接');
    }
}

async function handleLogout() {
    try {
        const response = await fetch('/api/auth/logout', {
            method: 'POST'
        });
        
        if (response.ok) {
            console.log('User logged out successfully.');
            
            // 断开Socket连接
            if (socket) {
                socket.disconnect();
                socket = null;
            }
            
            // 重置全局状态
            currentUserId = null;
            currentUserName = null;
            currentConversationId = null;
            currentReceiverId = null;
            
            // 清空界面
            conversationList.innerHTML = '';
            messageArea.innerHTML = '';
            contactNameDisplay.textContent = '请先登录并选择会话';
            
            // 禁用发送按钮
            sendButton.disabled = true;
            
            // 显示登录界面，隐藏聊天界面
            loginScreen.classList.remove('hidden');
            chatApp.classList.add('hidden');
        } else {
            alert('退出登录失败');
        }
    } catch (error) {
        console.error('Logout error:', error);
        alert('退出登录时发生错误');
    }
}

function initSocket() {
    // 连接 SocketIO，使用当前页面的主机和端口
    socket = io(); 
    
    socket.on('connect', () => {
        console.log('Socket Connected. Ready for P2P messaging.');
    });

    socket.on('disconnect', () => {
        console.log('Socket Disconnected.');
    });

    socket.on('receive_msg', handleIncomingMessage);
}


// --- 核心逻辑：会话/消息 ---
async function loadConversations() {
    conversationList.innerHTML = '';
    const response = await fetch('/api/friends');
    const conversations = await response.json();
    
    conversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = 'p-3 hover:bg-gray-200 border-b cursor-pointer';
        if (conv.conversation_id === currentConversationId) {
             item.classList.add('bg-blue-200'); // 选中高亮
        }
        item.innerHTML = `
            <div class="flex justify-between items-center">
                <span class="font-semibold">${conv.receiver_name}</span>
                ${conv.unread_count > 0 ? `<span class="bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">${conv.unread_count}</span>` : ''}
            </div>
            <p class="text-sm text-gray-500 truncate">${conv.last_message_content}</p>
        `;
        item.onclick = () => switchConversation(conv.conversation_id, conv.receiver_id, conv.receiver_name);
        conversationList.appendChild(item);
    });
}

async function handleAddFriend() {
    const friendUsername = searchFriendInput.value.trim();
    
    if (!friendUsername) {
        alert('请输入要添加的用户名');
        return;
    }
    
    try {
        const response = await fetch(`/api/friends/add/${friendUsername}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            const data = await response.json();
            alert(`成功添加好友: ${data.friend_username}`);
            searchFriendInput.value = '';
            // 重新加载会话列表
            await loadConversations();
        } else {
            const error = await response.json();
            alert(`添加好友失败: ${error.message}`);
        }
    } catch (error) {
        console.error('Add friend error:', error);
        alert('添加好友时发生错误');
    }
}

async function switchConversation(cid, rid, rname) {
    if (currentConversationId) {
        // 移除旧的高亮
        document.querySelectorAll('.bg-blue-200').forEach(el => el.classList.remove('bg-blue-200'));
    }

    currentConversationId = cid;
    currentReceiverId = rid;
    contactNameDisplay.textContent = rname;
    
    // 标记当前选中项高亮
    const selectedItem = document.querySelector(`[onclick*="${cid}"]`);
    if (selectedItem) {
        selectedItem.classList.add('bg-blue-200');
    }

    // 加载历史消息
    messageArea.innerHTML = '';
    const response = await fetch(`/api/history/${cid}`);
    const history = await response.json();
    history.forEach(msg => appendMessage(msg, msg.sender_id === currentUserId));
}

function handleIncomingMessage(data) {
    // 1. 渲染消息
    const isCurrentChat = data.conversation_id === currentConversationId;
    if (isCurrentChat) {
        appendMessage(data, data.sender_id === currentUserId);
    } 
    
    // 2. 更新列表
    loadConversations(); // 重新加载会话列表以更新未读计数和最新消息
    
    // 3. 消息通知（可选：如果不是当前聊天，弹窗/声音提示）
    if (!isCurrentChat && data.sender_id !== currentUserId) {
         console.log(`New message from ${data.sender_id} in conversation ${data.conversation_id}`);
    }
}

// --- 管理员功能 ---
function openAdminPanel() {
    if (!currentUserIsAdmin) {
        alert('你没有管理员权限');
        return;
    }
    
    // 显示管理员面板
    adminPanel.classList.remove('hidden');
    
    // 加载所有用户信息
    loadAllUsers();
}

function closeAdminPanel() {
    // 隐藏管理员面板
    adminPanel.classList.add('hidden');
}

async function loadAllUsers() {
    try {
        const response = await fetch('/api/admin/users', {
            method: 'GET'
        });
        
        if (response.ok) {
            const users = await response.json();
            
            // 清空用户列表
            userTableBody.innerHTML = '';
            
            // 渲染用户列表
            users.forEach(user => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${user.id}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${user.username}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${user.is_admin ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                            ${user.is_admin ? '是' : '否'}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button class="text-blue-600 hover:text-blue-900 toggle-admin-btn" data-user-id="${user.id}" data-current-admin="${user.is_admin}">
                            ${user.is_admin ? '取消管理员' : '设置为管理员'}
                        </button>
                        <button class="ml-2 text-red-600 hover:text-red-900 delete-user-btn" data-user-id="${user.id}" data-username="${user.username}">
                            删除用户
                        </button>
                    </td>
                `;
                userTableBody.appendChild(row);
            });
            
            // 添加切换管理员状态的事件监听
            document.querySelectorAll('.toggle-admin-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const userId = e.target.dataset.userId;
                    toggleAdminStatus(userId);
                });
            });
            
            // 添加删除用户的事件监听
            document.querySelectorAll('.delete-user-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const userId = e.target.dataset.userId;
                    const username = e.target.dataset.username;
                    deleteUser(userId, username);
                });
            });
        } else {
            const error = await response.json();
            alert(`加载用户列表失败: ${error.message}`);
        }
    } catch (error) {
        console.error('Load all users error:', error);
        alert('加载用户列表时发生错误');
    }
}

async function toggleAdminStatus(userId) {
    try {
        const response = await fetch(`/api/admin/users/${userId}/toggle-admin`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log(`Admin status updated for user ${userId}: ${data.is_admin}`);
            
            // 重新加载用户列表以显示更新后的状态
            loadAllUsers();
        } else {
            const error = await response.json();
            alert(`更新管理员状态失败: ${error.message}`);
        }
    } catch (error) {
        console.error('Toggle admin status error:', error);
        alert('更新管理员状态时发生错误');
    }
}

async function deleteUser(userId, username) {
    // 确认删除
    if (!confirm(`确定要删除用户 ${username} 吗？此操作不可恢复！`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/users/${userId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log(`User ${username} deleted successfully.`);
            alert(data.message);
            
            // 重新加载用户列表
            loadAllUsers();
        } else {
            // 尝试解析JSON错误响应，如果失败则显示通用错误
            try {
                const error = await response.json();
                alert(`删除用户失败: ${error.message}`);
            } catch (jsonError) {
                console.error('JSON parse error:', jsonError);
                alert(`删除用户失败: 服务器返回错误 (状态码: ${response.status})`);
            }
        }
    } catch (error) {
        console.error('Delete user error:', error);
        alert('删除用户时发生错误');
    }
}

// --- 清空聊天记录功能 ---
async function handleClearChat() {
    if (!currentConversationId) {
        alert('请先选择一个会话');
        return;
    }
    
    // 确认清空
    if (!confirm('确定要清空当前聊天记录吗？此操作不可恢复！')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/history/${currentConversationId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Chat history cleared successfully.');
            
            // 清空消息区域
            messageArea.innerHTML = '';
            
            // 重新加载会话列表以更新最新消息
            await loadConversations();
        } else {
            const error = await response.json();
            alert(`清空聊天记录失败: ${error.message}`);
        }
    } catch (error) {
        console.error('Clear chat history error:', error);
        alert('清空聊天记录时发生错误');
    }
}

// --- 消息发送 ---
function handleSendMessage() {
    const content = messageInput.value.trim();
    if (!content || !currentConversationId) return;

    const messageData = {
        receiver_id: currentReceiverId,
        content: content,
    };
    
    socket.emit('send_msg', messageData);
    messageInput.value = '';
}

// --- UI 渲染逻辑 (气泡样式) ---
function appendMessage(message, is_mine) {
    const bubble = document.createElement('div');
    bubble.className = is_mine ? 'flex justify-end' : 'flex justify-start';
    
    const contentClasses = is_mine
        ? 'bg-blue-500 text-white p-3 rounded-xl rounded-br-none max-w-xs md:max-w-md shadow-md'
        : 'bg-gray-200 text-gray-800 p-3 rounded-xl rounded-tl-none max-w-xs md:max-w-md shadow-sm';
    
    bubble.innerHTML = `
        <div class="flex flex-col">
             <div class="${contentClasses}">
                ${message.content}
                <div class="text-xs mt-1 ${is_mine ? 'text-blue-200' : 'text-gray-500'} text-right">
                    ${new Date(message.timestamp).toLocaleTimeString()}
                </div>
            </div>
        </div>
    `;
    messageArea.appendChild(bubble);
    // 滚动到底部
    messageArea.scrollTop = messageArea.scrollHeight; 
}