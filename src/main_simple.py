from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="SystemPrompt Management", version="1.0.0")

# ダミーデータ
DUMMY_PROMPTS = [
    {"id": 1, "prompt_key": "strategy_planning", "description": "戦略立案用システムプロンプト", "prompt_text": "あなたは戦略立案の専門家です。ユーザーリクエストを分析し、必要最小限のツールのみを選択してください。"},
    {"id": 2, "prompt_key": "integration_response", "description": "回答統合用システムプロンプト", "prompt_text": "証券会社の社内情報システムとして回答してください。"},
    {"id": 3, "prompt_key": "simple_chat", "description": "シンプルチャット用システムプロンプト", "prompt_text": "あなたは親切な金融商品アドバイザーです。ユーザーの質問に対して、親しみやすく分かりやすい回答をしてください。"}
]

@app.get("/", response_class=HTMLResponse)
async def index():
    try:
        prompts = DUMMY_PROMPTS
        
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SystemPrompt Management</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-cogs me-2"></i>SystemPrompt Management</h2>
            <div>
                <button class="btn btn-success me-2" onclick="alert('新規作成機能は後で実装予定')"><i class="fas fa-plus me-1"></i>新規作成</button>
                <a href="http://44.217.45.24/" class="btn btn-secondary"><i class="fas fa-home me-1"></i>ポータル</a>
            </div>
        </div>
        
        <div class="card">
            <div class="card-body">
                <table class="table table-hover">
                    <thead class="table-dark">
                        <tr>
                            <th>キー</th>
                            <th>説明</th>
                            <th>プロンプト</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>"""        
        
        for prompt in prompts:
            preview = prompt['prompt_text'][:100] + '...' if len(prompt['prompt_text']) > 100 else prompt['prompt_text']
            html += f"""                        <tr>
                            <td><code>{prompt['prompt_key']}</code></td>
                            <td>{prompt['description'] or '-'}</td>
                            <td><small class="text-muted">{preview}</small></td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary me-1" onclick="alert('編集機能は後で実装予定')"><i class="fas fa-edit"></i></button>
                                <button class="btn btn-sm btn-outline-danger" onclick="alert('削除機能は後で実装予定')"><i class="fas fa-trash"></i></button>
                            </td>
                        </tr>
"""
        
        html += """                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="alert alert-info mt-4">
            <i class="fas fa-info-circle me-2"></i>
            現在はダミーデータで表示しています。MySQL接続は後で実装予定です。
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    
    <footer class="mt-5 text-center text-muted">
        <small>SystemPrompt Management v1.0.0 - ダミーデータ版</small>
    </footer>
</body>
</html>"""
        
        return html
        
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

@app.get("/api/prompt/{prompt_key}")
async def get_prompt_by_key(prompt_key: str):
    for prompt in DUMMY_PROMPTS:
        if prompt['prompt_key'] == prompt_key:
            return {"prompt_key": prompt_key, "prompt_text": prompt["prompt_text"]}
    raise HTTPException(status_code=404, detail="Prompt not found")

@app.get("/api/status")
async def status():
    return {"status": "running", "service": "SystemPrompt Management", "version": "1.0.0", "data_source": "dummy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8007)
