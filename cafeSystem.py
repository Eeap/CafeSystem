import os, csv
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
from selenium.common import ElementNotInteractableException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By


class cafeSystem:
    def __init__(self, driver):
        self.driver = driver
        self.queryXpath = '//*[@id="search.keyword.query"]'
        self.submitXpath = '//*[@id="search.keyword.submit"]'
        self.placeList = '.placelist > .PlaceItem'
        self.menuType = '.cont_menu > .list_menu > .menuonly_type'
        self.nophotoType = '.cont_menu > .list_menu > .nophoto_type'
        self.photoType = '.cont_menu > .list_menu > .photo_type'
        self.menuName = '.info_menu > .loss_word'
        self.menuPrice = '.info_menu > .price_menu'
        self.titleList = []

    def getTitleList(self):
        return self.titleList

    def dataInput(self):
        place = input()
        return place

    def searchMain(self, place):
        self.driver.implicitly_wait(4)
        self.driver.get('https://map.kakao.com/')
        query = place + " 카페"
        path = os.path.join(os.getcwd(), query + '.csv')
        filename = query + ".csv"
        if os.path.exists(path):
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            data = pd.read_csv(filename)
            sortData = data.sort_values(by='price')
            printData = sortData[sortData['menu'].str.contains(
                '아메리카노|카페|라떼|스무디|주스|쥬스|티|차|콜드|아이스|요구르트|브루|에스프레소|모카|ICE|HOT|얼그레이|프라푸치노|커피|블렌디드|핫|카푸치노|돌체')]
            self.driver.quit()
            return printData

            # csv읽어서 정렬해서 출력
        else:
            self.search(query)
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            data = pd.read_csv(filename)
            sortData = data.sort_values(by='price')
            printData = sortData[sortData['menu'].str.contains(
                '아메리카노|카페|라떼|스무디|주스|쥬스|티|차|콜드|아이스|요구르트|브루|에스프레소|모카|ICE|HOT|얼그레이|프라푸치노|커피|블렌디드|핫|카푸치노|돌체')]
            self.driver.quit()
            return printData

    def search(self, query):
        f = open(query + ".csv", 'w')
        filewrite = csv.writer(f)
        filewrite.writerow(['menu', 'price', 'title'])
        searchQuery = self.driver.find_element(By.XPATH, self.queryXpath)
        searchQuery.send_keys(query)
        self.driver.find_element(By.XPATH, self.submitXpath).send_keys(Keys.ENTER)

        sleep(3)  # wait for searching

        page = self.driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        lists = soup.select(self.placeList)

        self.getData(lists, filewrite)
        searchQuery.clear()

        try:
            self.driver.find_element(By.XPATH, '//*[@id="info.search.place.more"]').send_keys(Keys.ENTER)
            sleep(2)

            for idx in range(2, 6):
                self.driver.find_element(By.XPATH, '//*[@id="info.search.page.no' + str(idx) + '"]').send_keys(
                    Keys.ENTER)
                sleep(2)
                page = self.driver.page_source
                soup = BeautifulSoup(page, "html.parser")
                lists = soup.select(self.placeList)
                self.getData(lists, filewrite)
        except ElementNotInteractableException:
            print("no dataList")
        finally:
            searchQuery.clear()
        f.close()

    def getData(self, lists, filewrite):
        for idx, query in enumerate(lists):
            self.getMenu(idx, filewrite)

    def getMenu(self, idx, filewrite):
        pageXpath = '//*[@id="info.search.place.list"]/li[' + str(idx + 1) + ']/div[5]/div[4]/a[1]'
        self.driver.find_element(By.XPATH, pageXpath).send_keys(Keys.ENTER)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        sleep(3)
        menu = []
        page = self.driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        title = soup.find('title').text.split("|")[0].strip()
        self.titleList.append(title)
        menuItem = soup.select(self.menuType)
        nophotoItem = soup.select(self.nophotoType)
        photoItem = soup.select(self.photoType)
        if len(menuItem) != 0:
            for v in menuItem:
                menu.append(self.parseMenu(v))
        elif len(nophotoItem) != 0:
            for v in nophotoItem:
                menu.append(self.parseMenu(v))
        elif len(photoItem) != 0:
            for v in photoItem:
                menu.append(self.parseMenu(v))
        if (len(menu) > 0):
            for item in menu:
                price = ""
                if ',' in item[1]:
                    temp = item[1].split(',')
                    for i in range(len(temp)):
                        price += temp[i]
                else:
                    price = item[1]
                if price:
                    if self.isInt(price):
                        print(price, item[0])
                        filewrite.writerow([item[0], int(price), title])
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def parseMenu(self, value):
        name = value.select(self.menuName)[0].text
        price = value.select(self.menuPrice)
        if len(price) != 0:
            price = price[0].text.split(" ")[1]
        return [name, price]

    def isInt(self, price):
        try:
            int(price)
        except ValueError:
            return False
        return True
