#!/bin/python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: wangms
# @Date  : 2019/8/20
# !/usr/bin/env python
import multiprocessing
import os
import time


def do_work(x):
    print('Work Started: %s' % os.getpid())
    time.sleep(10)
    return x * x


def main():
    pool = multiprocessing.Pool(4)
    try:
        result = pool.map_async(do_work, range(8))
        pool.close()
        pool.join()
        print(result)
    except KeyboardInterrupt:
        print('parent received control-c')

        pool.terminate()
        pool.join()


if __name__ == "__main__":
    main()