import requests
import json
import pandas as pd
import urllib3
import os
from datetime import datetime
from geopy.geocoders import Nominatim


def get_all_data():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    all_data = []
    page = 1
    has_more_data = True

    while has_more_data:
        url = f"https://m.land.naver.com/cluster/ajax/articleList?rletTpCd=DDDGG&tradTpCd=A1&z=12&lat=37.5443251&lon=126.9867247&btm=37.4228186&lft=126.7970389&top=37.6656339&rgt=127.1764105&spcMin=66&spcMax=165&dprcMin=40000&dprcMax=80000&tag=PARKINGYN&cortarNo%20=1100000000&page={page}"
        response = requests.get(url,  headers={
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language" : "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
             "Host" : "m.land.naver.com",
            "Referer" : "https://m.land.naver.com/",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "Content-Type" : "application/json;charset=UTF-8" ,
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.39"
        }, verify=False)
        response.encoding = "utf-8-sig"

        data = json.loads(response.text)
        article_list = data.get("body", [])
        all_data.extend(article_list)

        # 현재 페이지가 마지막 페이지인지 확인
        has_more_data = data.get("more", False)
        page += 1

    # print(all_data)
    return all_data


    
def get_real_address(latitude, longitude):
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.reverse((latitude, longitude), exactly_one=True)
    if location:
        return location.address
    return ""

# 제곱미터(m^2)를 평수로 변환하는 함수
def sqm_to_pyung(sqm):
    return int(sqm / 3.305785)


def save_to_excel(data_list):
    print("Start save_to_excel")
    df = pd.DataFrame(data_list)

    today_date = datetime.now().strftime("%Y%m%d")
    file_name = f"[{today_date}] 다가구주택리스트.xlsx"
    
    # Check if the file exists and delete it if it does
    if os.path.exists(file_name):
        os.remove(file_name)
        
    # seoul_data = df[df["실제주소"].str.contains("서울")]
    # seoul_data.to_excel(file_name, index=False)
    df.to_excel(file_name, index=False)
    print("Data saved to output.xlsx")

if __name__ == '__main__':
    
    # response_text = getDataList()
    # # JSON 텍스트를 파싱하여 딕셔너리로 변환
    # data = json.loads(response_text)
    article_list = get_all_data()


    # article_list = data.get("body", [])

    # articleList에 있는 모든 아이템들의 필드를 파싱하여 저장

    cnt = 0
    parsed_data = []

    for article in article_list:
        
        parsed_article = {
            "매물번호" : article.get("atclNo", ""),
            "매물URL": "https://m.land.naver.com/article/info/"+ article.get("atclNo", ""),
            "등록일자": article.get("atclCfmYmd", ""),
            "주택종류": article.get("realEstateTypeName", ""),   
            "주택종류명": article.get("atclNm", ""),         
            "매매가격": article.get("hanPrc", ""),
            "동일매물최저가격": article.get("sameAddrMinPrc", ""),
            "층정보": article.get("flrInfo", ""),
            "매물설명": article.get("atclFetrDesc", ""),
            "대지평수": sqm_to_pyung(float(article.get("spc1", ""))),
            "총평수": sqm_to_pyung(float(article.get("spc2", ""))),
            "대지면적": article.get("spc1", ""),
            "총면적": article.get("spc2", ""),
            "매물태그": article.get("tagList", ""),
            "실제주소": get_real_address(article.get("lat","0"), article.get("lng","0"))
            
        }
        parsed_data.append(parsed_article)
        cnt=cnt+1
        if cnt % 10 == 0:
            print(f"{cnt}번째 처리 중")
            

    # 엑셀로 저장
    save_to_excel(parsed_data)

