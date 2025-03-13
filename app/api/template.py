from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import Query

from app.utils.user import get_current_user
import time

api_template = APIRouter()

templates = Jinja2Templates(directory="templates")

@api_template.get("/index/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )


@api_template.get("/file/", response_class=HTMLResponse)
async def file(request: Request, token: str = Query(None)):
    if not token:
        return RedirectResponse(url="/template/index", status_code=302)

    current_user = get_current_user(token)  
    user_id = current_user["user_id"]  
    print(user_id)

    return templates.TemplateResponse(
        request=request,
        name="file.html",
        context={"user_id": user_id}  # 传递 user_id 给前端
    )

@api_template.get("/file_manager/", response_class=HTMLResponse)
async def file_manager(request: Request, token: str = Query(None)):
    if not token:
        return RedirectResponse(url="/template/index", status_code=302)
    
    current_user = get_current_user(token)  
    user_id = current_user["user_id"]  
    
    return templates.TemplateResponse(
        request=request,
        name="file_manager.html",
        context={"user_id": user_id} 
    )
    
@api_template.get("/AI_chat/text/",response_class=HTMLResponse)
async def AI_chat_text(request: Request, token: str = Query(None)):
    if not token:
        return RedirectResponse(url="/template/index", status_code=302)
    
    current_user = get_current_user(token)  
    user_id = current_user["user_id"]  
    
    return templates.TemplateResponse(
        request=request,
        name="AI_chat_text.html",
        context={"user_id": user_id} 
    )
    
@api_template.get("/video_player/", response_class=HTMLResponse)
async def video_player(request: Request, token: str = Query(None), file_name: str = Query(None)):
    if not token:
        return RedirectResponse(url="/template/index", status_code=302)
    
    current_user = get_current_user(token)
    user_id = current_user["user_id"]
    
    # 检查传递的参数
    print(f"file_name: {file_name}, user_id: {user_id}")
    
    return templates.TemplateResponse(
        request=request,
        name="video_player.html",
        context={"user_id": user_id, "file_name": file_name}
    )
