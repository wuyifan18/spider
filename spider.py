#!/usr/bin/env python
# coding=utf-8
import argparse
import requests
import execjs
import json
import multiprocessing
import time
import re
import datetime
from utils.docid import getkey, decode_docid
import os
import random


class SpiderManager(object):

    def __init__(self):

        self.url = "http://wenshu.court.gov.cn/List/List?sorttype=1{}"
        self.detailurl = "http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={}"
        self.conditions = []
        self.url_for_content = "http://wenshu.court.gov.cn/List/ListContent"
        self.proxies = []
        self.headers_getvjkl5 = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Cookie": "",
            "DNT": "1",
            "Host": "wenshu.court.gov.cn",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
        }
        self.headers_getdata = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Cookie": "",
            "DNT": "1",
            "Host": "wenshu.court.gov.cn",
            "Origin": "http://wenshu.court.gov.cn",
            "Referer": "http://wenshu.court.gov.cn/list/list/?sorttype=1&conditions=searchWord+5+AJLX++%E6%A1%88%E4%BB%B6%E7%B1%BB%E5%9E%8B:%E6%89%A7%E8%A1%8C%E6%A1%88%E4%BB%B6&conditions=searchWord++CPRQ++%E8%A3%81%E5%88%A4%E6%97%A5%E6%9C%9F:2016-01-04%20TO%202016-01-04&conditions=searchWord+%E5%8C%97%E4%BA%AC%E5%B8%82+++%E6%B3%95%E9%99%A2%E5%9C%B0%E5%9F%9F:%E5%8C%97%E4%BA%AC%E5%B8%82",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
        }
        self.headers_getdetail = {
            "Accept": "text/javascript, application/javascript, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Cookie": "",
            "DNT": "1",
            "Host": "wenshu.court.gov.cn",
            "Referer": "http://wenshu.court.gov.cn/content/content?DocID=e282e679-92f9-49ce-afae-c401fbafedec&KeyWord=",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
        }
        self.data = {
            "Param": "案件类型:执行案件,",
            "Index": "1",
            "Page": "10",
            "Order": "法院层级",
            "Direction": "asc",
            "vl5x": "",
            "number": "wens",
            "guid": ""
        }

    def setconditions(self, conditions):
        self.conditions = conditions

    def setdatacookies(self, cookies):
        self.headers_getdata["Cookie"] = cookies

    def setdetailcookies(self, cookies):
        self.headers_getdetail["Cookie"] = cookies

    @staticmethod
    def getguid():
        with open('utils/getGuid.js') as fp:
            js = fp.read()
            ctx = execjs.compile(js)
            return ctx.call('getGuid')

    def getvjkl5(self):
        request_url = self.url.format(self.conditions)
        while True:
            try:
                response = requests.post(request_url, headers=self.headers_getvjkl5, timeout=(3.05, 27), proxies={'http': self.proxies})
                response.close()
                break
            except (requests.exceptions.ChunkedEncodingError, requests.exceptions.InvalidURL, requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout)as e:
                print('id: {}, getvjk15: {}'.format(os.getpid(), e))
                self.proxies = getIP()
        return response.cookies["vjkl5"], response.cookies["wzws_cid"]

    @staticmethod
    def getvl5x(vjkl5):
        with open('utils/getVl5x.js') as fp:
            js = fp.read()
            ctx = execjs.compile(js)
            return ctx.call('getVl5x', vjkl5)

    def getData(self, page, date, area, court):
        if court == '中级法院:':
            self.data['Param'] = self.data['Param'] + date + ',' + area
        else:
            self.data['Param'] = self.data['Param'] + date + ',' + area + ',' + court
        self.data["Index"] = page
        q = 0
        while True:
            try:
                vjkl5, wzws_cid = self.getvjkl5()
                self.data["vl5x"] = self.getvl5x(vjkl5)
                self.data["guid"] = self.getguid()
                self.setdatacookies("wzws_cid={}; vjkl5={}".format(wzws_cid, vjkl5))
                self.setdetailcookies("wzws_cid={}; vjkl5={}".format(wzws_cid, vjkl5))
                rsp = requests.post(self.url_for_content, headers=self.headers_getdata, data=self.data, timeout=(3.05, 27), proxies={'http': self.proxies})
                rsp.close()
                if rsp.text[-3] == ',' and q == 1:
                    q = 0
                    return 'null', 'null'
                if rsp.text[-3] == ',':
                    q = q + 1
                    continue
                infodata = json.loads(json.loads(rsp.text))
                htmldata = self.getDetails(infodata)
                break
            except (KeyError, requests.exceptions.ChunkedEncodingError, requests.exceptions.InvalidURL, requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout)as e:
                print('id: {}, getData: {}'.format(os.getpid(), e))
                self.proxies = getIP()
            except (ValueError, execjs._exceptions.ProcessExitedWithNonZeroStatus, UnicodeDecodeError, IndexError) as e:
                print('id: {}, getKey: {}'.format(os.getpid(), e))
                self.proxies = getIP()
        return infodata, htmldata

    def getDetails(self, infodata):
        htmldata = []
        format_key_str = infodata[0]['RunEval']
        key = getkey(format_key_str).encode('utf-8')
        for x in infodata[1:]:
            iid = x['文书ID']
            docid = decode_docid(iid, key)
            if docid == '':
                continue
            request_url = self.detailurl.format(docid)
            while True:
                try:
                    response = requests.post(request_url, headers=self.headers_getdetail, timeout=(3.05, 27), proxies={'http': self.proxies})
                    response.close()
                    jsonHtmlData = re.findall('var jsonHtmlData = "({.*?}";)', response.text)
                    jsonHtmlData = json.loads(jsonHtmlData[0][:-2].replace('\\', ''), strict=False)['Html']
                    htmldata.append(jsonHtmlData)
                    break
                except (requests.exceptions.ChunkedEncodingError, requests.exceptions.InvalidURL, requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout)as e:
                    print('id: {}, getDetails: {}'.format(os.getpid(), e))
                    self.proxies = getIP()
                except IndexError:
                    print('id: {}, 验证码: {}'.format(os.getpid(), response.text))
                    self.proxies = getIP()
        return htmldata

    @staticmethod
    def save(infodata, htmldata, area, date):
        with open('data/' + date + '.txt', 'a+', encoding='utf-8') as fp:
            for item, html in zip(infodata, htmldata):
                row = '\t'.join(
                    (item.get('裁判日期', ""), area, item.get('案件名称', ""), item.get('法院名称', ""), item.get('案号', ""), html))
                fp.write(row + '\n')


def getIP():
    # while True:
    #     try:
    #         time.sleep(random.randint(2, 3))
    #         response = requests.get('http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=45&mr=1&regions=')
    #         ip = response.text.strip()
    #         return ip
    #     except (requests.exceptions.ChunkedEncodingError, requests.exceptions.InvalidURL, requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout)as e:
    #         print('id: {}, getIP: {}'.format(os.getpid(), e))
    return ''


def f(para):
    page, date, area, proxies, court = para.split(',')
    spider = SpiderManager()
    if court == '':
        spider.setconditions('&conditions=searchWord+5+AJLX++案件类型:执行案件&conditions=searchWord++CPRQ++{0}&conditions=searchWord+{1}+++法院地域:{1}'.format(date, area))
    else:
        spider.setconditions('&conditions=searchWord+5+AJLX++案件类型:执行案件&conditions=searchWord++CPRQ++{0}&conditions=searchWord+{1}+++法院地域:{1}&conditions=searchWord+{2}+++中级法院:{2}'.format(date, area, court))
    spider.proxies = proxies
    infodata, htmldata = spider.getData(page=page, date=date, area='法院地域:' + area, court='中级法院:' + court)
    if infodata == 'null':
        return 0, spider.proxies
    if court == '' and int(infodata[0]['Count']) > 200:
        spider.data['parval'] = area
        while True:
            try:
                rsp = requests.post('http://wenshu.court.gov.cn/List/CourtTreeContent', headers=spider.headers_getdata, data=spider.data, timeout=(3.05, 27), proxies={'http': spider.proxies})
                rsp.close()
                courtlist = [i['Key'] for i in json.loads(json.loads(rsp.text))[0]['Child'] if i['Key'] != '']
                break
            except (json.decoder.JSONDecodeError, requests.exceptions.ChunkedEncodingError, requests.exceptions.InvalidURL, requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout,
                    requests.exceptions.ReadTimeout) as e:
                print('id: {}, getCourt: {}'.format(os.getpid(), e))
                spider.proxies = getIP()
        return courtlist, spider.proxies
    if infodata != 'null':
        spider.save(infodata[1:], htmldata, area, date.split()[-1])
        return int(infodata[0]['Count']), spider.proxies


def getCount(page, date, area, ip, court):
    page_start = time.time()
    count, _ = f(page + ',' + date + ',' + area + ',' + ip + ',' + court)
    page_end = time.time()
    if isinstance(count, list):
        return 'null', count
    total = count
    count = min(count, 200)
    page_count = count // 10 if count % 10 == 0 and count >= 10 else count // 10 + 1
    if court == '':
        print('id: {}, date: {}, area: {}, total_count: {}, done: {}/{}, using time: {:.2f}'.format(os.getpid(), date.split()[-1], area, total, 1, page_count, page_end - page_start))
    else:
        print('id: {}, date: {}, area: {}, court: {}, total_count: {}, done: {}/{}, using time: {:.2f}'.format(os.getpid(), date.split()[-1], area, court, total, 1, page_count, page_end - page_start))
    return page_count, total


def fun(date):
    area = ['北京市', '天津市', '上海市', '重庆市', '河北省', '山西省', '辽宁省', '吉林省', '黑龙江省', '江苏省', '浙江省', '安徽省', '福建省', '江西省',
            '山东省', '河南省', '湖北省', '湖南省', '广东省', '海南省', '四川省', '贵州省', '云南省', '陕西省', '甘肃省', '青海省',
            '内蒙古自治区', '广西壮族自治区', '西藏自治区', '宁夏回族自治区', '新疆维吾尔自治区', '新疆维吾尔自治区高级人民法院生产建设兵团分院']
    # while True:
    #     try:
    #         response = requests.get('http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=45&mr=1&regions=')
    #         ip = response.text.strip()
    #         if ip.find('"code":111,"success":false') == -1:
    #             break
    #         time.sleep(random.randint(2, 3))
    #     except Exception as e:
    #         print('id: {}, getIP: {}'.format(os.getpid(), e))
    ip = ''
    for a in area:
        page_count, count = getCount('1', date, a, ip, '')
        if isinstance(count, list):
            for court in count:
                page_count, total = getCount('1', date, a, ip, court)
                for page in range(2, page_count + 1):
                    page_start = time.time()
                    _, proxies = f(str(page) + ',' + date + ',' + a + ',' + ip + ',' + court)
                    page_end = time.time()
                    ip = proxies
                    print('id: {}, date: {}, area: {}, court: {}, total_count: {}, done: {}/{}, using time: {:.2f}'.format(os.getpid(), date.split()[-1], a, court, total, page, page_count, page_end - page_start))
        else:
            for page in range(2, page_count + 1):
                page_start = time.time()
                _, proxies = f(str(page) + ',' + date + ',' + a + ',' + ip + ',' + '')
                page_end = time.time()
                ip = proxies
                print('id: {}, date: {}, area: {}, total_count: {}, done: {}/{}, using time: {:.2f}'.format(os.getpid(), date.split()[-1], a, count, page, page_count, page_end - page_start))
    return date


if __name__ == '__main__':
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('-num_processes', default=1, type=int)
    parser.add_argument('-start_time', default='2016-1-2')
    parser.add_argument('-end_time', default='2016-1-2')
    args = parser.parse_args()
    enabled_proxy = args.start_time
    pool = multiprocessing.Pool(processes=args.num_processes)
    begin = datetime.datetime.strptime(args.start_time, "%Y-%m-%d")
    end = datetime.datetime.strptime(args.end_time, "%Y-%m-%d")
    t = []
    while begin <= end:
        t.append("裁判日期:{} TO {}".format(begin.strftime("%Y-%m-%d"), begin.strftime("%Y-%m-%d")))
        begin += datetime.timedelta(days=1)
    for d in pool.imap(fun, iter(t)):
        print('id: {}, date: {} finished.'.format(os.getpid(), d.split()[-1]))
    pool.close()
    pool.join()
    end = time.time()
    print('id: {}, using time: {:.2f}'.format(os.getpid(), end - start))
