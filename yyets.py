import requests,re,pymysql,sys
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import unquote

chrome_options = Options()
chrome_options.add_argument('--headless')
# SERVICE_ARGS=['--load-images=false','--disk-cache=true']

EMAIL='meiyujack@msn.cn'
PASSWORD='013301227'
WEBSITE='http://www.zimuzu.io'

class YYETS:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0(Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          'Chrome/57.0.2987.133 Safari/537.36'
        }
        self.searchURL=WEBSITE+'/search/index?keyword='
        self.universalURL=WEBSITE+'/resource/'
        self.id=''
        self.name=''
        self.originalName=''
        self.ch_browser=webdriver.Chrome(chrome_options=chrome_options)

    def getPage(self,url,encoding='utf-8'):
        try:
            response = requests.get(url=url, headers=self.headers)
            # print(response.encoding,response.apparent_encoding)
            if response.status_code==200:
                response.encoding=encoding
                html=etree.HTML(response.text)
                return html
        except:
            print('超时，没有获取到下载页面')

    def getMovieBasic(self,keyword=None,currentName=None):
        while True:
            if not keyword:
                keyword = input('请输入你要查询的电影(e退出)：')
                if keyword=='e':
                    sys.exit()
                else:
                    keyword=keyword
            html=self.getPage(self.searchURL+keyword)
            listType=html.xpath('//em/text()')
            listName=html.xpath('//strong[@class="list_title"]/text()')
            listURL=html.xpath('//div[@class="fl-img"]/a/@href')
            q=len(listURL)
            listType=listType[:q]
            listName=listName[:q]
            for t in listType[:]:
                if t=='电视剧':
                    n=listType.index(t)
                    listName.pop(n)
                    listURL.pop(n)
                    listType.pop(n)
            if currentName:
                for c in currentName:
                    for l in listName[:]:
                        if c in l:
                            i=listName.index(l)
                            listName.pop(i)
                            listURL.pop(i)
            if len(listName)==0:
                print('没有结果，请重输！')
                keyword=False
                currentName=None
                continue
            else:
                while True:
                    b=False
                    for l in listName:#模糊查找
                        # if keyword in l:
                        i = listName.index(l)
                        self.id=listURL[i][10:]
                        self.name=re.match('^《(.*)》',l).group(1)
                        self.originalName=re.match('.*?\((.*)\)',l).group(1)
                        # result=re.match('^《'+self.keyword+'((：.*?)|》).*',l)
                        # if result:#精确指定
                        #     return listURL[listName.index(l)]
                        n=i+1
                        if n==len(listName):
                            tip='这是最后一部：'
                            bool=True
                        elif i==0:
                            tip='共有{0}部搜索结果：'.format(len(listName))
                        else:
                            tip='还有…'
                        key=input('请确认是这部电影(y确定,n继续查找,c重选,b返回上级菜单)'+l+tip)
                        if key=='y':
                            return self.id,self.name,self.originalName
                        if key=='n':
                            continue
                        if key == 'c':
                            break
                        if key=='b':
                            b=True
                            break
                    if b==True:
                        keyword=False
                        break
            currentName=None

    def dealDetail(self,listDetails,e,r=''):
        movieDetails=re.sub(e,r,self.getStr(listDetails))
        return movieDetails

    def getStr(self,l,s=''):
        return s.join(l).rstrip()

    def getMovieInfo(self):
        movieURL=self.universalURL+self.id
        details=self.getPage(movieURL)
        listText = details.xpath('//div[@class="fl-info"]/ul//strong/text()')
        # ID=url[10:]
        # title=self.getStr(details.xpath('//div[@class="resource-tit"]//h2/text()')[0])
        # name=re.match('.*?《(.*)》',title,re.S).group(1)
        imageURL=self.getStr(details.xpath('//div[@class="imglink"]/a/@href'))
        region=listText[1]
        lang=listText[2]
        premiere=listText[3][:-3]
        production=self.getStr(details.xpath('//div[@class="fl-info"]//li[5]/strong/text()'))#制作公司
        type=self.getStr(details.xpath('//div[@class="fl-info"]//li[6]/strong/text()'))#类型
        IMDB=self.getStr(details.xpath('//div[@class="fl-info"]//li[8]/text()'))
        v=re.match('^\s+(\d.\d)',IMDB)
        if IMDB is not '':
            if v:
                score=self.getStr(v.groups(1))# 得分
            else:
                print('正在获取IMDB得分')
                IMDB=self.getStr(details.xpath('//div[@class="fl-info"]//li[8]/a/@href'))
                h=self.getPage(IMDB)
                score=self.getStr(h.xpath('//div[@class="ratingValue"]/strong/span/text()'))
        else:
            print('正在获取IMDB得分，请稍候')
            base='https://www.imdb.com/find?ref_=nv_sr_fn&q='+self.originalName
            website='https://www.imdb.com'
            h=self.getPage(base)
            ch=self.getStr(h.xpath('//table[@class="findList"]//tr[1]//td[2]/a/@href'))
            url=website+ch
            h=self.getPage(url)
            score = self.getStr(h.xpath('//div[@class="ratingValue"]/strong/span/text()'))
        otherName=self.dealDetail(details.xpath('//div[@class="fl-info"]/ul//li[@class="mg"]/text()'),' / ','/')#别名
        screenwriter=self.getStr(details.xpath('//div[@class="fl-info"]//li[10]/a/text()'))
        director=self.getStr(details.xpath('//div[@class="fl-info"]//li[11]/a/text()'))
        starringrole=self.getStr(details.xpath('//div[@class="fl-info"]/ul//li[@class="rel"]/a/text()'),'/')#主演
        content=self.dealDetail(details.xpath('//div[@class="con"]/text()'),' |\\u3000\\u3000|\\r\\n|©豆瓣')#内容梗概
        movieInfoData={
            'movieID':self.id,
            'name':self.name,#0
            'image':imageURL,
            'originalName':self.originalName,#1
            'region':region,#2
            'lang':lang,#3
            'premiere':premiere,#4
            'production':production,
            'type':type,#5
            'IMDB':score,#6
            'otherName':otherName,
            'screenwriter':screenwriter,
            'director':director,#7
            'starringrole':starringrole,#8
            'content':content#9
        }
        t = ['名称', '原名', '地区', '语言', '首播', '类型', 'IMDB', '导演', '主演', '内容介绍']
        v=[self.name,self.originalName,region,lang,premiere,type,score,director,starringrole,content]
        for i in range(10):
            print(t[i]+'：'+v[i])
        return movieInfoData

    def connMySQL(self):
        db = pymysql.connect(host='localhost', user='root', password='12345', port=3306, db='yyets')
        return db

    def insertTable(self,data,table='movieinfo'):
        data=data
        table=table
        keys=','.join(data.keys())
        values=','.join(['%s']*len(data))
        sql='insert into {table}({keys}) values ({values}) on duplicate key update '.format(table=table,keys=keys,values=values)
        update=','.join(["{key}=%s".format(key=key) for key in data])
        sql+=update
        db=self.connMySQL()
        cursor=db.cursor()
        # try:
        if cursor.execute(sql,tuple(data.values())*2):
            if table=='movieinfo':
                print('插入电影《{0}》信息成功！'.format(self.name))
            if table=='getmovie':
                print('插入电影《{0}》下载地址成功！'.format(self.name))
            db.commit()
        # except:
        #     if table=='movieinfo':
        #         print('插入电影《{0}》信息失败'.format(self.name))
        #     if table == 'getmovie':
        #         print('插入电影《{0}》下载地址失败！'.format(self.name))
        #     db.rollback()
        db.close()

    def getKeyURL(self,url):
        print('请等待……')
        movieURL=self.universalURL+url
        chrome=webdriver.Chrome(chrome_options=chrome_options)
        chrome.get(movieURL)
        self.ch_browser.get(movieURL)
        wait=WebDriverWait(self.ch_browser,12)
        loginButton=wait.until(EC.element_to_be_clickable((By.XPATH,'//div[@class="u"]/a')))
        loginButton.click()
        email=wait.until(EC.presence_of_element_located((By.NAME,'email')))
        password=self.ch_browser.find_element_by_name('password')
        email.send_keys(EMAIL)
        password.send_keys(PASSWORD)
        loginButton=self.ch_browser.find_element_by_id('login')
        loginButton.click()
        try:
            a=wait.until(EC.element_to_be_clickable((By.XPATH,'//div[@class="resource-box"]//a')))
            KeyURL = a.get_attribute('href')
            return KeyURL
        except TimeoutException:
            print('超时，没有找到下载链接')

    def getDownloadURL(self,keyURL):
        resources=self.getPage(keyURL)
        names=resources.xpath('//div[@id="tab-g1-HR-HDTV"]//li//span[@class="filename"]/text()')
        ed2ks=resources.xpath('//div[@id="tab-g1-HR-HDTV"]//li/ul[@class="down-links"]//li[2]/a/@href')
        if names==[]:
            names=resources.xpath('//div[@id="tab-g1-MP4"]//li//span[@class="filename"]/text()')
            ed2ks=resources.xpath('//div[@id="tab-g1-MP4"]//li/ul[@class="down-links"]//li[2]/a/@href')
        if len(names)>1:
            while True:
                for name in names:
                    c=names.index(name)+1
                    n=len(names)-c
                    tip = '，还有{0}个'.format(n)
                    if n==0:
                        tip=''
                    key=input('请确认是此链接(y确定，n继续查找)，{0}{1}：'.format(unquote(name),tip))
                    if key=='y':
                        return  unquote(ed2ks[names.index(name)])
                    if key=='n':
                        continue
        else:
            return unquote(self.getStr(ed2ks))

    def selectTable(self,table,key,arg):
        sql = 'select * from {table} where {key} like %s'.format(table=table,key=key)
        db = self.connMySQL()
        cursor = db.cursor()
        cursor.execute(sql,arg)
        return cursor

    # def api(self):
    #     while True:
    #         self.getMovieBasic(keyword=False)
    #         self.getMovieInfo()
    #         keyURL = self.getKeyURL(self.id)
    #         ed2kURL = self.getDownloadURL(keyURL)
    #         # return ed2kURL
    #         print('《{0}》的下载地址为\n{1}'.format(self.name,ed2kURL))


