from datetime import datetime
import pickle
import time
import requests
import cart
import sys
import cookiemaker
import urllib.parse


class KasinaAIO:
    def __init__(self):
        sys.stdout.write(f"\rA-RT ver 0.0.4\n")
        sys.stdout.flush()
        data = '''                
        kasina       
                                  AIO by Choi10                                    
                                                                     '''
        for i in data.split("\n"):
            print(i)
            time.sleep(0.1)


        sys.stdout.write(f"\r네이버 계정 검증 시작\n")
        sys.stdout.flush()
        self.navercookie = self.cookie()
        sys.stdout.write(f"\r네이버 계정 검증 완료\n")
        sys.stdout.flush()

    def cookie(self):
        return cookiemaker.Cookiemake().naver_cookie()

    def job_start(self, data, header):
        if data["Type"] == 1:
            cart.kasinaCart().run(data, self.navercookie)
        elif data["Type"] == 2:
            num = 0
            keyword = urllib.parse.quote(data["product_code"])
            while True:
                req = requests.get(f"https://shop-api.e-ncp.com/products/search?categoryNos=&pageSize=100&pageNumber=1&filter.keywords={keyword}&order.by=MD_RECOMMEND&order.direction=ASC&filter.soldout=true&brandNos=&filter.saleStatus=ALL_CONDITIONS", headers=header)
                if len(req.json()["items"]) != 0:
                    sys.stdout.write(f"\r{req.json()['items'][0]['productName']} 발견\n")
                    sys.stdout.flush()
                    data["product_code"] = f"https://www.kasina.co.kr/product-detail/{req.json()['items'][0]['productNo']}"
                    break
                else:
                    if num == 4:
                        num = 1
                    sys.stdout.write(f"\r재고 대기중{'.'*num}")
                    sys.stdout.flush()
                    num = num+1
                    time.sleep(1)

            # cart.kasinaCart().run(data, self.navercookie)

    def save(self, data):
        pickle.dump(data, open(f'_internal/dclp.dll', 'wb'), pickle.HIGHEST_PROTOCOL)

    def load(self):
        return pickle.load(open(f'_internal/dclp.dll', 'rb'))


    def mypage(self, data):
        return cart.kasinaCart().login(data)


    def run(self):
        while True:
            while True:
                id = input("kasina ID:")
                pw = input("kasina PW:")
                try:
                    name, header = self.mypage({"ID": id, "PW": pw})
                    sys.stdout.write(f"\r{name}님 kasina AIO에 오신것을 환영합니다.\n")
                    sys.stdout.flush()
                    break
                except:
                    print("\n계정을 다시 확인해주세요.")
            while True:
                session = input("원하는 작업을 입력해주세요.\n1 온라인 링크 구매:")
                if session == "1":
                    product_code = input("URL:")
                    size = input("SIZE:")
                    Pay = input("NaverPay Password:")
                    while True:
                        timer = input("실행 예약(ex:20240131 095800\n.입력시 바로 시작):")
                        if timer == ".":
                            break

                        try:
                            inputtime = datetime.strptime(timer, '%Y%m%d %H%M%S')
                            while True:
                                sys.stdout.write(f"\r{datetime.now().strftime('%Y%m%d %H%M%S')}")
                                sys.stdout.flush()
                                if datetime.now() >= inputtime:
                                    break
                            break
                        except:
                            print("\n시간 양식을 맞춰 다시 입력해주세요.")

                    data = {
                        "Type": 1,
                        "ID": id,
                        "PW": pw,
                        "product_code": product_code,
                        "size": size,
                        "Pay": Pay,
                    }
                    self.job_start(data, None)
                elif session == "2":
                    product_code = input("키워드:")
                    size = input("SIZE:")
                    Pay = input("NaverPay Password:")
                    while True:
                        timer = input("실행 예약(ex:20240131 095800\n.입력시 바로 시작):")
                        if timer == ".":
                            break

                        try:
                            inputtime = datetime.strptime(timer, '%Y%m%d %H%M%S')
                            while True:
                                sys.stdout.write(f"\r{datetime.now().strftime('%Y%m%d %H%M%S')}")
                                sys.stdout.flush()
                                if datetime.now() >= inputtime:
                                    break
                            break
                        except:
                            print("\n시간 양식을 맞춰 다시 입력해주세요.")

                    data = {
                        "Type": 2,
                        "ID": id,
                        "PW": pw,
                        "product_code": product_code,
                        "size": size,
                        "Pay": Pay,
                    }
                    self.job_start(data, header)

KasinaAIO().run()
