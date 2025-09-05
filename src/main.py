# SystemPrompt Management Service
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SystemPrompt Management", version="1.0.0")

# テンプレート設定
templates = Jinja2Templates(directory="templates")

# データベース設定
DB_CONFIG = {
    'host': 'localhost',
    'database': 'systemprompt',
    'user': 'root',
    'password': 'password'
}

# データモデル
class SystemPrompt(BaseModel):
    id: Optional[int] = None
    prompt_key: str
    prompt_text: str
    description: Optional[str] = ""
    category: str = "general"
    is_active: bool = True
    version: int = 1

class SystemPromptUpdate(BaseModel):
    prompt_text: str
    description: Optional[str] = ""
    category: str = "general"
    is_active: bool = True

# データベース接続
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# ルート - プロンプト一覧画面
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, prompt_key, description, category, is_active, 
                   LEFT(prompt_text, 100) as prompt_preview,
                   version, updated_at
            FROM system_prompts 
            ORDER BY category, prompt_key
        """)
        
        prompts = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "prompts": prompts
        })
        
    except Exception as e:
        logger.error(f"Error loading prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# プロンプト詳細・編集画面
@app.get("/prompt/{prompt_id}", response_class=HTMLResponse)
async def edit_prompt(request: Request, prompt_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM system_prompts WHERE id = %s", (prompt_id,))
        prompt = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        return templates.TemplateResponse("edit.html", {
            "request": request,
            "prompt": prompt
        })
        
    except Exception as e:
        logger.error(f"Error loading prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 新規プロンプト作成画面
@app.get("/new", response_class=HTMLResponse)
async def new_prompt(request: Request):
    return templates.TemplateResponse("new.html", {"request": request})

# プロンプト作成処理
@app.post("/create")
async def create_prompt(
    prompt_key: str = Form(...),
    prompt_text: str = Form(...),
    description: str = Form(""),
    category: str = Form("general")
):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO system_prompts (prompt_key, prompt_text, description, category)
            VALUES (%s, %s, %s, %s)
        """, (prompt_key, prompt_text, description, category))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return RedirectResponse(url="/", status_code=303)
        
    except mysql.connector.IntegrityError:
        raise HTTPException(status_code=400, detail="Prompt key already exists")
    except Exception as e:
        logger.error(f"Error creating prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# プロンプト更新処理
@app.post("/update/{prompt_id}")
async def update_prompt(
    prompt_id: int,
    prompt_text: str = Form(...),
    description: str = Form(""),
    category: str = Form("general"),
    is_active: bool = Form(True)
):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # バージョンアップ
        cursor.execute("SELECT version FROM system_prompts WHERE id = %s", (prompt_id,))
        current_version = cursor.fetchone()[0]
        new_version = current_version + 1
        
        cursor.execute("""
            UPDATE system_prompts 
            SET prompt_text = %s, description = %s, category = %s, 
                is_active = %s, version = %s, updated_at = %s
            WHERE id = %s
        """, (prompt_text, description, category, is_active, new_version, 
              datetime.now(), prompt_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return RedirectResponse(url="/", status_code=303)
        
    except Exception as e:
        logger.error(f"Error updating prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# プロンプト削除処理
@app.post("/delete/{prompt_id}")
async def delete_prompt(prompt_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM system_prompts WHERE id = %s", (prompt_id,))
        connection.commit()
        cursor.close()
        connection.close()
        
        return RedirectResponse(url="/", status_code=303)
        
    except Exception as e:
        logger.error(f"Error deleting prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API: プロンプト取得
@app.get("/api/prompt/{prompt_key}")
async def get_prompt_by_key(prompt_key: str):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT prompt_text FROM system_prompts 
            WHERE prompt_key = %s AND is_active = true
        """, (prompt_key,))
        
        prompt = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        return {"prompt_key": prompt_key, "prompt_text": prompt["prompt_text"]}
        
    except Exception as e:
        logger.error(f"Error getting prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API: 全プロンプト一覧
@app.get("/api/prompts")
async def get_all_prompts():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT prompt_key, prompt_text, description, category 
            FROM system_prompts 
            WHERE is_active = true
            ORDER BY category, prompt_key
        """)
        
        prompts = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return {"prompts": prompts}
        
    except Exception as e:
        logger.error(f"Error getting prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
