import os
from fastapi import HTTPException
from app.config.default import DEFAULT_CONFIG

UPLOAD_DIR = DEFAULT_CONFIG["FileUpload_config"]["upload_path"]


async def save_file(file, user_id: str):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True) 
    
    file_name = file.filename  
    user_dir = f"{UPLOAD_DIR}/{user_id}"  
    file_path = f"{user_dir}/{file_name}" 
    
    file_ext = os.path.splitext(file.filename)[1]  
    file_name = os.path.splitext(file.filename)[0]  
    
     
    if not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok=True)  
    res = await file.read()  
    # 防止文件重名
    count = 1
    while os.path.exists(file_path):
        new_filename = f"{file_name}_{count}{file_ext}"
        file_path = os.path.join(user_dir, new_filename)
        count += 1
    # file_path 必须是文件路径，不能是目录路径
    with open(file_path, "wb") as f:
        f.write(res) 
    return {
        "filename": file_name,
        "path": file_path
    }  

def file_iterator(file_path, chunk_size=1024*1024):
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            # 生成器函数，每次返回一chunk
            yield chunk


