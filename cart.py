import random
import time
import cv2
import numpy as np
import pytesseract
from PIL import Image
import requests
import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class kasinaCart:
    def __init__(self):
        self.driver = None

    def url_setting(self, url):
        return url.split("product-detail/")[-1].split("?")[0]

    def login(self, data):

        header = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json',
            'Origin': 'https://www.kasina.co.kr',
            'Referer': 'https://www.kasina.co.kr',
            'Sec-Fetch-Dest': 'empty',
            'User-Agent': '',
            'Device-uuid': ''
        }
        data = {
            "password": data["PW"],
            "username": data["ID"]
        }
        authenticate = requests.post("https://shop-api.kasina.co.kr/api/v1/authenticate", headers=header, data=json.dumps(data))

        requests.options('https://shop-api.e-ncp.com/oauth/openid', headers=header)
        header["clientid"] = ""
        header["Platform"] = "IOS"
        header["Version"] = "1.0"

        openid = {
            'noAccessToken': True,
            'openAccessToken': authenticate.json()["refreshToken"],
            'provider': 'ncpstore'
        }
        accessToken = requests.post('https://shop-api.e-ncp.com/oauth/openid', headers=header, data=json.dumps(openid)).json()["accessToken"]
        header["accesstoken"] = accessToken
        requests.get("https://shop-api.e-ncp.com/profile", headers=header)
        header["Authorization"] = f'Bearer {authenticate.json()["accessToken"]}'

        req = requests.get("https://shop-api.kasina.co.kr/api/v1/members", headers=header)

        return req.json()["name"], header

    def cart(self, product_code, header, data):
        url = f"https://shop-api.e-ncp.com/products/{product_code}/options?useCache=true"
        payload = {}
        req = requests.get(url, headers=header, data=payload)
        option = ""
        for i in req.json()["multiLevelOptions"]:
            if str(i["value"])==str(data["size"]):
                if i["stockCnt"] != 0:
                    option = str(i["optionNo"])
                    break
        if option == "":
            for i in req.json()["multiLevelOptions"]:
                if i["stockCnt"] != 0:
                    option = str(i["optionNo"])
                    break
        url = "https://shop-api.e-ncp.com/order-sheets"
        payload = {
            "products": [
                {
                    "optionNo": int(option),
                    "orderCnt": 1,
                    "productNo": int(product_code)
                }
            ]
        }

        orderSheetNo = requests.post(url, headers=header, data=json.dumps(payload))

        req = requests.get(f'https://shop-api.e-ncp.com/order-sheets/{orderSheetNo.json()["orderSheetNo"]}?includeMemberAddress=true', headers=header)
        address = req.json()["orderSheetAddress"]["recentAddresses"][0]
        ordererContact = req.json()["ordererContact"]
        payload = {
            "payType": "NAVER_EASY_PAY",
            "member": True,
            "saveAddressBook": False,
            "updateMember": False,
            "orderSheetNo": str(orderSheetNo.json()["orderSheetNo"]),
            "pgType": "NAVER_EASY_PAY",
            "subPayAmt": "0",
            "paymentAmtForVerification": req.json()["paymentInfo"]["cartAmt"],
            "orderer": ordererContact,
            "clientReturnUrl": f"https://www.kasina.co.kr/order/{orderSheetNo.json()['orderSheetNo']}/confirm",
            "shippingAddress": address,
            "useDefaultAddress": False,
            "coupons": {
                "productCoupons": [],
                "cartCouponIssueNo": 0,
                "promotionCode": "",
                "channelType": ""
            },
            "inAppYn": "N",
            "extraData": {
                "appUrl": ""
            }
        }
        payments = requests.post("https://api.e-ncp.com/payments/reserve", data=json.dumps(payload), headers=header)
        payload = {
            "merchantUserKey": payments.json()["extraData"]["sdkParam"]["merchantUserKey"],
            "merchantPayKey": payments.json()["extraData"]["sdkParam"]["merchantPayKey"],
            "productName": payments.json()["extraData"]["sdkParam"]["productName"],
            "totalPayAmount": payments.json()["extraData"]["sdkParam"]["totalPayAmount"],
            "taxScopeAmount": payments.json()["extraData"]["sdkParam"]["taxScopeAmount"],
            "taxExScopeAmount": payments.json()["extraData"]["sdkParam"]["taxExScopeAmount"],
            "returnUrl": payments.json()["extraData"]["sdkParam"]["returnUrl"],
            "productItems": payments.json()["extraData"]["sdkParam"]["productItems"],
            "productCount": payments.json()["extraData"]["sdkParam"]["productCount"],
            "clientId": payments.json()["extraData"]["sdkCreateKey"]["clientId"],
            "merchantOriginUrl": "https://www.kasina.co.kr"
        }


        req = requests.post("https://nsp.pay.naver.com/payments/sdk/reserve", data=json.dumps(payload), headers=header)
        return f'https://m.pay.naver.com/z/payments/{req.json()["body"]["reserveId"]}'

    def info(self, product_code, header):
        url = f"https://shop-api.e-ncp.com/products/{product_code}?useCache=true"
        payload = {}
        req = requests.get(url, headers=header, data=payload)
        return req.json()

    def wait_for(self, el_type, element):
        while True:
            try:
                if el_type == "ID":
                    self.driver.find_element(By.ID, element)
                elif el_type == "XPATH":
                    self.driver.find_element(By.XPATH, element)
                elif el_type == "NAME":
                    self.driver.find_element(By.NAME, element)
                elif el_type == "CLASS_NAME":
                    self.driver.find_element(By.CLASS_NAME, element)
                time.sleep(0.1)
            except:
                break

    def wait_for_second(self, el_type, element):
        num = 0
        while True:
            try:
                if el_type == "ID":
                    self.driver.find_element(By.ID, element)
                elif el_type == "XPATH":
                    self.driver.find_element(By.XPATH, element)
                elif el_type == "NAME":
                    self.driver.find_element(By.NAME, element)
                elif el_type == "CLASS_NAME":
                    self.driver.find_element(By.CLASS_NAME, element)
                return False
            except:
                if num == 100:
                    return True
                else:
                    num = num + 1
                    time.sleep(0.1)
                    pass

    def driver_setting(self, header):
        chrome_options = Options()
        chrome_options.add_argument(f"User-Agent={header['User-Agent']}")
        # chrome_options.add_argument("headless")
        chrome_options.add_argument('log-level=3')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        return driver


    def automatic(self, cart_url, naver_cookie, data, product_code, header):
        sys.stdout.write(f"\r네이버 계정 검증\n")
        sys.stdout.flush()
        self.driver = self.driver_setting(header)
        self.driver.get("https://new-m.pay.naver.com/historybenefit/home")
        self.driver.delete_all_cookies()
        for i in naver_cookie:
            self.driver.add_cookie(i)
        self.driver.get('https://new-m.pay.naver.com/historybenefit/home')

        sys.stdout.write(f"\r결제창 진입\n")
        sys.stdout.flush()
        self.driver.get(cart_url)

        sys.stdout.write(f"\r네이버페이 결제 진행\n")
        sys.stdout.flush()
        self.naver_pay(product_code, header, data)



    def naver_pay(self, product_code, header, data):
        self.wait_for_second('XPATH', '//label[@for="card"]')
        self.driver.find_element(By.XPATH, '//label[@for="card"]').click()
        try:
            self.driver.find_element(By.ID, 'f_s2').click()
            self.driver.find_element(By.XPATH, '//option[@value="03"]').click()
        except:
            pass
        self.driver.find_element(By.CLASS_NAME, 'button_bottom').click()
        while True:
            if "authentication" in self.driver.current_url:
                break
            else:
                pass

        sys.stdout.write(f"\r결제 OCR 진행\n")
        sys.stdout.flush()
        self.driver.save_screenshot('screenshot.png')
        self.pay_key_orc(data)

    def pay_key_orc(self, data):
        pytesseract.pytesseract.tesseract_cmd = r'_internal\Tesseract\tesseract.exe'
        image = cv2.imread('screenshot.png')

        height, width = image.shape[:2]
        midpoint = height // 2

        mask_color = (255, 255, 255)  # Assuming white background
        upper_half_mask = np.full((midpoint, width, 3), mask_color, dtype=np.uint8)

        image[0:midpoint, :] = upper_half_mask

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        invert = 255 - thresh
        custom_config = r'--oem 3 --psm 6'
        text_data = pytesseract.image_to_data(invert, config=custom_config, lang='eng+kor', output_type=pytesseract.Output.DICT)
        screenshot_image = Image.open('screenshot.png')
        screenshot_size = screenshot_image.size
        viewport_size = self.driver.execute_script("return [window.innerWidth, window.innerHeight];")
        scale = screenshot_size[0] / viewport_size[0]
        for i in range(len(data["Pay"])):
            x, y = self.get_ocr_pos(text_data, data["Pay"][i])
            script = """
                var element = document.elementFromPoint(arguments[0], arguments[1]);
                if (element) {
                    element.click();
                }
            """
            self.driver.execute_script(script, x, y)

    def get_ocr_pos(self, text_data, num):
        target_number = str(num)
        for i, text in enumerate(text_data['text']):
            if text == target_number:
                x = text_data['left'][i] + text_data['width'][i] / 2
                y = text_data['top'][i] + text_data['height'][i] / 2
        return x, y

    def check_stock(self, urls, product_code, header, data):
        if "onthespot" in urls:
            url = "https://www.onthespot.co.kr/"
        elif "grandstage" in urls:
            url = "https://grandstage.a-rt.com/"
        else:
            url = "https://abcmart.a-rt.com/"
        url = f"{url}product/info?prdtNo=" + product_code
        stock = 0
        num = 0
        while True:
            req = requests.get(url, headers=header)
            for i in req.json()["productOption"]:
                if str(i["optnName"]) == data['size']:
                    stock = i["totalStockQty"]-i["totalOrderQty"]
                    break
            if num == 4:
                num = 1
            sys.stdout.write(f"\r재고 대기중{'.'*num}")
            sys.stdout.flush()
            num = num+1
            if stock>0:
                # print(json.dumps(req.json(), ensure_ascii=False, indent=4))
                break
            else:
                time.sleep(0.2)

    def draw_info(self, product_code):
        url = f'https://static.shoeprize.com/campaign/json/kasina-{product_code}.json'
        return requests.get(url).json()

    def terms(self, data):
        from datetime import datetime, timezone, timedelta
        now = datetime.now()
        kst = timezone(timedelta(hours=9))
        now_kst = now.astimezone(kst)
        formatted_time = now_kst.strftime('%Y-%m-%dT%H:%M:%S%z')
        terms = {}
        for i in data["terms"]["campaign-participate"]:
            terms.update({i:{
                "approve": True,
                "approvedAt": formatted_time,
                "unapprovedAt": ""}
            })
        return terms

    def draw(self, data):
        sys.stdout.write(f"\r응모 시작\n")
        sys.stdout.flush()
        product_code = data["product_code"]
        product_code = self.url_setting(product_code)

        sys.stdout.write(f"\rkasina Login\n")
        sys.stdout.flush()
        n, header = self.login(data)
        sys.stdout.write(f"\r제품 정보 취득\n")
        sys.stdout.flush()
        while True:
            try:
                product_info = self.draw_info(product_code)
                break
            except:
                time.sleep(0.3)

        sys.stdout.write(f'\r{product_info["title"]} {product_info["url"]}\n')
        sys.stdout.flush()

        sys.stdout.write(f"\r응모 시작\n")
        sys.stdout.flush()
        tokens = requests.post("https://shop-api.kasina.co.kr/api/v1/campaign/token", headers=header)

        tokenss = {
            "jwtToken": tokens.json()["token"]
        }
        tokensss = requests.post(f"https://campaign-api.shoeprize.com/campaign/kasina/{product_code}/token/member", headers=header, data=json.dumps(tokenss))
        header_campaign = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ko-KR,ko;q=0.9',
            'Content-Type': 'application/json',
            'Origin': 'https://launches.kasina.co.kr',
            'Sec-Fetch-Dest': 'cors',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebkit/605.1.15 (KHTML, like Gecko)  Mobile/15E148 Kasina/2.0.6',
            'Authorization': f'Bearer {tokensss.json()["token"]}'
        }
        draw_page = requests.get(f"https://campaign-api.shoeprize.com/campaign/kasina/{product_code}", headers=header_campaign)

        option = None
        for i in product_info["modules"][1]["form"][1]["options"]:
            if str(i["label"]) == str(data["size"]):
                option = i["value"]
        if option == None:
            i = random.choice(product_info["modules"][1]["form"][1]["options"])
            option = i["value"]

        draw_data = {
            "channel": "APP",
            "email": draw_page.json()["user"]["email"],
            "name": draw_page.json()["user"]["name"],
            "phone": draw_page.json()["user"]["phone"],
            "rewardOptionalId": product_info["modules"][1]["form"][0]["value"],
            "rewardOptionalOption": option,
            "terms": self.terms(product_info)
        }
        requests.post(f"https://campaign-api.shoeprize.com/campaign/kasina/{product_code}", headers=header_campaign, data=json.dumps(draw_data))
        sys.stdout.write(f"\r응모 완료\n")
        sys.stdout.flush()

    def run(self, data, naver_cookie):
        sys.stdout.write(f"\r구매 시작\n")
        sys.stdout.flush()
        product_code = data["product_code"]
        product_code = self.url_setting(product_code)

        sys.stdout.write(f"\rkasina Login\n")
        sys.stdout.flush()
        n, header = self.login(data)
        sys.stdout.write(f"\r제품 정보 취득\n")
        sys.stdout.flush()
        product_info = self.info(product_code, header)
        sys.stdout.write(f'\r{product_info["baseInfo"]["productNameEn"]} {product_info["baseInfo"]["productManagementCd"]}\n')
        sys.stdout.flush()
        sys.stdout.write(f"\r장바구니 담기 시작\n")
        sys.stdout.flush()
        while True:
            try:
                cart_url = self.cart(product_code, header, data)
                break
            except:
                time.sleep(0.5)

        sys.stdout.write(f"\r구매 시작\n")
        sys.stdout.flush()
        self.automatic(cart_url, naver_cookie, data, product_code, header)


        self.wait_for_second('CLASS_NAME', 'c-headline__title')
        self.driver.close()
        self.driver.quit()
        sys.stdout.flush()
        sys.stdout.write(f"\r결제 완료\n")
