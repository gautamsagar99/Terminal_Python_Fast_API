from fastapi import FastAPI
import subprocess
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware


origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static files directory to serve the HTML file
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    # Serve the index.html file
    with open("static/index.html", "r") as f:
        content = f.read()
    return HTMLResponse(content)

@app.post("/execute/{command}")
def execute_command(command: str):
    output = execute_shell_command(command)
    return StreamingResponse(output, media_type='text/plain')

def execute_shell_command(command: str):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        yield output.rstrip('\n')

    return_code = process.poll()
    if return_code != 0:
        yield f"Command execution failed with return code: {return_code}"