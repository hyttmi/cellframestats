from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def return_42():
    return 42

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    value = return_42()
    return templates.TemplateResponse("index.html", {"request": request, "value": value})
