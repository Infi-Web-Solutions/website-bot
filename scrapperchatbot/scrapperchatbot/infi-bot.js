// chatbot-widget.js

(function() { // Start of IIFE to encapsulate the chatbot logic
    // STEP 1: Read bot ID from script tag
const currentScript = document.currentScript || [...document.getElementsByTagName('script')].pop();
const botId = currentScript.getAttribute('data-bot-id') || 'DEFAULT_BOT';
console.log("Bot ID detected:", botId);

    // ------------------ 1. CHATBOT CSS (as a string) ------------------
    const chatbotCss = `
        /* General body styles - Be cautious, this might affect host page */
        body {
            font-family: 'Inter', sans-serif;
            /* Consider removing margin/height/padding/background if this script targets body */
            /* margin: 0; */
            /* height: 100vh; */
            /* padding: 0; */
            /* background: #f8fafc; */
        }

        .glass {
            background: linear-gradient(to bottom right, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1));
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 1.5rem;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
            overflow: hidden;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .chat-wrapper-injected { /* Use a unique class to avoid conflicts */
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            transition: all 0.3s ease;
            z-index: 1000;
        }

        .chat-wrapper-injected.collapsed .glass {
            width: 64px;
            height: 64px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .chat-wrapper-injected.expanded .glass {
            width: 100%;
            max-width: 400px;
            height: 540px;
            border-radius: 1.5rem;
        }

        .chat-header-injected { /* Unique class */
            background: transparent;
            color: #1f2937;
            padding: 1rem;
            font-weight: 600;
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            user-select: none;
            gap: 0.5rem;
        }

        .chat-wrapper-injected.collapsed .chat-header-injected {
            padding: 0;
            width: 100%;
            height: 100%;
            justify-content: center;
            align-items: center;
        }

        .chat-wrapper-injected.collapsed .chat-header-injected span,
        .chat-wrapper-injected.collapsed .chat-header-injected hr {
            display: none;
        }

        .chat-body-injected { /* Unique class */
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 476px;
        }

        .chat-wrapper-injected.collapsed .chat-body-injected {
            display: none;
        }

        .chat-messages-injected { /* Unique class */
            overflow-y: auto;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            scrollbar-width: thin;
        }

        .chat-messages-injected::-webkit-scrollbar {
            width: 6px;
        }
        .chat-messages-injected {
    max-height: 400px !important;
  }

        .chat-messages-injected::-webkit-scrollbar-thumb {
            background-color: rgba(100, 116, 139, 0.3);
            border-radius: 10px;
        }

        .bot-injected ul { /* Unique class */
            list-style-type: disc;
            padding-left: 20px;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }

        .bot-injected ol { /* Unique class */
            list-style-type: decimal;
            padding-left: 20px;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }

        .bot-injected li { /* Unique class */
            margin-bottom: 0.25rem;
        }

        .message-injected { /* Unique class */
            max-width: 80%;
            padding: 0.75rem 1rem;
            border-radius: 1rem;
            font-size: 0.95rem;
            line-height: 1.4;
            word-break: break-word;
            overflow-wrap: break-word;
        }

        .user-injected { /* Unique class */
            align-self: flex-end;
            background: #dbeafe;
            color: #1e40af;
            border-bottom-right-radius: 0.25rem;
        }

        .bot-injected { /* Unique class */
            align-self: flex-start;
            background: #f1f5f9;
            color: #334155;
            border-bottom-left-radius: 0.25rem;
        }

        .chat-input-area-injected { /* Unique class */
            display: flex;
            gap: 0.5rem;
            padding: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            background-color: rgba(255, 255, 255, 0.05);
        }

        .chat-input-area-injected input { /* Unique class */
            flex: 1;
            padding: 0.75rem 1rem;
            border-radius: 9999px;
            border: 1px solid #cbd5e1;
            outline: none;
            font-size: 0.95rem;
        }

        .chat-input-area-injected button { /* Unique class */
            background: linear-gradient(to right, #6366f1, #4f46e5);
            color: white;
            padding: 0.75rem 1.25rem;
            border-radius: 9999px;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: background 0.3s ease;
        }

        .chat-input-area-injected button:hover {
            background: #4338ca;
        }

        .loading-injected { /* Unique class */
            text-align: center;
            color: #9ca3af;
            font-size: 0.875rem;
            margin: 0.5rem 1rem;
        }

        .rotate-180-injected { /* Unique class */
            transform: rotate(180deg);
        }

        .chat-brand-injected { /* Unique class */
            padding: 0.5rem 1rem;
            text-align: center;
            font-size: 0.85rem;
            font-weight: 600;
            color: #475569;
            border-top: 1px solid #e2e8f0;
            background-color: rgba(255, 255, 255, 0.07);
        }
    `;

    // ------------------ 2. CHATBOT HTML (as a template literal) ------------------
    // Notice the class names are changed to include '-injected' suffix to minimize conflicts
    const chatbotHtml = `
        <div id="chatbot-wrapper-unique" class="chat-wrapper-injected collapsed">
            <div class="glass">
                <div id="chatbot-header-unique" class="chat-header-injected">
                    <div style="display: flex; flex-direction: column;">
                        <span>Infi Web Solutions</span>
                        <hr style="width: 100%; border: 1px solid #ccc; margin-top: 4px;" />
                    </div>
                    <svg id="chatbot-toggle-icon-unique" class="h-6 w-6 text-gray-700 transition-transform duration-300" fill="none" stroke="black" stroke-width="2" viewBox="0 0 24 24">
                        <path d="M6 9l6 6 6-6" />
                    </svg>
                </div>

                <div class="chat-body-injected">
                    <div id="chatbot-messages-unique" class="chat-messages-injected">
                        <div class="message-injected bot-injected">Hello! How can I help you today?</div>
                    </div>
                    <div id="chatbot-loading-indicator-unique" class="loading-injected hidden">Thinking...</div>
                    <div class="chat-input-area-injected">
                        <input id="chatbot-user-input-unique" type="text" placeholder="Ask a question..." />
                        <button id="chatbot-send-button-unique">Send</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // ------------------ 3. Dynamic Injection and Event Handling ------------------

    function initializeChatbot() {
        // Create a container for the chatbot
        const chatbotContainer = document.createElement('div');
        chatbotContainer.id = 'injected-chatbot-root'; // Unique ID for the root element
        document.body.appendChild(chatbotContainer); // Append to body

        // Inject the HTML
        chatbotContainer.innerHTML = chatbotHtml;

        // Inject the CSS
        const styleTag = document.createElement('style');
        styleTag.textContent = chatbotCss;
        document.head.appendChild(styleTag);

        // Load Google Fonts (if not already loaded by host page)
        const fontLink = document.createElement('link');
        fontLink.href = "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap";
        fontLink.rel = "stylesheet";
        document.head.appendChild(fontLink);

        // Load TailwindCSS (if not already loaded by host page)
        // Be cautious: If the host page also uses Tailwind, this might cause issues.
        // It's generally better to compile necessary Tailwind classes into your chatbot's CSS.
        const tailwindScript = document.createElement('script');
        tailwindScript.src = "https://cdn.tailwindcss.com";
        document.head.appendChild(tailwindScript);


        // Get references to the elements *after* they've been inserted
        const chatWrapper = document.getElementById('chatbot-wrapper-unique');
        const chatHeader = document.getElementById('chatbot-header-unique');
        const toggleIcon = document.getElementById('chatbot-toggle-icon-unique');
        const userInput = document.getElementById('chatbot-user-input-unique');
        const sendButton = document.getElementById('chatbot-send-button-unique');
        const chatMessages = document.getElementById('chatbot-messages-unique');
        const loadingIndicator = document.getElementById('chatbot-loading-indicator-unique');

        // Initialize the arrow to point up when collapsed
        toggleIcon.classList.add('rotate-180-injected'); // Use unique class name

        chatHeader.addEventListener('click', () => {
            const isCollapsed = chatWrapper.classList.contains('collapsed');
            chatWrapper.classList.toggle('collapsed', !isCollapsed);
            chatWrapper.classList.toggle('expanded', isCollapsed);
            toggleIcon.classList.toggle('rotate-180-injected', !isCollapsed); // Use unique class name

            if (isCollapsed) {
                setTimeout(() => userInput.focus(), 300);
            }
        });

        function addMessage(text, sender) {
            const msg = document.createElement('div');
            // Use unique class names
            msg.className = `message-injected ${sender}-injected`;
            msg.innerHTML = text;
            chatMessages.appendChild(msg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        async function sendMessage() {
            const question = userInput.value.trim();
            if (!question) return;

            addMessage(question, 'user');
            userInput.value = '';
            sendButton.disabled = true;
            loadingIndicator.classList.remove('hidden');

            try {
                // !!! IMPORTANT: Adjust this URL to your ABSOLUTE backend endpoint !!!
                // Example: 'https://your-backend-domain.com/webscrapper/chatbot/'
                const backendUrl = 'http://localhost:8000/webscrapper/chatbot/'; // Relative path, assumes same domain

                const res = await fetch(backendUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({ question, bot_id: botId })
                });

                const data = await res.json();
                addMessage(data.response || data.error || 'No response', 'bot');
            } catch (e) {
                console.error('Chatbot Error:', e);
                addMessage('Something went wrong. Please try again.', 'bot');
            } finally {
                sendButton.disabled = false;
                loadingIndicator.classList.add('hidden');
                userInput.focus();
            }
        }

        sendButton.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', e => {
            if (e.key === 'Enter') sendMessage();
        });
    }

    // Run the initialization function once the DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeChatbot);
    } else {
        initializeChatbot();
    }

})(); // End of IIFE