from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import node_utils as nu
import database_utils as du

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "active_page": "home",
                                                     "active_nodes": nu.fetch_active_nodes(),
                                                     "main_blocks": du.fetch_blocks_on_main(),
                                                     "active_wallets": nu.fetch_all_activated_wallets(),
                                                     "all_transactions": du.fetch_all_transactions(),
                                                     "all_stakes": du.fetch_all_staked_tokens()})

@app.get("/stats", response_class=HTMLResponse)
async def read_stats(request: Request):
    return templates.TemplateResponse("stats.html", {"request": request, "active_page": "stats",
                                                     "latest_7_blocks": du.chart_daily_blocks(7),
                                                     "latest_30_blocks": du.chart_daily_blocks(30),
                                                     "latest_120_blocks": du.chart_daily_blocks(120)})