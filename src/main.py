from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import psycopg2
from psycopg2.extras import RealDictCursor
import uvicorn
from datetime import datetime
import html

app = FastAPI(title="SystemPrompt Management", version="1.0.0")

# PostgreSQL設定
DB_CONFIG = {
    'host': 'localhost',
    'database': 'wealthai',
    'user': 'wealthai_user',
    'password': 'password'
}

def get_db_connection():
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

@app.get("/", response_class=HTMLResponse)
async def index():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM system_prompts ORDER BY prompt_key")
        prompts = cursor.fetchall()
        cursor.close()
        connection.close()
        
        prompt_count = len(prompts)
        
        # HTMLテンプレートを安全に作成
        html_header = """<!DOCTYPE html>
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
                <button class="btn btn-success me-2" onclick="showAddForm()"><i class="fas fa-plus me-1"></i>新規作成</button>
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
        
        # テーブル行を作成
        table_rows = ""
        for prompt in prompts:
            preview = prompt['prompt_text'][:100] + '...' if len(prompt['prompt_text']) > 100 else prompt['prompt_text']
            
            table_rows += f"""                        <tr>
                            <td><code>{prompt['prompt_key']}</code></td>
                            <td>{prompt['description'] or '-'}</td>
                            <td><small class="text-muted">{preview}</small></td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary me-1" 
                                        data-id="{prompt['id']}" 
                                        data-key="{prompt['prompt_key']}"
                                        data-desc="{html.escape(prompt['description'] or '')}"
                                        data-prompt="{html.escape(prompt['prompt_text'])}"
                                        onclick="editFromData(this)" 
                                        title="編集"><i class="fas fa-edit"></i></button>
                                <button class="btn btn-sm btn-outline-danger" onclick="deletePrompt({prompt['id']}, '{prompt['prompt_key']}')" title="削除"><i class="fas fa-trash"></i></button>
                            </td>
                        </tr>
"""
        
        html_footer = f"""                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="alert alert-success mt-4">
            <i class="fas fa-database me-2"></i>
            PostgreSQL (wealthai database) に接続中 - {prompt_count}件のプロンプトを管理
        </div>
    </div>

    <!-- 新規作成モーダル -->
    <div class="modal fade" id="addModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">新規プロンプト作成</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form method="post" action="/create">
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">キー <span class="text-danger">*</span></label>
                            <input type="text" class="form-control" name="prompt_key" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">説明</label>
                            <input type="text" class="form-control" name="description">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">プロンプト <span class="text-danger">*</span></label>
                            <textarea class="form-control" name="prompt_text" rows="8" required></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">キャンセル</button>
                        <button type="submit" class="btn btn-success">作成</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- 編集モーダル -->
    <div class="modal fade" id="editModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">プロンプト編集</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form method="post" id="editForm">
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">キー</label>
                            <input type="text" class="form-control" id="editKey" readonly>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">説明</label>
                            <input type="text" class="form-control" name="description" id="editDescription">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">プロンプト <span class="text-danger">*</span></label>
                            <textarea class="form-control" name="prompt_text" id="editPromptText" rows="8" required></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">キャンセル</button>
                        <button type="submit" class="btn btn-primary">更新</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function showAddForm() {{
            new bootstrap.Modal(document.getElementById('addModal')).show();
        }}
        
        function editFromData(button) {{
            const id = button.dataset.id;
            const key = button.dataset.key;
            const description = button.dataset.desc;
            const promptText = button.dataset.prompt;
            
            document.getElementById('editKey').value = key;
            document.getElementById('editDescription').value = description;
            document.getElementById('editPromptText').value = promptText;
            document.getElementById('editForm').action = '/update/' + id;
            new bootstrap.Modal(document.getElementById('editModal')).show();
        }}
        
        function deletePrompt(id, key) {{
            if (confirm('プロンプト "' + key + '" を削除しますか？')) {{
                fetch('/delete/' + id, {{method: 'POST'}})
                    .then(() => location.reload());
            }}
        }}
    </script>
    
    <footer class="mt-5 text-center text-muted">
        <small>SystemPrompt Management v1.0.0 - PostgreSQL版</small>
    </footer>
</body>
</html>"""
        
        return html_header + table_rows + html_footer
        
    except Exception as e:
        return f"<h1>Database Error</h1><p>{str(e)}</p>"

@app.post("/create")
async def create_prompt(prompt_key: str = Form(...), description: str = Form(""), prompt_text: str = Form(...)):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO system_prompts (prompt_key, description, prompt_text) VALUES (%s, %s, %s)", 
                      (prompt_key, description, prompt_text))
        connection.commit()
        cursor.close()
        connection.close()
        return RedirectResponse(url="/", status_code=303)
    except psycopg2.IntegrityError:
        raise HTTPException(status_code=400, detail="Prompt key already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update/{prompt_id}")
async def update_prompt(prompt_id: int, description: str = Form(""), prompt_text: str = Form(...)):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE system_prompts SET description = %s, prompt_text = %s, updated_at = %s WHERE id = %s",
                      (description, prompt_text, datetime.now(), prompt_id))
        connection.commit()
        cursor.close()
        connection.close()
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete/{prompt_id}")
async def delete_prompt(prompt_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM system_prompts WHERE id = %s", (prompt_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prompt/{prompt_key}")
async def get_prompt_by_key(prompt_key: str):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT prompt_text FROM system_prompts WHERE prompt_key = %s", (prompt_key,))
        prompt = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        return {"prompt_key": prompt_key, "prompt_text": prompt["prompt_text"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def status():
    return {"status": "running", "service": "SystemPrompt Management", "version": "1.0.0", "database": "PostgreSQL"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8007)
