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
    get_all_system_prompts, 
    get_system_prompt_by_key, 
    update_system_prompt, 
    create_system_prompt, 
    delete_system_prompt
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
    description: str = Form(""),
    prompt_text: str = Form(...)
):
    try:
        await create_system_prompt(prompt_key, description, prompt_text)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update/{prompt_key}")
async def update_prompt_post(
    prompt_key: str,
    description: str = Form(""),
    prompt_text: str = Form(...)
):
    try:
        await update_system_prompt(prompt_key, description, prompt_text)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete/{prompt_id}")
async def delete_prompt_post(prompt_id: int):
    try:
        await delete_system_prompt(prompt_id)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVER_CONFIG["port"])
