from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.remote_connection import RemoteConnection
import os
import time
import json
import subprocess


class MySelenium(object):
    def __init__(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--enable-automation")
        chrome_options.add_experimental_option('w3c', False)
        chrome_options.add_experimental_option('excludeSwitches', ["enable-automation"])

        chrome_options.add_argument('--user-agent="User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"')  # 设置请求头的User-Agent
        chrome_options.add_argument("--disable-infobars")
        # chrome_options.add_argument('--window-size=1280x1024')  # 设置浏览器分辨率（窗口大小）
        # chrome_options.add_argument('--start-maximized')  # 最大化运行（全屏窗口）,不设置，取元素会报错
        # chrome_options.add_argument('--disable-infobars')  # 禁用浏览器正在被自动化程序控制的提示
        # chrome_options.add_argument('--incognito')  # 隐身模式（无痕模式）
        # chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
        # #chrome_options.add_argument('--disable-javascript')  # 禁用javascript
        # chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
        #
        # chrome_options.add_argument('--ignore-certificate-errors')  # 禁用扩展插件并实现窗口最大化
        # chrome_options.add_argument('--disable-software-rasterizer')
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                    })
                  """
        })
        executable_path = os.path.join(os.path.abspath("."), "chromedriver.exe")
        print(executable_path)
        caps = DesiredCapabilities.CHROME
        caps['loggingPrefs'] = {'performance': 'ALL'}
        self.driver = webdriver.Chrome(executable_path=executable_path,
                                       options=chrome_options,
                                       desired_capabilities=caps)
        #self.driver.add_cookie("")
        self.base_url = "https://alihealth.taobao.com/medicalhealth/influenzamap"

    def fetch_demostic_influenza_data(self):
        self.driver.get(self.base_url)
        elements = self.driver.find_element_by_class_name("show-all")
        while not elements:
            time.sleep(1)
            elements = self.driver.find_element_by_class_name("show-all")
        elements.click()
        time.sleep(0.5)
        elements = self.driver.find_element_by_class_name("influenza-city-area")
        all_data = []
        for i in elements.find_elements_by_css_selector(".province"):
            province_name = i.find_element_by_css_selector("span.province-name").text
            total_confirmed_count = i.find_element_by_css_selector(".province-item>.taro-text").text
            _, total_death_count, total_cured_count = [ii.text for ii in
                                                       i.find_elements_by_css_selector(".province-item.taro-text")]
            all_data.append({
                "province_name": province_name,
                "total_confirmed_count": total_confirmed_count,
                "total_death_count": total_death_count,
                "total_cured_count": total_cured_count,
                "city_data": []
            })

            self.driver.execute_script("arguments[0].click();", i.find_element_by_css_selector(".province-info.info-item"))
            time.sleep(0.05)
            for ii in i.find_elements_by_css_selector(".province-cities-info>.city-info"):
                city_name = ii.find_element_by_css_selector("span.city-item").text
                confirmed_count = ii.find_element_by_css_selector(".city-item>.taro-text").text
                _, death_count, cured_count = [iii.text for iii in
                                               ii.find_elements_by_css_selector(".city-item.taro-text")]
                all_data[-1]["city_data"].append({
                    "city_name": city_name,
                    "confirmed_count": confirmed_count,
                    "death_count": death_count,
                    "cured_count": cured_count
                })

        print(json.dumps(all_data, indent=4, ensure_ascii=False))


    def fetch_influenza_trend_chart(self):
        self.driver.get(self.base_url)
        elements = self.driver.find_element_by_class_name("influenza-line-area")
        elements.screenshot("image/influenza-line-area.png")

        elements = elements.find_element_by_css_selector(".canvas")
        self.driver.execute_script("arguments[0].toDataURL('image/png');", elements.find_element_by_css_selector(".canvas"))

    def fetch_response_data(self):
        self.driver.get(self.base_url)
        logs = self.driver.get_log("performance")
        for i in logs:
            message =json.loads(i["message"])["message"]
            if message["method"] == "Network.responseReceived" \
                    and message["params"]["response"]["mimeType"] == "application/json":
                request_id = message["params"]["requestId"]
                print(f"request_id: {request_id}")
                result = self.driver.execute_cdp_cmd('Network.getResponseBody', {"requestId": request_id})
                print(result)
    def fetch_nhc_gzbd_publish(self):

        self.driver.get("http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml")
        #self.driver.get('https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html')
        time.sleep(5)
        elements = self.driver.find_elements_by_css_selector(".zxxx_list>li")
        data = {}
        for ele in elements:
            data_time = ele.find_element_by_css_selector("span").text
            data_link = ele.find_element_by_css_selector("a").get_attribute("href")
            data_title = ele.find_element_by_css_selector("a").get_attribute("title")
            if data_title.find("肺炎疫情")>0 and data_time>'2020-01-21':
                data[data_time] = data_link
        import re


        for day, link in data.items():
            self.driver.get(link)
            time.sleep(0.1)
            content = self.driver.find_elements_by_css_selector("#xw_box>p")[0].text
            confirmed_count = re.findall(r"新增确诊.*?(\d+).*?湖北.*?(\d+)", content)
            cured_count = re.findall(r"新增治愈.*?(\d+).*?湖北.*?(\d+)", content)
            relieved_count = re.findall(r"当日解除医学观察.*?(\d)", content)
            icu_count = re.findall(r"新增重症.*?(\d+).*?湖北.*?(\d+)", content)
            death_count = re.findall(r"新增死亡.*?(\d+).*?湖北.*?(\d+)例", content)
            suspected_count = re.findall(r"新增疑似.*?(\d+).*?湖北.*?(\d+)", content)

            total_confirmed_count = re.findall(r"累计.*?确诊.*?(\d+)", content)
            total_cured_count = re.findall(r"累计治愈.*?(\d+)", content)
            current_confirmed_count = re.findall(r"现有确诊.*?(\d+)", content)
            total_relieved_count = re.findall(r"当日解除医学观察.*?(\d)", content)
            total_icu_count = re.findall(r"重症.*?(\d+).*?湖北.*?(\d+)", content)
            total_death_count = re.findall(r"累计死亡病例(\d+)例", content)
            total_suspected_count = re.findall(r"新增疑似病例(\d+)例（湖北(\d+)例", content)
            current_suspected_count = re.findall(r"现有疑似病例(\d+)例", content)
            total_trace_count = re.findall(r"累计追踪到密切接触者(\d+)人", content)
            current_trace_count = re.findall(r"尚在医学观察的密切接触者(\d+)人", content)

            print(f"{day}, {confirmed_count[0]}({confirmed_count[1]}), {cured_count[0]}({cured_count[1]}), "
                  f"{relieved_count}, {icu_count[0]}({icu_count[1]}), {death_count[0]}({death_count[1]}),"
                  f"{suspected_count[0]}({suspected_count[1]})")

    def __del__(self):
        self.driver.close()
        subprocess.run('wmic process where "name = \'chromedriver.exe\'" call terminate', stdout=subprocess.PIPE, shell=True)

if __name__ == '__main__':
    ms = MySelenium()
    ms.fetch_nhc_gzbd_publish()
