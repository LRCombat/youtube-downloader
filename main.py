from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
from fastapi.responses import FileResponse
import subprocess
import os
import uuid

app = FastAPI()
FILES_DIR = "files"
os.makedirs(FILES_DIR, exist_ok=True)

class RequestModel(BaseModel):
    url: str

def download_video(url: str, format: str):
    file_id = str(uuid.uuid4())
    output_path = os.path.join(FILES_DIR, f"{file_id}.%(ext)s")

    if format == "mp3":
        command = [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "mp3",
            "-o", output_path,
            url
        ]
    else:  # mp4
        command = [
            "yt-dlp",
            "-f", "bestvideo+bestaudio/best",
            "-o", output_path,
            url
        ]

    subprocess.run(command, check=True)
    final_path = os.path.join(FILES_DIR, f"{file_id}.{format}")
    if not os.path.exists(final_path):
        raise HTTPException(status_code=500, detail="Erro ao gerar o arquivo.")
    return final_path, f"{file_id}.{format}"

@app.post("/baixar_mp3")
def baixar_mp3(url: str = Form(...)):
    path, filename = download_video(url, "mp3")
    return {"download_url": f"/download/{filename}"}

@app.post("/baixar_mp4")
def baixar_mp4(url: str = Form(...)):
    path, filename = download_video(url, "mp4")
    return {"download_url": f"/download/{filename}"}

@app.get("/download/{filename}")
def download_file(filename: str):
    filepath = os.path.join(FILES_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    return FileResponse(filepath, media_type="application/octet-stream", filename=filename)
