from fastapi import APIRouter, Query,HTTPException
from fastapi import File, UploadFile,Form,Header
from fastapi.responses import StreamingResponse,Response
from typing import List
import urllib.parse
import os, shutil

from app.utils.file import save_file, file_iterator
from app.config.default import DEFAULT_CONFIG


UPLOAD_DIR = DEFAULT_CONFIG["FileUpload_config"]["upload_path"]

api_file = APIRouter()

# 利用user-id作为区分用户的唯一标识，将上传的文件保存在用户的文件夹下

@api_file.post("/upload/file")
async def upload_file(
    user_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    if not files:
        return {"提示": "未上传文件！"}

    uploaded_files = []
    for file in files:
        try:
            await save_file(file, user_id)
            uploaded_files.append(file.filename)
        except Exception as e:
            return {"错误": f"文件 {file.filename} 上传失败: {str(e)}"}

    return {"上传成功": uploaded_files}

@api_file.get("/download/file/{file_name}")
async def download_file(file_name: str, user_id: str = Query(...)):
    file_path = os.path.join(UPLOAD_DIR, user_id, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 防止中文乱码
    encoded_file_name = urllib.parse.quote(file_name.encode("utf-8"))
    
    return StreamingResponse(
        file_iterator(file_path),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={encoded_file_name}"}
    )


@api_file.delete("/delete/file/{file_name}")
def delete_file(file_name: str, user_id: str = Query(...)):
    file_path = os.path.join(UPLOAD_DIR, user_id, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        os.remove(file_path)
        return {"提示": f"文件{file_name}删除成功！"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件{file_name}删除失败: {str(e)}")
    

@api_file.patch("/rename/file/{file_name}")
async def rename_file(file_name: str, 
                      new_file_name: str = Query(...),
                      user_id: str = Query(...)):
    origin_file_path = os.path.join(UPLOAD_DIR, user_id, file_name)
    if not os.path.exists(origin_file_path):
        raise HTTPException(status_code=404, detail="修改名称的文件不存在")
    
    # 获取文件后缀名
    _, file_extention = os.path.splitext(file_name)
    new_file_name = f"{new_file_name}{file_extention}"
    
    new_file_path = os.path.join(UPLOAD_DIR, user_id, new_file_name)
    if os.path.exists(new_file_name):
        raise HTTPException(status_code=400, detail="新文件名已存在,请重新输入")
    
    try:
        shutil.move(origin_file_path, new_file_path)
        return {"提示": f"文件{file_name}重命名为{new_file_name}成功！"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件{file_name}重命名失败: {str(e)}")
    
    
@api_file.get("/search/file_all/{user_id}")
async def search_file_all(user_id: str):
    folder_path = f"{UPLOAD_DIR}/{user_id}"
    
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="用户目录不存在")
    files = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path) / 1024  # 单位 KB
            files.append({"filename": filename, "size": round(file_size, 2)})
    
    return files



@api_file.get("/video/stream")
async def stream_video(filename: str, user_id: str, range: str = Header(None)):
    folder_path = f"{UPLOAD_DIR}/{user_id}"
    file_path = os.path.join(folder_path, filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        return Response("Video not found", status_code=404)

    file_size = os.path.getsize(file_path)
    start, end = 0, file_size - 1

    # Handle Range request
    if range:
        # Parse the Range header
        start = int(range.replace("bytes=", "").split("-")[0])
        end = min(start + 1024 * 1024, file_size - 1)  # 每次传输 1MB

    def iterfile():
        with open(file_path, "rb") as f:
            f.seek(start)
            while chunk := f.read(1024 * 1024):
                yield chunk

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(end - start + 1),
        "Content-Type": "video/mp4",
    }
    
    return StreamingResponse(iterfile(), status_code=206, headers=headers)
