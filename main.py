import os
from pprint import pprint
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from cafeSystem import cafeSystem


def makeOptions(webdriver):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('lang=ko_KR')
    options.add_argument('headless')
    return options

if __name__=="__main__":
    chromedriver_path = "chromedriver"
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "none"
    cafe = cafeSystem(webdriver.Chrome(os.path.join(os.getcwd(), chromedriver_path), options= makeOptions(webdriver)))
    place = cafe.dataInput()
    data = cafe.searchMain(place)
    pprint(data)