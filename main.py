from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime
import html

from config import SERVER_CONFIG
from utils.database import (
    get_all_system_prompts, 
    get_system_prompt_by_key, 
    update_system_prompt, 
    create_system_prompt, 
    delete_system_prompt
)

app = FastAPI(title=SERVER_CONFIG["title"], version=SERVER_CONFIG["version"])

# 静的ファイル配信
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
        </head>
        <body>
            <div class="container mt-4">
                <h1 class="mb-4">SystemPrompt Management v2.0.0</h1>
                <p class="text-muted">AIChat Database: aichat.system_prompts</p>
                
                <div class="row">
                    <div class="col-md-8">
                        <h3>System Prompts ({count})</h3>
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Prompt Key</th>
                                        <th>Text Length</th>
                                        <th>Updated</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {rows}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <div class="col-md-4">
                        <h3>Add New Prompt</h3>
                        <form method="post" action="/create">
                            <div class="mb-3">
                                <label class="form-label">Prompt Key</label>
                                <input type="text" class="form-control" name="prompt_key" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Prompt Text</label>
                                <textarea class="form-control" name="prompt_text" rows="5" required></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary">Create</button>
                        </form>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        rows = ""
        for prompt in prompts:
            updated_str = prompt['updated_at'].strftime('%Y-%m-%d %H:%M') if prompt['updated_at'] else 'N/A'
            rows += f"""
                <tr>
                    <td><code>{html.escape(prompt['prompt_key'])}</code></td>
                    <td>{len(prompt['prompt_text'])}</td>
                    <td>{updated_str}</td>
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

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "SystemPrompt-Management", "version": SERVER_CONFIG["version"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVER_CONFIG["port"])
