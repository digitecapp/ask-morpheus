from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
import requests

app = FastAPI()

PERPLEXITY_API_KEY = "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"  # Your key

@app.get("/", response_class=HTMLResponse)
def welcome():
    return """
    <html>
        <head>
            <title>Chat + Edit AI</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs/loader.min.js"></script>
            <link href="https://fonts.cdnfonts.com/css/courier-prime" rel="stylesheet">
            <style>
                body { background: black; text-align: center; }
                #editor { width: 80%; height: 45px; margin: 20px auto; background: #000000; color: #50C878; font-family: 'Courier Prime', monospace; overflow: hidden; text-align: left; padding-left: 5px; border: none; outline: none; box-shadow: none; }
                .monaco-editor, .monaco-editor .overflow-guard, .monaco-editor .scrollbar { overflow: hidden !important; }
                .monaco-editor .scrollbar.vertical { display: none !important; }
                #reply { width: 80%; margin: 20px auto; background: #000000; color: #50C878; font-family: 'Courier Prime', monospace; font-style: normal; font-size: 36px; border: none; line-height: 45px; }
                h1 { color: #50C878; font-family: 'Courier Prime', monospace; font-size: 36px; font-weight: normal; line-height: 45px; }
            </style>
        </head>
        <body>
            <h1>Morpheus</h1>
            <div id="editor"></div>
            <div id="reply"></div>
            <script>
                let editor;
                require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' }});
                require(['vs/editor/editor.main'], function() {
                    editor = monaco.editor.create(document.getElementById('editor'), {
                        value: '',
                        language: 'plaintext',
                        theme: 'vs-dark',
                        lineNumbers: 'off',
                        cursorBlinking: 'blink',
                        fontFamily: "'Courier Prime', monospace",
                        fontSize: 36,
                        wordWrap: 'off',
                        wrappingIndent: 'none',
                        lineHeight: 45,
                        minimap: { enabled: false },
                        scrollBeyondLastLine: false,
                        scrollbar: { vertical: 'hidden', horizontal: 'hidden', useShadows: false, verticalScrollbarSize: 0, horizontalScrollbarSize: 0 },
                        maxLines: 1,
                        automaticLayout: true
                    });
                    monaco.editor.defineTheme('custom-dark', {
                        base: 'vs-dark',
                        inherit: true,
                        rules: [{ token: '', foreground: '50C878' }],
                        colors: {
                            'editor.background': '#000000',
                            'editorCursor.foreground': '#50C878',
                            'editor.lineHighlightBorder': '#000000',
                            'editor.focusOutline': '#000000',
                            'scrollbar.shadow': '#000000'
                        }
                    });
                    editor.updateOptions({ theme: 'custom-dark' });
                    window.onload = function() { editor.focus(); };
                    editor.onKeyDown(function(e) {
                        if (e.keyCode === monaco.KeyCode.Enter) {
                            e.preventDefault();
                            sendDocument();
                        }
                    });
                });
                async function sendDocument() {
                    const message = editor.getValue();
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                        body: 'message=' + encodeURIComponent(message)
                    });
                    const data = await response.json();
                    document.getElementById('reply').innerHTML = '<p>You: ' + message + '</p><p>Morpheus: ' + data.response + '</p><hr>' + document.getElementById('reply').innerHTML;
                }
            </script>
        </body>
    </html>
    """

@app.post("/chat")
def chat(message: str = Form(...)):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-sonar-large-128k-online",
        "messages": [
            {"role": "system", "content": "Be concise and helpful."},
            {"role": "user", "content": message}
        ],
        "max_tokens": 300
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"].strip()
    else:
        reply = f"Oops, API failed - Status: {response.status_code}, Error: {response.text}"
    return {"response": reply}