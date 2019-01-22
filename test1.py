import requests
from lxml import etree
import queue
import threading
import json

class ThreadCrawl(threading.Thread):
    def __init__(self,crawl,pageQueue):
        super(ThreadCrawl,self).__init__()
        self.crawl = crawl
        self.pageQueue = pageQueue
        self.headers = {
                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
                       'Accept-Language': 'zh-CN,zh;q=0.8'}
    def run(self):
        print("%s正在处理数据..."%self.crawl)
        while not CRAWLEXIT:
            
            page = self.pageQueue.get(False)
            self.link_spider(page) 
            
                
           

    def link_spider(self,page):
        url = 'http://mil.news.sina.com.cn/roll/index.d.html?cid=57918&page='+str(page)
        response = requests.get(url,headers=self.headers)       
        #response.encoding = 'utf-8' 
        html = etree.HTML(response.text)    
        links = html.xpath('//ul[@class="linkNews"]/li/a/@href')    
        print(len(links))
        for link in links:
            
            dataQueue.put(link)
        #print(dataQueue)


class ParserSpider(threading.Thread):
    def __init__(self,parser,dataQueue,output,lock,total):
        super(ParserSpider,self).__init__()
        self.parser = parser
        self.dataQueue = dataQueue
        self.output = output
        self.lock = lock
        self.total = total
        #print (self.dataQueue.get())
        self.headers = {
                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
                       'Accept-Language': 'zh-CN,zh;q=0.8'}
    def run(self):
        print('%s正在解析数据...'%self.parser)
        while not PARSEREXIT:
            
            url = self.dataQueue.get(False)
            self.parser_spider(url)
            
            #print("dataQueue kong")

    def parser_spider(self,url):
        global total,number 
          
            #print (url)
        response = requests.get(url,headers=self.headers)
        #print(url)
        response.encoding = 'utf-8' 
        html = etree.HTML(response.text)
            
        title = html.xpath('//h1[@class="main-title"]')[0].text
        date = html.xpath('//span[@class="date"]')[0].text
        try:
            source = html.xpath('//div[@class="date-source"]/a')[0].text
        except:
            try:
                source=html.xpath('//div[@class="date-source"]/span')[1].text
            except:
                source =""

        content = html.xpath('//div[@class="article"]/p/text()')
                #print("------4444-----")
        #for i in contentlist:
            #content = i.text
        #print("____")               
        
        try:
            imagelist =[]
            images= html.xpath('//div[@class="img_wrapper"]/img/@src')
            for i in images:
                image = "https:"+i
                imagelist.append(image)
                #print (image)
        except:
            image =''
        
        number += 1
        result={'num':number,
                'title':title,
                'date':date,
                'source':source,
                'content':content,
                'image':imagelist
                      }
       #print(result)
       

        with self.lock:
            self.output.write(json.dumps(result,ensure_ascii=False)+"\n")
            
            total += 1         
            #print("写入文件中>>>")
        
            
            
        
            #print ("dataQueue")          
        
        #with self.lock:
            #total += 1

dataQueue = queue.Queue()
CRAWLEXIT = False
PARSEREXIT = False
lock = threading.Lock()
total = 0
number = 0
def main():
    output = open("jsnews.json","a",encoding='utf-8')
    num = int(input("请输入要获取的总页数:"))
    pageQueue = queue.Queue()
    for page in range(1,num+1):
        pageQueue.put(page)

    crawlthread =[]
    crawllist =["crawl-1","crawl-2","craw-3"  ]
    for crawl in crawllist:
        thread = ThreadCrawl(crawl,pageQueue)
        thread.start()
        crawlthread.append(thread)

    while not pageQueue.empty():
        pass
    global CRAWLEXIT    
    CRAWLEXIT = True

    for t in crawlthread:
        t.join()

    parserthread =[]
    parserlist = ["parser-1","parser-2","parser-3"]
    for parser in parserlist:
        thread = ParserSpider(parser,dataQueue,output,lock,total)
        thread.start()
        parserthread.append(thread)

    while not dataQueue.empty():
        pass    
    global PARSEREXIT
    PARSEREXIT = True
       
    for t in parserthread:
        t.join()

    with lock:
        output.close()
    print (total)

if __name__ == '__main__':
    main()
