from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime
import html
import os

from config import SERVER_CONFIG
from utils.database import (
    get_all_system_prompts, 
    get_system_prompt_by_key, 
    update_system_prompt, 
    create_system_prompt, 
    delete_system_prompt
)

app = FastAPI(title=SERVER_CONFIG["title"], version=SERVER_CONFIG["version"])

# 静的ファイル配信（存在時のみ）
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index():
    try:
        prompts = await get_all_system_prompts()
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>SystemPrompt Management v2.0.0</title>
            <meta charset="UTF-8">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .prompt-preview {{
                    width: 100%;
                    font-family: monospace;
                    font-size: 12px;
                    background-color: #f8f9fa;
                    padding: 8px;
                    border-radius: 4px;
                    border-left: 3px solid #007bff;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    word-wrap: break-word;
                }}
                .prompt-preview:hover {{
                    background-color: #e9ecef;
                }}
                .prompt-full {{
                    display: none;
                    width: 100%;
                    font-family: monospace;
                    font-size: 11px;
                    background-color: #1e1e1e;
                    color: #ffffff;
                    padding: 12px;
                    border-radius: 4px;
                    margin-top: 8px;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }}
                .expand-btn {{
                    font-size: 10px;
                    color: #007bff;
                    text-decoration: none;
                }}
                .expand-btn:hover {{
                    text-decoration: underline;
                }}
                .add-prompt-section {{
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="container-fluid mt-4">
                <h1 class="mb-4">SystemPrompt Management v2.0.0</h1>
                <p class="text-muted">AIChat Database: aichat.system_prompts</p>
                
                <!-- Add New Prompt Section (上段) -->
                <div class="add-prompt-section">
                    <h4 class="mb-3">Add New Prompt</h4>
                    <form method="post" action="/create" class="row g-3">
                        <div class="col-md-3">
                            <label class="form-label">Prompt Key</label>
                            <input type="text" class="form-control" name="prompt_key" required>
                        </div>
                        <div class="col-md-7">
                            <label class="form-label">Prompt Text</label>
                            <textarea class="form-control" name="prompt_text" rows="3" required></textarea>
                        </div>
                        <div class="col-md-2 d-flex align-items-end">
                            <button type="submit" class="btn btn-primary w-100">Create</button>
                        </div>
                    </form>
                </div>

                <!-- System Prompts Table (全幅) -->
                <div class="row">
                    <div class="col-12">
                        <h3>System Prompts ({count})</h3>
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th width="20%">Prompt Key</th>
                                        <th width="60%">Content Preview</th>
                                        <th width="8%">Length</th>
                                        <th width="12%">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {rows}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                function togglePrompt(id) {{
                    const preview = document.getElementById('preview-' + id);
                    const full = document.getElementById('full-' + id);
                    const btn = document.getElementById('btn-' + id);
                    
                    if (full.style.display === 'none') {{
                        full.style.display = 'block';
                        preview.style.display = 'none';
                        btn.textContent = '▲ 折りたたむ';
                    }} else {{
                        full.style.display = 'none';
                        preview.style.display = 'block';
                        btn.textContent = '▼ 全文表示';
                    }}
                }}
            </script>
        </body>
        </html>
        """
        
        rows = ""
        for i, prompt in enumerate(prompts):
            # プレビュー用テキスト（最初の100文字に拡張）
            preview_text = prompt['prompt_text'][:100]
            if len(prompt['prompt_text']) > 100:
                preview_text += "..."
            
            # 全文テキスト
            full_text = html.escape(prompt['prompt_text'])
            
            rows += f"""
                <tr>
                    <td><code>{html.escape(prompt['prompt_key'])}</code></td>
                    <td>
                        <div id="preview-{i}" class="prompt-preview" onclick="togglePrompt({i})">
                            {html.escape(preview_text)}
                        </div>
                        <div id="full-{i}" class="prompt-full">
                            {full_text}
                        </div>
                        <a href="#" id="btn-{i}" class="expand-btn" onclick="togglePrompt({i}); return false;">
                            ▼ 全文表示
                        </a>
                    </td>
                    <td><span class="badge bg-info">{len(prompt['prompt_text'])}</span></td>
                    <td>
                        <a href="/edit/{html.escape(prompt['prompt_key'])}" class="btn btn-sm btn-outline-primary">Edit</a>
                        <a href="/delete/{html.escape(prompt['prompt_key'])}" class="btn btn-sm btn-outline-danger" 
                           onclick="return confirm('Delete this prompt?')">Delete</a>
                    </td>
                </tr>
            """
        
        return html_content.format(count=len(prompts), rows=rows)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/edit/{prompt_key}", response_class=HTMLResponse)
async def edit_prompt(prompt_key: str):
    try:
        prompt = await get_system_prompt_by_key(prompt_key)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Edit Prompt - {html.escape(prompt_key)}</title>
            <meta charset="UTF-8">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-4">
                <h1>Edit System Prompt</h1>
                <p class="text-muted">Key: <code>{html.escape(prompt_key)}</code></p>
                
                <form method="post" action="/update/{html.escape(prompt_key)}">
                    <div class="mb-3">
                        <label class="form-label">Prompt Text</label>
                        <textarea class="form-control" name="prompt_text" rows="15" required>{html.escape(prompt['prompt_text'])}</textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Update</button>
                    <a href="/" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create")
async def create_prompt(prompt_key: str = Form(...), prompt_text: str = Form(...)):
    try:
        await create_system_prompt(prompt_key, prompt_text)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update/{prompt_key}")
async def update_prompt(prompt_key: str, prompt_text: str = Form(...)):
    try:
        success = await update_system_prompt(prompt_key, prompt_text)
        if not success:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/delete/{prompt_key}")
async def delete_prompt(prompt_key: str):
    try:
        success = await delete_system_prompt(prompt_key)
        if not success:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API エンドポイント
@app.get("/api/prompt/{prompt_key}")
async def get_prompt_api(prompt_key: str):
    """プロンプト取得API（単数形）"""
    try:
        prompt = await get_system_prompt_by_key(prompt_key)
        return {
            "prompt_key": prompt_key,
            "prompt_text": prompt["prompt_text"]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Prompt not found")

@app.get("/api/prompts/{prompt_key}")
async def get_prompt_api_plural(prompt_key: str):
    """プロンプト取得API（複数形・ProductMaster-MCP互換）"""
    return await get_prompt_api(prompt_key)

@app.get("/api/status")
async def api_status():
    """サービス状態確認API"""
    return {
        "status": "running",
        "service": "SystemPrompt Management",
        "version": SERVER_CONFIG["version"],
        "database": "PostgreSQL"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "SystemPrompt-Management", "version": SERVER_CONFIG["version"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVER_CONFIG["port"])
