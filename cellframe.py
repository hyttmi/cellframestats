import asyncio
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException


import node_utils as nu
import database_utils as du
import common as co

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

async def run_async(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    all_active_nodes = await run_async(du.fetch_all_active_nodes)
    main_blocks = await run_async(du.fetch_blocks_on_main)
    activated_wallets = await run_async(du.fetch_all_activated_wallets)
    all_transactions = await run_async(du.fetch_all_transactions)
    staked_tokens = await run_async(du.fetch_all_staked_tokens)
    return templates.TemplateResponse("index.html", {"request": request, "active_page": "home",
                                                     "active_nodes": all_active_nodes,
                                                     "main_blocks": main_blocks,
                                                     "active_wallets": activated_wallets,
                                                     "all_transactions": all_transactions,
                                                     "all_stakes": staked_tokens})

@app.get("/stats", response_class=HTMLResponse)
async def read_stats(request: Request):
    latest_blocks = await run_async(du.chart_daily_blocks, 120)
    latest_transactions = await run_async(du.chart_daily_transactions, 120)
    latest_stakes = await run_async(du.fetch_latest_stakes, 20)
    return templates.TemplateResponse("stats.html", {"request": request, "active_page": "stats",
                                                     "latest_120_blocks": latest_blocks,
                                                     "latest_120_transactions": latest_transactions,
                                                     "latest_stakes": latest_stakes})

@app.get("/nodes", response_class=HTMLResponse)
async def read_nodes(request: Request):
    all_node_info = await run_async(du.fetch_all_node_info)
    return templates.TemplateResponse("nodes.html", {"request": request, "active_page": "nodes",
                                                     "node_info": all_node_info})

@app.get("/richlist", response_class=HTMLResponse)
async def read_richlist(request: Request):
    top_wallets_cell = await run_async(du.fetch_top_wallets, "CELL", 50)
    top_wallets_mcell = await run_async(du.fetch_top_wallets, "mCELL", 50)
    top_stakes = await run_async(du.fetch_stakes, 50)
    return templates.TemplateResponse("richlist.html", {"request": request, "active_page": "richlist",
                                                     "wallets_info_top_cell": top_wallets_cell,
                                                     "wallets_info_top_mcell": top_wallets_mcell,
                                                     "fetch_stakes": top_stakes})

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse("error.html", {"request": request, "code": exc.status_code,
                                                     "msg": exc.detail,
                                                     "url": request.url.path})

@app.post("/submit")
async def submit_form(wallet: str = Form(...)):
    msg = co.validate_input(wallet)
    return msg

@app.get("/node_info")
async def get_node_info(address: str):
    result = du.fetch_node_info_by_addr(address)
    if result:
        return result
    else:
        return {"error": "Node not found"}
