from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from multipart.multipart import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

root_path = "/media/music"

def get_song_generator(path, start, end):
    with open(path, mode="rb") as song:
        song.seek(start)
        yield song.read(end-start)

@app.get("/")
def home_page(request: Request):
    return templates.TemplateResponse('home/index.html', {"request": request})

@app.get("/artists")
def get_artists():

    # TODO: Setup path validation
    artists = os.listdir(path=root_path)
    artists.sort()

    content = ""
    for artist in artists:
        content += f"<button hx-get='/artists/{artist}/albums' hx-target='#music-display' hx-trigger='click'>{artist}</button>"

    return HTMLResponse(content)

@app.get("/artists/{artist}/albums")
def get_albums(artist: str):

    # TODO: Setup path validation
    albums = os.listdir(path=root_path + "/" + artist)
    albums.sort()

    content = ""
    for album in albums:
        content += f"<button hx-get='/artists/{artist}/albums/{album}' hx-target='#music-display'>{album}</button>"

    return HTMLResponse(content)

@app.get("/artists/{artist}/albums/{album}")
def get_songs(artist: str, album: str):

    # TODO: Setup path validation
    songs = os.listdir(path=root_path + "/" + artist + "/" + album)
    songs.sort()

    content = "<div id='songs'>"
    for song in songs:
        content += f"<button hx-get='/artists/{artist}/albums/{album}/songs/{song}' hx-target='#music-display'>{song}</button>"

    content += "</div>"

    return HTMLResponse(content)

@app.get("/artists/{artist}/albums/{album}/songs/{song}")
def get_audio_element(artist: str, album: str, song: str):
    return HTMLResponse(
        f"<audio autoplay controls preload='auto' src='/artists/{artist}/albums/{album}/songs/{song}/audio'></audio>"
    )

@app.get("/artists/{artist}/albums/{album}/songs/{song}/audio")
def get_audio_stream(request: Request, artist: str, album: str, song: str):
    range_header = request.headers.get("range")
    headers = {"Accept-Ranges": "bytes"}

    # TODO: Setup path validation
    path = f"{root_path}/{artist}/{album}/{song}"
    size = os.path.getsize(path)

    start = 0
    end = size

    if range_header is not None:
        print("Range request found")
        headers["Content-Length"] = f"{end-start}"
        headers["Content-Range"] = f"bytes {start}-{end}/{size}"

    return StreamingResponse(get_song_generator(path, start, end), media_type="audio/flac", headers=headers)
