import os
from pprint import pprint
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from cafeSystem import cafeSystem


options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('lang=ko_KR')
chromedriver_path = "chromedriver"
options.add_argument('headless')
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "none"
cafe = cafeSystem(webdriver.Chrome(os.path.join(os.getcwd(), chromedriver_path), options=options))
place = cafe.dataInput()
data = cafe.searchMain(place)
pprint(data)