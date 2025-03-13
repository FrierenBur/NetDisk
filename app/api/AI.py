from fastapi import APIRouter,Depends
from fastapi.responses import StreamingResponse
import uuid
from app.utils.AI import response_stream,get_chat_history,save_chat_history
from app.schemas.AI_chat import ChatRequest
from app.utils.database import get_db,get_redis

redis_client = get_redis()
api_AI = APIRouter()

@api_AI.post("/chat/text")
async def chat_text(request: ChatRequest, cur=Depends(get_db)):
    
    session_id = request.session_id or str(uuid.uuid4())
    
    history = await get_chat_history(cur, request.user_id, session_id)
    history.append({"role": "user", "content": request.message})

    #!  这里有个问题：就是保存的聊天记录会有一条遗漏，顺序虽然是对的
    full_response = redis_client.get(session_id) or "暂无记录"
    await save_chat_history(cur, request.user_id, session_id, "assistant", full_response)  
    
    await save_chat_history(cur, request.user_id, session_id, "user", request.message)
    print("用户:",request.message)
    
    
    return StreamingResponse(response_stream(history, request.user_id, session_id), media_type="text/plain", headers={"X-Session-ID": session_id})
