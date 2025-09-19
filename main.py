from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from datetime import datetime
import html
import os

from config import SERVER_CONFIG
from utils.database import (
    get_db_connection,
    get_all_system_prompts, 
    get_system_prompt_by_key, 
    update_system_prompt, 
    create_system_prompt, 
    delete_system_prompt,
    delete_system_prompt_by_key,
    check_prompt_key_exists
)

app = FastAPI(title=SERVER_CONFIG["title"], version=SERVER_CONFIG["version"])

# テンプレートエンジン設定
templates = Jinja2Templates(directory="templates")

# 静的ファイル配信（存在時のみ）
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    try:
        prompts = await get_all_system_prompts()
        return templates.TemplateResponse("index.html", {
            "request": request,
            "prompts": prompts,
            "version": SERVER_CONFIG["version"]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/edit/{prompt_key}", response_class=HTMLResponse)
async def edit_prompt(request: Request, prompt_key: str):
    try:
        prompt = await get_system_prompt_by_key(prompt_key)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        return templates.TemplateResponse("edit.html", {
            "request": request,
            "prompt": prompt,
            "version": SERVER_CONFIG["version"]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/new", response_class=HTMLResponse)
async def new_prompt(request: Request):
    return templates.TemplateResponse("new.html", {
        "request": request,
        "version": SERVER_CONFIG["version"]
    })

@app.post("/create")
async def create_prompt_post(
    prompt_key: str = Form(...),
    prompt_text: str = Form(...)
):
    try:
        # prompt_key重複チェック
        if await check_prompt_key_exists(prompt_key):
            raise HTTPException(status_code=400, detail=f"Prompt key '{prompt_key}' already exists")
        
        await create_system_prompt(prompt_key, prompt_text)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update/{prompt_key}")
async def update_prompt_post(
    prompt_key: str,
    new_prompt_key: str = Form(..., alias="prompt_key"),
    prompt_text: str = Form(...)
):
    try:
        # prompt_keyが変更された場合は削除→作成、同じ場合は更新
        if prompt_key != new_prompt_key:
            # 新しいキーの重複チェック
            if await check_prompt_key_exists(new_prompt_key):
                raise HTTPException(status_code=400, detail=f"Prompt key '{new_prompt_key}' already exists")
            
            # 古いキーを削除して新しいキーで作成
            await delete_system_prompt_by_key(prompt_key)
            await create_system_prompt(new_prompt_key, prompt_text)
        else:
            # 同じキーの場合は通常の更新
            await update_system_prompt(prompt_key, prompt_text)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system-prompts/{prompt_key}")
async def get_system_prompt_api(prompt_key: str):
    """システムプロンプトAPI取得"""
    try:
        prompt = await get_system_prompt_by_key(prompt_key)
        if prompt:
            return {
                "prompt_key": prompt["prompt_key"],
                "prompt_text": prompt["prompt_text"],
                "created_at": prompt["created_at"],
                "updated_at": prompt["updated_at"]
            }
        else:
            raise HTTPException(status_code=404, detail="Prompt not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete/{prompt_id}")
async def delete_prompt_post(prompt_id: int):
    try:
        # IDで直接削除（シンプル）
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM system_prompts WHERE id = %s", (prompt_id,))
        connection.commit()
        cursor.close()
        connection.close()
        
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVER_CONFIG["port"])
