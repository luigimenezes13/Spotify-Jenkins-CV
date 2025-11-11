import os
import sys
from pathlib import Path
from reactpy.backend.starlette import configure, Options
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.applications import Starlette
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.App import App

load_dotenv()

static_dir = Path(__file__).parent.parent / "static"

app = Starlette()
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

configure(app, App, options=Options(url_prefix=""))

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

