"""
查詢雙語詞彙庫 http://www.fcu.edu.tw/wSite/lp?ctNode=16185&mp=1
請幫我查XX的英文
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def get_keyword_vocabulary(keyword=None):

    """
    找尋頁數
    """
    url = 'http://www.fcu.edu.tw/wSite/lp?ctNode=16185&mp=1'

    r = requests.get(url)
    soup = BeautifulSoup(r.text,"html.parser")

    pagesize = soup.find("section",{'class':'page'}).find('span').find('em').text
    print(pagesize)

    url = 'http://www.fcu.edu.tw/wSite/lp?ctNode=16185&mp=1&idPath=&nowPage=1&pagesize=' + pagesize

    r = requests.get(url)
    soup = BeautifulSoup(r.text,"html.parser")

    table = soup.find("table",{'class':'tb'})

    row_title = [] #欄位標題
    serial_number = [] #序號
    main_category = [] #主類別
    sub_category = [] #次類別
    chinese = [] #中文
    english = [] #英文

    # 抓取表格標題欄位
    for title in table.find("tr").find_all("th"):
        row_title.append(title.text.strip())

    # 抓取表格其他欄位
    for row in table.find_all("tr")[1:]:
        fields =  row.find_all("td")
        serial_number.append(fields[0].text.strip())
        main_category.append(fields[1].text.strip())
        sub_category.append(fields[2].text.strip())
        chinese.append(fields[3].text.strip())
        english.append(fields[4].text.strip())

    """
    print(row_title)
    print(serial_number)
    print(main_category)
    print(sub_category)
    print(chinese)
    print(english)
    """

    vocabulary_df = pd.DataFrame({row_title[0]:serial_number,row_title[1]:main_category,row_title[2]:sub_category,row_title[3]:chinese,row_title[4]:english})

    """
    print(vocabulary_df)
    """

    msg = ""

    if keyword != None:
        vocabulary_df = vocabulary_df[vocabulary_df["中文"].str.lower().str.contains(keyword.lower())]

    for index, row in vocabulary_df.iterrows():
        msg += "「" + row["中文"] + '」 的英文是 「' + row["英文"] + '」\n'

    if msg == "":
        msg = "查無 「" + keyword + "」 的英文"

    return msg


if __name__ == '__main__':
    print(get_keyword_vocabulary(" "))
