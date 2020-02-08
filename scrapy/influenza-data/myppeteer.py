#!/bin/python
# -*- coding: utf-8 -*-
# @File  : myppeteer.py
# @Author: wangms
# @Date  : 2020/2/3
import re
import asyncio
from pyppeteer import launch
from pyppeteer.network_manager import Request, Response

launch_args = {
    "headless": False,
    "args": [
        "--start-maximized",
        "--no-sandbox",
        "--disable-infobars",
        "--ignore-certificate-errors",
        "--log-level=3",
        "--enable-extensions",
        "--window-size=1920,1080",
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
    ],
}


async def modify_url(request: Request):
    if request.url == "https://www.baidu.com/":
        await request.continue_({"url": "https://www.baidu.com/s?wd=ip&ie=utf-8"})
    else:
        await request.continue_()


async def fetch_data(response: Response):
    if response.url == "https://h5api.m.taobao.com/h5/mtop.alihealth.mdeer.pidemic.getcitydiseaseinfo/1.3/":
        content = await response.text()
        title = re.search(b"", content)
        print(title.group(1))


async def interception_test():
    # 启动浏览器
    browser = await launch(**launch_args)
    # 新建标签页
    page = await browser.newPage()
    # 设置页面打开超时时间
    page.setDefaultNavigationTimeout(10 * 1000)
    # 设置窗口大小
    await page.setViewport({"width": 1920, "height": 1040})
    # 启用拦截器
    await page.setRequestInterception(True)
    # 设置拦截器
    # 1. 修改请求的url
    if 1:
        page.on("response", fetch_data)
    await asyncio.sleep(10)
    # 关闭浏览器
    await page.close()
    await browser.close()
    return


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(interception_test())