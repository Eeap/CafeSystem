import json
import os
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from cafeSystem import cafeSystem
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
app = FastAPI()
templates = Jinja2Templates(directory="templates")
#chrome 옵션 설정
def makeOptions(webdriver):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('lang=ko_KR')
    options.add_argument("disable-gpu")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    return options

app = FastAPI()
@app.get("/")
async def mainPage(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})

@app.get("/get")
async def getData(request: Request,place:str):
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "none"
    cafe = cafeSystem(webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=makeOptions(webdriver)))
    # place = cafe.dataInput()
    data_list = cafe.searchMain(place)
    return templates.TemplateResponse("cafe.html",{"request":request,
                                                   "data":json.loads(data_list)})
