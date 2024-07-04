from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from multipart.multipart import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def get_song_generator(start, end):
    with open("/media/music/Bas/Too High to Riot/09 Night Job.flac", mode="rb") as song:
        song.seek(start)
        yield song.read(end-start)

@app.get("/")
def home_page(request: Request):
    return templates.TemplateResponse('home/index.html', {"request": request})

@app.get("/audio/selection")
def search_books():
    return HTMLResponse(
        """
        <div>
            <audio controls preload="auto" src="/audio"></audio>
        </div>
        """
    )

@app.get("/audio")
async def get_audio(request: Request):
    range_header = request.headers.get("range")
    print(f"range-header: {range_header}")

    headers = {"Accept-Ranges": "bytes"}

    size = os.path.getsize("/media/music/Bas/Too High to Riot/09 Night Job.flac")

    start = 0
    end = size

    if range_header is not None:
        print("Range request found")
        headers["Content-Length"] = f"{end-start}"
        headers["Content-Range"] = f"bytes {start}-{end}/{size}"

    return StreamingResponse(get_song_generator(start, end), media_type="audio/flac", headers=headers)
