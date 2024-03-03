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
    masternodes = nu.fetch_active_nodes()
    total_blocks = nu.fetch_blocks_on_main()
    wallets = nu.fetch_all_activated_wallets()
    all_tx = du.fetch_all_transactions()
    all_stakes = du.fetch_all_staked_tokens()
    return templates.TemplateResponse("index.html", {"request": request, "active_page": "home", "active_nodes": masternodes, "main_blocks": total_blocks, "active_wallets": wallets, "all_transactions": all_tx,
                                                     "all_stakes": all_stakes})

@app.get("/stats", response_class=HTMLResponse)
async def read_stats(request: Request):
    get_7_blocks = du.chart_daily_blocks(7)
    get_30_blocks = du.chart_daily_blocks(30)
    get_365_blocks = du.chart_daily_blocks(365)
    return templates.TemplateResponse("stats.html", {"request": request, "active_page": "stats", "latest_7_blocks": get_7_blocks, "latest_30_blocks": get_30_blocks, "latest_365_blocks": get_365_blocks})