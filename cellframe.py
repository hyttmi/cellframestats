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

@app.get("/nodes", response_class=HTMLResponse)
async def read_stats(request: Request):
    return templates.TemplateResponse("nodes.html", {"request": request, "active_page": "nodes",
                                                     "node_info": du.fetch_all_node_info(),
                                                     "wallets_info": nu.fetch_all_wallets_info()})

@app.get("/richlist", response_class=HTMLResponse)
async def read_stats(request: Request):
    return templates.TemplateResponse("richlist.html", {"request": request, "active_page": "richlist",
                                                     "wallets_info_top_100_cell": nu.fetch_top_100_wallets("CELL"),
                                                     "wallets_info_top_100_mcell": nu.fetch_top_100_wallets("mCELL")})