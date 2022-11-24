import json
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from cafeSystem import cafeSystem
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
#chrome 옵션 설정
def makeOptions(webdriver):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('lang=ko_KR')
    return options

app = FastAPI()
@app.get("/")
async def mainPage(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})

@app.get("/get")
async def getData(request: Request,place:str):
    chromedriver_path = "chromedriver"
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "none"
    cafe = cafeSystem(webdriver.Chrome(os.path.join(os.getcwd(), chromedriver_path), options= makeOptions(webdriver)))
    # place = cafe.dataInput()
    result = cafe.searchMain(place)
    data_list = pd.DataFrame(result, columns=['menu','price','title','url']).to_json(force_ascii=False)
    return templates.TemplateResponse("cafe.html",{"request":request,
                                                   "data":json.loads(data_list),
                                                   "size":len(result)})
