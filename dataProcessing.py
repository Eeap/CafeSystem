import pandas as pd

class dataProcess:
    def __init__(self,filename):
        self.filename = filename
        self.dataList = '아메리카노|카페|라떼|스무디|주스|쥬스|티|차|콜드' \
                        '|아이스|요구르트|브루|에스프레소|모카|ICE|HOT|얼그레이' \
                        '|프라푸치노|커피|블렌디드|핫|카푸치노|돌체|요거트|시그니처|카라멜|에이드|마끼아또'
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', 4)
    # csv파일의 데이터를 읽어오는 함수
    def dataRead(self):
        data = pd.read_csv(self.filename)
        sortData = data.sort_values(by='price')
        dataFrame = sortData[sortData['menu'].str.contains(self.dataList)]
        dataJson = pd.DataFrame(dataFrame, columns=['menu', 'price', 'title', 'url']).to_json(force_ascii=False)
        return dataJson
