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
        self.dataList = '아메리카노|카페|라떼|스무디|주스|쥬스|티|차|콜드' \
                        '|아이스|요구르트|브루|에스프레소|모카|ICE|HOT|얼그레이' \
                        '|프라푸치노|커피|블렌디드|핫|카푸치노|돌체|요거트|시그니처|카라멜|에이드|마끼아또'
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', 4)
    # 장소를 입력하는 함수
    def dataInput(self):
        place = input()
        return place
    #검색을 돌리기 위한 메인 함수
    def searchMain(self, place):
        #크롬 드라이버가 돌아가는걸 4초 정도 기다림
        self.driver.implicitly_wait(4)
        self.driver.get('https://map.kakao.com/')
        query = place + " 카페"
        path = os.path.join(os.getcwd()+"/data/", query + '.csv')
        filename = os.path.join(os.getcwd()+"/data/",query + ".csv")
        #파일이 이미 존재하는 경우 재크롤링을 하지 않음
        if os.path.exists(path):
            printData = self.dataRead(filename)
            self.driver.quit()
            return printData
        else:
            #검색 후 저장된 데이터를 출력
            self.search(query,filename)
            printData = self.dataRead(filename)
            self.driver.quit()
            return printData
    #csv파일의 데이터를 읽어오는 함수
    def dataRead(self, filename):
        data = pd.read_csv(filename)
        sortData = data.sort_values(by='price')
        printData = sortData[sortData['menu'].str.contains(self.dataList)]
        return printData
    #실제로 검색과 저장을 하는 함수
    def search(self, query,filename):
        f = open(filename, 'w')
        filewrite = csv.writer(f)
        filewrite.writerow(['menu', 'price', 'title','url'])
        #해당 장소 카페 검색
        searchQuery = self.driver.find_element(By.XPATH, self.queryXpath)
        searchQuery.send_keys(query)
        self.driver.find_element(By.XPATH, self.submitXpath).send_keys(Keys.ENTER)
        #검색 해오는 걸 3초 정도 기다림
        sleep(3)
        #페이지 중 검색된 카페 리스트를 가져와서 lists에 저장
        page = self.driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        lists = soup.select(self.placeList)

        self.getData(lists, filewrite)
        searchQuery.clear()
        #첫번째 페이지 이후의 페이지의 데이터를 크롤링(2~5페이지)
        try:
            self.driver.find_element(By.XPATH, '//*[@id="info.search.place.more"]').send_keys(Keys.ENTER)
            sleep(2)
            # 1페이지부터 5페이지까지 크롤링
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

    #페이지에 있는 카페 리스트 중 하나씩 꺼내서 데이터를 크롤링하는 함수
    def getData(self, lists, filewrite):
        for idx, query in enumerate(lists):
            self.getMenu(idx, filewrite)
    #실제로 카페 정보를 크롤링하는 함수
    def getMenu(self, idx, filewrite):
        #상세 페이지로 넘어감()
        pageXpath = '//*[@id="info.search.place.list"]/li[' + str(idx + 1) + ']/div[5]/div[4]/a[1]'
        self.driver.find_element(By.XPATH, pageXpath).send_keys(Keys.ENTER)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        sleep(3) #페이지 로딩 3초 정도 기다림
        menu = []
        page = self.driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        title = soup.find('title').text.split("|")[0].strip()
        url = soup.head.find("meta",{"property":"og:url"}).get("content")
        #카카오맵의 menu에 대한 타입 세가지 중 데이터가 있는 타입의 데이터를 가져옴
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
                '''
                가격의 경우 빈값도 오고 단위가 1,000처럼 ,가 들어오는 부분이 있어서 
                데이터를 1000과 같이 int로 변환되게 바꿈
                '''
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
                        #데이터를 csv에 저장
                        filewrite.writerow([item[0], int(price), title, url])
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
    #메뉴와 가격의 데이터를 가져오는 함수
    def parseMenu(self, value):
        name = value.select(self.menuName)[0].text
        price = value.select(self.menuPrice)
        if len(price) != 0:
            price = price[0].text.split(" ")[1]
        return [name, price]
    #정수형으로 변환할 수 있는지 확인하는 함수
    def isInt(self, price):
        try:
            int(price)
        except ValueError:
            return False
        return True
