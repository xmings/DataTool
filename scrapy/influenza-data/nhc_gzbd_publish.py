import requests
from bs4 import BeautifulSoup
import datetime
import re
from selenium import webdriver
import time

def get_sh_data(url):
    '''获得上海卫健委的数据'''
    r = requests.get(url=url, headers=sh_headers)
    sh_dict = {}
    soup = BeautifulSoup(r.text, 'lxml')
    try:
        news = soup.find_all(name='span')
        for new in news:
            new_text = new.get_text()
            if len(new_text) >=10:
                # print(new_text)
                if new_text.startswith('截至'):
                    style1 = re.compile('.*?上海市已累计排除疑似病例(\d+)例.*?确诊病例(\d+)例')
                    sh_paichu = re.search(style1, new_text).group(1)
                    sh_quezhen = re.search(style1, new_text).group(2)
                    sh_dict['累计排除疑似'] = sh_paichu
                    sh_dict['累计确诊'] = sh_quezhen
                elif new_text.startswith('目前'):
                    style2 = re.compile('(\d+)例病情危重.*?(\d+)例重症.*?(\d+)例治愈.*?(\d+)例死亡.*?尚有(\d+)例疑似病例')
                    sh_dict['累计重症'] = int(re.search(style2, new_text).group(1)) + int(re.search(style2, new_text).group(2))
                    sh_dict['累计治愈'] = re.search(style2, new_text).group(3)
                    sh_dict['累计死亡'] = re.search(style2, new_text).group(4)
                    sh_dict['累计疑似'] = re.search(style2, new_text).group(5)
    except:
        print('上海数据未更新！')
    finally:
        # print(sh_dict)
        return sh_dict

def get_sh_today_news():
    '''获得上海卫健委的新闻'''
    url = r'http://wsjkw.sh.gov.cn/xwfb/index.html'
    r = requests.get(url=url, headers=sh_headers)
    soup = BeautifulSoup(r.text, 'lxml')
    # print(soup)
    today_format = datetime.datetime.today().strftime('%Y-%m-%d')
    try:
        today_sh_news = soup.find_all(name='span', text=today_format)
        today_counts = len(today_sh_news)
        for i in range(today_counts-1, -1, -1):
            title = today_sh_news[i].find_previous_sibling(name='a').attrs['title']  # 标题
            href = 'http://wsjkw.sh.gov.cn' + today_sh_news[i].find_previous_sibling(name='a').attrs['href'] #网址
            if title.startswith('上海新增'):
                # print(title)
                return get_sh_data(href)
    except:
        print('上海数据未更新1')
        return {}

def get_all_today_news():
    '''获得国家卫健委的新闻'''
    url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml'
    r = requests.get(url, headers=quanguo_headers)
    print(r.text)
    soup = BeautifulSoup(r.text, 'lxml')
    try:
        today_format = datetime.datetime.today().strftime('%Y-%m-%d')
        # latest_news_title = soup.find(name='span', text=today_format).find_previous_sibling(name='a').attrs['title']
        latest_news_href = 'http://www.nhc.gov.cn' + soup.find(name='span', text=today_format).find_previous_sibling(name='a').attrs['href']
        # print(latest_news_href)
        return get_all_today_data(latest_news_href)
    except:
        print('全国数据未更新1')
        return ({}, {})

def get_all_today_data(url):
    '''获得国家卫健委的数据'''
    r = requests.get(url, headers=quanguo_headers)
    all_dict = {}
    hubei_dict = {}
    soup = BeautifulSoup(r.text, 'lxml')
    try:
        news = soup.find(name='p').get_text()
        # print(news)
        style1 = re.compile('新增确诊病例(\d+)例.*?（湖北省(\d+)例.*?重症病例(\d+)例.*?湖北省(\d+)例.*?死亡病例(\d+)例.*?湖北省(\d+)例.*?治愈出院病例(\d+)例.*?湖北省(\d+)例.*?疑似病例(\d+)例.*?湖北省(\d+)例')
        style2 = re.compile('.*?累计报告确诊病例(\d+)例.*?现有重症病例(\d+)例.*?累计死亡病例(\d+)例.*?累计治愈出院病例(\d+)例.*?疑似病例(\d+)例')
        style3 = re.compile('.*?累计追踪到密切接触者(\d+)人.*?解除医学观察(\d+)人.*?共有(\d+)人正在接受医学观察')
        hubei_dict['新增确诊'] = re.search(style1, news).group(2)
        hubei_dict['新增重症'] = re.search(style1, news).group(4)
        hubei_dict['新增死亡'] = re.search(style1, news).group(6)
        hubei_dict['新增治愈'] = re.search(style1, news).group(8)
        hubei_dict['新增疑似'] = re.search(style1, news).group(10)
        all_dict['新增疑似'] = re.search(style1, news).group(9)
        all_dict['累计确诊'] = re.search(style2, news).group(1)
        all_dict['累计重症'] = re.search(style2, news).group(2)
        all_dict['累计死亡'] = re.search(style2, news).group(3)
        all_dict['累计治愈'] = re.search(style2, news).group(4)
        all_dict['累计疑似'] = re.search(style2, news).group(5)
        all_dict['累计密切接触者'] = re.search(style3, news).group(1)
        all_dict['累计医学观察者'] = re.search(style3, news).group(3)
        # print(all_dict, hubei_dict)
    except:
        print('全国数据未更新！')
    finally:
        return all_dict, hubei_dict

def get_cookie(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)
    cookies = driver.get_cookies()
    driver.quit()
    items = []
    for i in range(len(cookies)):
        cookie_value = cookies[i]
        item = cookie_value['name'] + '=' + cookie_value['value']
        items.append(item)
    cookiestr = '; '.join(a for a in items)
    return cookiestr

sh_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Cookie': get_cookie('http://wsjkw.sh.gov.cn/xwfb/index.html'),
    # 'Cookie': 'zh_choose=s; zh_choose=s; _gscu_2010802395=80620430ie0po683; yd_cookie=12f170fc-e368-4a662db5220af2d434160e259b2e31585efb; _ydclearance=2cd0a8873fd311efcda1c1aa-05fc-4001-a108-0e86b80b3fee-1580700296; _gscbrs_2010802395=1; _pk_ref.30.0806=%5B%22%22%2C%22%22%2C1580693101%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DDVUbOETLyMZLC5c_V7RJRbAYPvyqaU3f2PCBi2-E6KC2QEFltdrKWGmhgA5NbC3c%26wd%3D%26eqid%3Df38b30250015e1c5000000045e365a8d%22%5D; _pk_ses.30.0806=*; _pk_id.30.0806=35b481da38abb562.1580620431.6.1580694952.1580693101.; _gscs_2010802395=80693100qds57e17|pv:6; AlteonP=ALa1BGHbHKyWUqcNUGRETw$$',
    'Host': 'wsjkw.sh.gov.cn'
}

quanguo_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Cookie': 'oHAcoULcWCQb80S=pxzexGFCvyGV4xDkaMHSyjBmzwXn5O4vfCbxFCgMDfcBaKqsFU9FHstqjFY6wJt9; yfx_c_g_u_id_10006654=_ck20020209283417867964364567575; insert_cookie=67313298; security_session_verify=cdd046e368d8aca2f5503e2ccffd1d6f; yfx_f_l_v_t_10006654=f_t_1580606914774__r_t_1580694464711__v_t_1580695075457__r_c_2; oHAcoULcWCQb80T=4Keu.kLbpJzFTgYuS17WBAWziJn6so.QUEz6HHm0Fo8Gy_MmgQ3KoO.QYwdhMVG3RTKnfG84frm5f0CmsZgt5.CczGuklquP7LpEAcyl4Mfyln5xXmcOoaIbghHy10ediSfInBUc59SIxyekXKFlKdqXhFwvS47acnhsTNlVbspCopRBIcCHNc8HxRasIhLSBFs8UjiLwlcBdw.3MEDQ.m4O6jFo1M2xJfxrhFu1z1Pv_ZmynVDcLndwflWVg20Nn3.xdZ7_5ERSB3fpOKu6CXwAkGTaDnnG5jDQ01y5w5U1h8nv_WRm1TgQnnrbf3AOmHUEKesvqnbCx0WQB0HVocLg6kLJbGLtDrlKix0h97Vu.SG',
    'Host': 'www.nhc.gov.cn'
}


#一、全国和湖北的数据
all_data, hubei_data = get_all_today_news()
# print(all_data, hubei_data)
try:
    all_commited = all_data['累计确诊']
    all_intensive = all_data['累计重症']
    all_death = all_data['累计死亡']
    all_cure = all_data['累计治愈']
    all_suspection = all_data['累计疑似']
    all_new_suspection = all_data['新增疑似']
    hubei_new_commited = hubei_data['新增确诊']
    hubei_new_intensive = hubei_data['新增重症']
    hubei_new_death = hubei_data['新增死亡']
    hubei_new_cure = hubei_data['新增治愈']
    hubei_new_suspection = hubei_data['新增疑似']
except:
    print('全国数据未更新2')
#二、上海的数据
sh_data = get_sh_today_news()
try:
    sh_commited = sh_data['累计确诊']
    sh_intensive = sh_data['累计重症']
    sh_death = sh_data['累计死亡']
    sh_cure = sh_data['累计治愈']
    sh_suspection = sh_data['累计疑似']
    sh_exclude_suspection = sh_data['累计排除疑似']
except:
    print('上海数据未更新2')

print('全国数据：{}\n'
      '湖北数据：{}\n'
      '上海数据：{}'.format(all_data, hubei_data, sh_data))
