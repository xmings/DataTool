#!/bin/python
# -*- coding: utf-8 -*-
# @File  : china_outbreaks_2020.py
# @Author: wangms
# @Date  : 2020/1/31
import sys
import requests
import time
from datetime import datetime
import psycopg2


class OutbreaksScrapy(object):
    def __init__(self):
        self.session = requests.Session()

    def run(self):
        data = self.fetch_data()
        print(data)
        self.save(data)

    def fetch_data(self):
        self.session.get("https://alihealth.taobao.com/medicalhealth/influenzamap?spm=a2oua.wuhaninfo.more.wenzhen&chInfo=spring2020-stay-in")
        resp = self.session.get("https://h5api.m.taobao.com/h5/mtop.alihealth.mdeer.pidemic.getcitydiseaseinfo/1.3/", params={
            "jsv": "3.0.5",
            "appKey": "12574478",
            "t": "1580473605319",
            "sign": "6e14170ca914e6eedb4c806d087abefa",
            "type": "originaljson",
            "valueType": "original",
            "v": "1.3",
            "api": "mtop.alihealth.mdeer.pidemic.getCityDiseaseInfo",
            "env": "m",
            "cookie2": "57f3e6c517bc789a7520228543ed15f3",
            "sg": "810",
            "data": "{}"
        }, headers={
            "cookie": "cna=CgAdE3KkmHMCATo+5rwkmb/F; thw=cn; t=01282f578b5fda4c1b8311dd5b69d8d7; tracknick=tigerjor; tg=0; enc=yhKvVNILr9I7i%2FOFBBTzntLiG9Hd8WyWoPSpusILH2ZQZtl0XXkE2KAefT6e%2B6N8fkiLn%2BDllR1f3xpLJBtPJA%3D%3D; hng=CN%7Czh-CN%7CCNY%7C156; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; miid=1540385403175812332; UM_distinctid=16f03cacc741f-0636cc7d454bc4-2393f61-100200-16f03cacc7532c; lgc=tigerjor; v=0; cookie2=1d1444a89f8bc2f9a4af40cd5921f8b8; _tb_token_=ee83b9b33e331; uc3=lg2=UtASsssmOIJ0bQ%3D%3D&vt3=F8dBxdgpATpPx5m6X5M%3D&nk2=F59YitmRsyQ%3D&id2=UoM93NeAax4I; csg=ba3121c9; dnk=tigerjor; skt=ed47424b034cc454; existShop=MTU3ODExMjM3Ng%3D%3D; uc4=nk4=0%40FYWoWOEGxBstfZJj4QkVV%2FRtGw%3D%3D&id4=0%40UOu5RiBAxHYp%2FEEZHHEiXiXFvrI%3D; _cc_=WqG3DMC9EA%3D%3D; uc1=cookie16=Vq8l%2BKCLySLZMFWHxqs8fwqnEw%3D%3D&cookie21=Vq8l%2BKCLjA%2Bl&cookie15=URm48syIIVrSKA%3D%3D&existShop=false&pas=0&cookie14=UoTblAByx2vU7A%3D%3D&tag=8&lng=zh_CN; _samesite_flag_=true; _m_h5_tk=b703696beb747ea4afce24b810985d56_1580482597285; _m_h5_tk_enc=02fd6f82b65dac1c1c7897b444468a9f; l=cBOTwLlmqyDik3qDBOCZourza779SIRAguPzaNbMi_5pw6L_PPbOo4n1sFp6cjWd9x8B4dH2-se9-etkiGuJIt0_Wf-c.; isg=BNDQjh_wumeba2U4sVt94ZUCoR4imbTjc7fUiMqhmCv-BXCvcqvUcqs33c3l1Wy7"
        })

        return resp.text

    def fetch_image(self):
        resp = self.session.get("https://alihealth.taobao.com/medicalhealth/influenzamap")

    def save(self, data):
        db = {
            "host": "192.168.1.161",
            "port": 9999,
            "dbname": "postgres",
            "user": "etl_usr",
            "password": "etl_usr$"
        }
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        data_time = now.replace(hour=10) if now.hour <= 12 else now.replace(hour=16)
        with psycopg2.connect(**db) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    insert into t_china_outbreaks_2020 (data_time, outbreaks_data, insert_time)
                    values (%s, %s, now())
                    on conflict (data_time) do update set outbreaks_data=EXCLUDED.outbreaks_data,insert_time=now()
                """, (data_time, data))
            conn.commit()


def main():
    s = OutbreaksScrapy()
    s.run()


if __name__ == '__main__':
    sys.exit(main())
