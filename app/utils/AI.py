from zhipuai import ZhipuAI
from fastapi import Depends
from app.utils.database import get_db,get_redis
import aiomysql

from app.config.default import DEFAULT_CONFIG

ZHIPU_API_KEY = DEFAULT_CONFIG['AI_config']['ZHIPU_API_KEY']

client = ZhipuAI(api_key=ZHIPU_API_KEY)

redis_client = get_redis()

async def response_stream(history, user_id, session_id):
    try:
        response = client.chat.completions.create(
            model="glm-4-air",
            messages=history, 
            top_p=0.7,
            temperature=0.95,
            max_tokens=1024,
            stream=True
        )

        full_response = "" 
        
        for trunk in response:
            if trunk.choices[0].delta.content:
                content = trunk.choices[0].delta.content
                full_response += content  
                yield content  # 返回当前的内容

        print("AI:", full_response)
        redis_client.set(session_id, full_response, ex=3600) 
        

    except Exception as e:
        yield f"发生错误：{e}"

            
            
# 获取历史消息
async def get_chat_history(cur, user_id, session_id):
    await cur.execute(
        "SELECT role, message FROM chat_history WHERE user_id = %s AND session_id = %s ORDER BY timestamp",
        (user_id, session_id)
    )
    rows = await cur.fetchall()  # 获取所有数据
    return [{"role": row["role"], "content": row["message"]} for row in rows]

# 存储消息
async def save_chat_history(cur, user_id, session_id, role, message):
    await cur.execute(
        "INSERT INTO chat_history (user_id, session_id, role, message) VALUES (%s, %s, %s, %s)",
        (user_id, session_id, role, message)
    )
    await cur.connection.commit()  # 提交事务
