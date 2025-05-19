from fastapi import FastAPI, HTTPException
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
    format: str  # "mp3" ou "mp4"

@app.post("/convert")
def convert_video(req: RequestModel):
    url = req.url
    format = req.format.lower()

    if format not in ["mp3", "mp4"]:
        raise HTTPException(status_code=400, detail="Formato inválido. Use 'mp3' ou 'mp4'.")

    file_id = str(uuid.uuid4())
    output_path = os.path.join(FILES_DIR, f"{file_id}.%(ext)s")

    command = [
        "yt-dlp",
        "-f", "bestvideo+bestaudio/best",
        url,
        "-o", output_path,
    ]

    if format == "mp3":
        command = [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "mp3",
            "-o", output_path,
            url
        ]

    try:
        subprocess.run(command, check=True)
        final_filename = f"{file_id}.{format}"
        final_path = os.path.join(FILES_DIR, final_filename)

        if not os.path.exists(final_path):
            raise HTTPException(status_code=500, detail="Erro ao gerar o arquivo.")

        return {
            "status": "sucesso",
            "download_url": f"/download/{final_filename}"
        }

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@app.get("/download/{filename}")
def download_file(filename: str):
    filepath = os.path.join(FILES_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    return FileResponse(filepath, media_type="application/octet-stream", filename=filename)

@app.get("/")
def root():
    return {"mensagem": "Servidor está no ar!"}
