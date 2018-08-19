from douban.config import *
from douban.mysql import MySQL
import requests
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import pymysql
import re
import time
import os
from selenium.common.exceptions import StaleElementReferenceException,WebDriverException,NoSuchElementException

browser=webdriver.Chrome()
wait=WebDriverWait(browser,10)
movie_num1=1
comment_num=1
movie_num=1

class Spider():
    base_url = 'https://movie.douban.com/tag/#/?sort=T&range=0,10&tags=%E7%94%B5%E8%A7%86%E5%89%A7'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': 'bid=Uq1d2FGdftc; ap_v=1,6.0; ll="118174"; _vwo_uuid_v2=D1E01FF3C6AA7D4A9D2E4CB491A568181|fa3dd148622a12894ff3ed2f1bd9ca01; ps=y; dbcl2="138899670:Uqn4yLXdaUc"; ck=EkTz; frodotk="a5ebdb43a31763b5f1c391cae9462b1f"; push_noty_num=0; push_doumail_num=0',
        'Host': 'movie.douban.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    }
    mysql = MySQL()

    def start(self,start_url):
        """
        初始化工作
        """
        rating={'&#x5F88;&#x5DEE;':1,'&#x8F83;&#x5DEE;':2,'&#x8FD8;&#x884C;':3,'&#x63A8;&#x8350;':4,'&#x529B;&#x8350;':5}
        # 全局更新Headers
        start_url = start_url
        # 调度第一个请求

        print('Start', start_url)
        browser.get(start_url)
        while(1):
            try:
                more = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.more')))
                time.sleep(3)
                more.click()
                global movie_num1
                movie_num1+=1
                print('现在%d部电影了'%(movie_num1*20))
            except StaleElementReferenceException as e:
                print('到底了，总共%d部电影'%(movie_num1*20))
                break
            except WebDriverException:
                continue
        html=browser.page_source
        doc=pq(html)
        items=doc('.list-wp .item').items()

        for item in items:
            time.sleep(1)
            next_url=item.attr('href')
            print('crawl', next_url)
            browser.get(next_url)
            html1 = browser.page_source
            doc1 = pq(html1)
            items1=doc1(".attrs").items()
            attrs={}
            number=0
            for x in items1:
                attrs[number]=x.text()
                number+=1
            types=re.findall('"v:genre">(.*?)<',html1,re.S)
            type=""
            for type0 in types:
                type=type+type0+'/'
            dates=re.findall('ReleaseDate".*?>(.*?)<',html1,re.S)
            date=""
            for date0 in dates:
                date=date+date0+'/'
            name = re.search('h1.*?"v:itemreviewed">(.*?)<', html1, re.S).group(1)
            bool_name = re.search('/', name, re.S)
            if bool_name:
                continue
            global movie_num
            movie_item={
                # 'director':re.search('rel="v:direcedBy">(.*?)<',html,re.S).group(1),
                'num':movie_num,
                'name':name,
                'director': attrs[0],
                'scriptwriter': attrs[1],
                'actor':attrs [2],
                'type':type,
                'area':re.search('地区:</span>(.*?)<',html1,re.S).group(1),
                'language':re.search('语言:</span>(.*?)<',html1,re.S).group(1),
                'date':date
            }
            if not self.mysql.repetition(movie_item):
                try:
                    html1 = doc1('#mainpic .nbgnbg').html()
                    picture_url = re.search('src="(.*?)"', html1, re.S).group(1)
                    if not os.path.exists('image'):
                        os.mkdir('image')
                    response = requests.get(picture_url)
                    if response.status_code == 200:
                        file_path = 'image/{0}.jpg'.format(movie_item['name'])
                        # file_path = '{0}/{1}.{2}'.format('image', md5(response.content).hexdigest(), 'jpg')
                        if not os.path.exists(file_path):
                            with open(file_path, 'wb') as f:
                                f.write(response.content)
                        else:
                            print('Already Download', file_path)
                except requests.ConnectionError:
                    print('Failed to Save Image')
                self.mysql.insert('movies',tuple(movie_item.values()))
                movie_num+=1
                comment_url = doc1('#comments-section .mod-hd .pl').html()
                comment_url1 = re.search('href="(.*?)"', comment_url, re.S).group(1)
                try:
                    page=0
                    while(1):
                        add_url = "&start={0}&limit=20&sort=new_score".format(page)
                        next_comment_url=comment_url1+add_url
                        browser.get(next_comment_url)
                        doc2=pq(browser.page_source)
                        browser.find_element_by_class_name('comment')
                        page += 20
                        comment_items = doc2('#content .grid-16-8 .article .mod-bd .comment-item .comment .comment-info').items()

                        global comment_num
                        comment_num_i = 1
                        time.sleep(0.1)
                        for comment_item in comment_items:
                            comment_html=comment_item.html()
                            find_rate=re.search('title="(.*?)"',comment_html, re.S).group(1)
                            if find_rate in rating.keys():
                                movie_rate = rating[find_rate]
                            else:
                                movie_rate=1
                            comment_for_db = {
                                'num': comment_num,
                                'user_name': re.search('>(.*?)</a>', comment_item.html(), re.S).group(1),
                                'movie_name': movie_item['name'],
                                'movie_rate': movie_rate,
                            }
                            self.mysql.insert('comments', tuple(comment_for_db.values()))
                            comment_num += 1
                            comment_num_i += 1
                            if comment_num_i >= 1000:
                                break
                        if comment_num_i >= 1000:
                            break

                except NoSuchElementException:
                    continue
            else:
                print("已经存在%s" % (movie_item['name']))


        browser.close()

    
    def error(self, douban_request):
        """
        错误处理
        :param weixin_request: 请求
        :return:
        """
        douban_request.fail_time = douban_request.fail_time + 1
        print('Request Failed', douban_request.fail_time, 'Times', douban_request.url)
        if douban_request.fail_time < MAX_FAILED_TIME:
            self.queue.add(douban_request)

    
    def run(self):
        """
        入口
        :return:
        """
        urls=['https://movie.douban.com/tag/#/?sort=T&range=0,10&tags=%E7%94%B5%E5%BD%B1','https://movie.douban.com/tag/#/?sort=T&range=0,10&tags=%E7%94%B5%E8%A7%86%E5%89%A7','https://movie.douban.com/tag/#/?sort=T&range=0,10&tags=%E7%BB%BC%E8%89%BA','https://movie.douban.com/tag/#/?sort=T&range=0,10&tags=%E5%8A%A8%E7%94%BB','https://movie.douban.com/tag/#/?sort=T&range=0,10&tags=%E7%BA%AA%E5%BD%95%E7%89%87']
        for url in urls:
            self.start(url)


if __name__ == '__main__':
    #先运行mysqlstorage创建数据库

    spider = Spider()
    spider.run()
