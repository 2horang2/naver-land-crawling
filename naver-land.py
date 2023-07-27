import requests
import json
import pandas as pd
import urllib3
import os
from datetime import datetime
from geopy.geocoders import Nominatim

tradTpCd = [
    {'tagCd': 'A1', 'uiTagNm': '매매'},
    {'tagCd': 'B1', 'uiTagNm': '전세'},
    {'tagCd': 'B2', 'uiTagNm': '월세'},
    {'tagCd': 'B3', 'uiTagNm': '단기임대'}
]

rletTpCd = [
    {'tagCd': 'APT', 'uiTagNm': '아파트'}, 
    {'tagCd': 'OPST', 'uiTagNm': '오피스텔'}, 
    {'tagCd': 'VL', 'uiTagNm': '빌라'},
    {'tagCd': 'ABYG', 'uiTagNm': '아파트분양권'}, 
    {'tagCd': 'OBYG', 'uiTagNm': '오피스텔분양권'}, 
    {'tagCd': 'JGC', 'uiTagNm': '재건축'},
    {'tagCd': 'JWJT', 'uiTagNm': '전원주택'}, 
    {'tagCd': 'DDDGG', 'uiTagNm': '단독/다가구'}, 
    {'tagCd': 'SGJT', 'uiTagNm': '상가주택'},
    {'tagCd': 'HOJT', 'uiTagNm': '한옥주택'}, 
    {'tagCd': 'JGB', 'uiTagNm': '재개발'}, 
    {'tagCd': 'OR', 'uiTagNm': '원룸'},
    {'tagCd': 'GSW', 'uiTagNm': '고시원'}, 
    {'tagCd': 'SG', 'uiTagNm': '상가'}, 
    {'tagCd': 'SMS', 'uiTagNm': '사무실'},
    {'tagCd': 'GJCG', 'uiTagNm': '공장/창고'}, 
    {'tagCd': 'GM', 'uiTagNm': '건물'}, 
    {'tagCd': 'TJ', 'uiTagNm': '토지'},
    {'tagCd': 'APTHGJ', 'uiTagNm': '지식산업센터'}
]


def get_all_data(trad_tag_cd,rlet_tag_cd,minPrice,maxPrice,minPyeong,maxPyeong):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    all_data = []
    page = 1
    has_more_data = True

    url = f"https://m.land.naver.com/cluster/ajax/articleList?rletTpCd={rlet_tag_cd}&tradTpCd={trad_tag_cd}&z=12&lat=37.5443251&lon=126.9867247&btm=37.4228186&lft=126.7970389&top=37.6656339&rgt=127.1764105&spcMin={minPyeong}&spcMax={maxPyeong}&dprcMin={minPrice}&dprcMax={maxPrice}&tag=PARKINGYN&cortarNo%20=1100000000&page={page}" 
    print(url)

    while has_more_data:
        url = f"https://m.land.naver.com/cluster/ajax/articleList?rletTpCd={rlet_tag_cd}&tradTpCd={trad_tag_cd}&z=12&lat=37.5443251&lon=126.9867247&btm=37.4228186&lft=126.7970389&top=37.6656339&rgt=127.1764105&spcMin={minPyeong}&spcMax={maxPyeong}&dprcMin={minPrice}&dprcMax={maxPrice}&tag=PARKINGYN&cortarNo%20=1100000000&page={page}"
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



def save_to_excel(data_list, input_area):
    print("Start save_to_excel")
    df = pd.DataFrame(data_list)

    today_date = datetime.now().strftime("%Y%m%d")
    file_name = f"[{today_date}] 네이버부동산필터링리스트.xlsx"
    
    # Check if the file exists and delete it if it does
    if os.path.exists(file_name):
        os.remove(file_name)        
    
    seoul_data = df[df["실제주소"].str.contains(input_area)]
    print("Total count of filtered data : ",len(seoul_data))
    seoul_data.to_excel(file_name, index=False)
    # f.to_excel(file_name, index=False)
    print("Data saved to output.xlsx")



def find_tag_cd_by_ui_tag_nm(ui_tag_nm, tag_list):
    for item in tag_list:
        if item['uiTagNm'] == ui_tag_nm:
            return item['tagCd']
    return None


def print_valid_tags(tag_list):
    valid_tags = [tag['uiTagNm'] for tag in tag_list]
    print("유효한 값:", ", ".join(valid_tags))

def get_valid_input(prompt, tag_list):
    while True:
        user_input = input(prompt)
        tag_cd = find_tag_cd_by_ui_tag_nm(user_input, tag_list)
        if tag_cd:
            return tag_cd
        else:
            print(f"유효하지 않은 값입니다. 다시 입력해주세요.")
            print_valid_tags(tag_list)

if __name__ == '__main__':


    # 매매유형 입력 받기
    print("매매유형을 입력해주세요.")
    print_valid_tags(tradTpCd)
    trad_tag_cd = get_valid_input("매매유형: ", tradTpCd)

    # 주택유형 입력 받기
    print("\n주택유형을 입력해주세요.")
    print_valid_tags(rletTpCd)
    rlet_tag_cd = get_valid_input("주택유형: ", rletTpCd)

    print("\n서울 내에서 검색 원하는 지역 단어를 하나만 입력해주세요.")
    input_area = input()

    
    print("\n최소 가격을 입력해주세요. (억)")
    minPrice = input()    
    print("최대 가격을 입력해주세요. (억)")
    maxPrice = input()
    print("최소 평수를 입력해주세요.")
    minPyeong = input()    
    print("최대 평수를 입력해주세요.")
    maxPyeong = input()

    minPrice = int(minPrice)*10000
    maxPrice = int(maxPrice)*10000
    minPyeong = int(float(minPyeong) * 3.3)
    maxPyeong = int(float(maxPyeong) * 3.3)


    print("\n-----------------------------------------------------------")
    print("입력된 매매유형 tagCd 값:", trad_tag_cd)
    print("입력된 주택유형 tagCd 값:", rlet_tag_cd)
    print("입력된 주소값:", input_area)
    print("입력된 가격 범위:", minPrice," ~ ",maxPrice,"만원")
    print("입력된 면적 범위:", minPyeong," ~ ",maxPyeong,"m2")
    print("-----------------------------------------------------------")

    # response_text = getDataList()
    # # JSON 텍스트를 파싱하여 딕셔너리로 변환
    # data = json.loads(response_text)
    article_list = get_all_data(trad_tag_cd,rlet_tag_cd,minPrice,maxPrice,minPyeong,maxPyeong)
    total_articles = len(article_list)
    progress_interval = 10
    print("Data load complete! Total count:", total_articles )

    if total_articles == 0:
        print("프로그램을 종료합니다. 데이터가 없습니다.")
        exit()


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
            "실제주소": get_real_address(article.get("lat","0"), article.get("lng","0")),
            "지역번호": article.get("cortarNo", ""),
            "매물상태코드": article.get("atclStatCd", ""),
            "거래유형코드": article.get("rletTpCd", ""),
            "상위거래유형코드": article.get("uprRletTpCd", ""),
            "거래유형명": article.get("rletTpNm", ""),
            "거래유형상세코드": article.get("tradTpCd", ""),
            "거래유형상세명": article.get("tradTpNm", ""),
            "확인유형코드": article.get("vrfcTpCd", ""),
            "방향정보": article.get("direction", ""),
            "대표이미지URL": article.get("repImgUrl", ""),
            "대표이미지유형코드": article.get("repImgTpCd", ""),
            "대표이미지썸네일": article.get("repImgThumb", ""),
            "위도": article.get("lat", ""),
            "경도": article.get("lng", ""),
            "건물명": article.get("bildNm", ""),
            "분": article.get("minute", ""),
            "동일주소매물수": article.get("sameAddrCnt", ""),
            "동일주소직접매물수": article.get("sameAddrDirectCnt", ""),
            "동일주소해시": article.get("sameAddrHash", ""),
            "동일주소최고가격": article.get("sameAddrMaxPrc", ""),
            "업소ID": article.get("cpid", ""),
            "업소명": article.get("cpNm", ""),
            "업소매물수": article.get("cpCnt", ""),
            "공인중개사사무소명": article.get("rltrNm", ""),
            "직거래여부": article.get("directTradYn", ""),
            "최소중개보수": article.get("minMviFee", ""),
            "최대중개보수": article.get("maxMviFee", ""),
            "연립다세대방수": article.get("etRoomCnt", ""),
            "거래가격한글표기": article.get("tradePriceHan", ""),
            "거래임대가격": article.get("tradeRentPrice", ""),
            "거래직접확인여부": article.get("tradeCheckedByOwner", ""),
            "상세주소여부": article.get("dtlAddrYn", ""),
            "상세주소": article.get("dtlAddr", "")
            
        }
        parsed_data.append(parsed_article)      

        cnt=cnt+1
        progress = (cnt / total_articles) * 100

        # Update progress at 10% intervals
        if progress >= progress_interval:
            print(f"{progress_interval}% 진행 중")
            progress_interval += 10            

    # 엑셀로 저장
    save_to_excel(parsed_data,input_area)

