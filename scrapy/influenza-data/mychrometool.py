#!/bin/python
# -*- coding: utf-8 -*-
# @File  : mychrometool.py
# @Author: wangms
# @Date  : 2020/2/3
import PyChromeDevTools
import time

chrome = PyChromeDevTools.ChromeInterface()
chrome.Network.enable()
chrome.Page.enable()

chrome.Page.navigate(url="https://alihealth.taobao.com/medicalhealth/influenzamap")
chrome.wait_event("Page.frameStoppedLoading", timeout=60)

#Wait last objects to load
time.sleep(5)

cookies=chrome.Network.getCookies()
for cookie in cookies["result"]["cookies"]:
    print ("Cookie:")
    print ("\tDomain:", cookie["domain"])
    print ("\tKey:", cookie["name"])
    print ("\tValue:", cookie["value"])
    print ("\n")