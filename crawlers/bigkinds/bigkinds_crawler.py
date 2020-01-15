import requests
import json
from bs4 import BeautifulSoup
import re
import csv

def get_list(keyword,page) :

    startNo = (page-1)*100+1
    request_url = 'https://www.bigkinds.or.kr/news/newsResult.do'
    raw_data = """pageInfo:main
    login_chk:null
    LOGIN_SN:null
    LOGIN_NAME:null
    indexName:news
    keyword:%s
    byLine:
    searchScope:1
    searchFtr:1
    startDate:1991-01-01
    endDate:2019-10-13
    sortMethod:date
    contentLength:100
    providerCode:
    categoryCode:
    incidentCode:
    dateCode:
    highlighting:true
    sessionUSID:
    sessionUUID:test
    listMode:
    categoryTab:
    newsId:
    delnewsId:
    delquotationtxt:
    filterProviderCode:
    filterCategoryCode:
    filterIncidentCode:
    filterDateCode:
    filterAnalysisCode:
    startNo:%d
    resultNumber:100
    topmenuoff:
    resultState:
    keywordJson:
    keywordFilterJson:
    realKeyword:
    totalCount:
    interval:
    quotationKeyword1:
    quotationKeyword2:
    quotationKeyword3:
    searchFromUseYN:N
    mainTodayPersonYn:
    period:"""%(keyword, startNo)
    #print(raw_data)
    split_data = raw_data.splitlines()
    dict_data = {}
    for data in split_data:
        key, value = data.strip().split(':', 1)
        if value == 'null':
            value = None
        dict_data[key] = value
    #print(dict_data)
    response = requests.post(request_url, data=dict_data)
    html = response.text
    #print(html)
    soup = BeautifulSoup(html, 'html.parser')
    ##file = open('news.json', 'a', encoding='utf-8')
    #print(soup.get_text())
    lst = soup.select('#resultNews li.useImg')
    totalCount = int(soup.select('#totalCount')[0].get('value'))
    print(keyword, totalCount)
    return lst, totalCount

def save_content(id, filename) :

    #    doc_id = data.get('id').replace('news_', '')
    #    doc_publisher = data.get(
    doc_url = 'https://www.bigkinds.or.kr/news/detailView.do?docId={}&returnCnt=1&sectionDiv=1000'.format(id)
    data_json = json.loads(requests.get(doc_url).text)
    #print(data_json)
    content = data_json['detail']['CONTENT']
    print(id, content)
    with open(filename, "w", encoding="utf-8") as file :
        file.write(content)

def crawl(keyword,page_init=1) :
    page = page_init
    totalPage = page
    csv_file = open('meta_bigkinds.csv',"a", newline='', encoding="UTF-8")
    csv_writer = csv.writer(csv_file)
    while page <= totalPage :
        lst,totalCount = get_list(keyword, page)
        totalPage = totalCount//100 + 1
        print(len(lst))
        if(len(lst)==0) : break
        for data in lst:
            id = data.select("div.chkbox input")[0].get("value")
            link = data.select("div.resTxt li.list_provider")[0].get("link_page")
            filename = "bigkinds_"+id
            title = data.select("div.resTit h3")[0].text
            date = id.split(".")[1][:8]
            summary = data.select("div.resTit p")[0].text
            summary = re.sub("%s+"," ",summary).strip()
            publisher = data.select("div.resTxt li.list_provider span")[0].text
            meta_content = [id, link, filename, title, date, summary]
            #print(id, link, filename, title, summary, publisher)
            #print(meta_content)
            csv_writer.writerow(meta_content)
            save_content(id, "bigkinds/"+filename+".txt")

        print(page,"/", totalPage, "done")
        page+=1

#csv_file = open('meta_bigkinds.csv',"w", newline='', encoding="UTF-8")
#csv_writer = csv.writer(csv_file)
#csv_writer.writerow(["ID","Link","Filename","Title","Date","Summary"])

with open("../keywords.csv","r") as o:
    keyword_list= o.readlines()

keyword_list = keyword_list[1:]
for k in keyword_list :
    keyword = k.strip()
    try : crawl(keyword)
    except Exception as ex :
        print(ex)
        print(keyword)
