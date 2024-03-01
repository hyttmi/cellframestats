from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import node_utils as nu


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    masternodes = nu.fetch_active_nodes()
    total_blocks = nu.fetch_blocks_on_main()
    wallets = nu.fetch_all_activated_wallets()
    return templates.TemplateResponse("index.html", {"request": request, "active_nodes": masternodes, "main_blocks": total_blocks, "active_wallets": wallets})

@app.get("/stats", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("stats.html", {"request": request})

