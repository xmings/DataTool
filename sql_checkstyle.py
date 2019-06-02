#!/bin/python
# -*- coding: utf-8 -*-
# @File  : sql_checkstyle.py
# @Author: wangms
# @Date  : 2019/5/31
import re
from dataclasses import dataclass

@dataclass
class Warnning(object):
    file: str
    line_no: int
    warn_content: str


KEYWORD = []

"""
Check Point:
    1. whether upper or not for keyword
    2. whether indent as need for every line
    3. whether a comment in a single line
"""
class SQLCheckStyle(object):
    def __init__(self):
        self.warnning_list = []

    def run(self):
        files = self.recognize_modified_file()
        for f in files:
            self.check_style(f)


    def recognize_modified_file(self):
        return []

    def check_style(self, file):
        # we need to ignore the semicolon in comment at first.
        segment_list = self.fetch_segment_list(file)
        for segment_begin_no, segment in segment_list:
            query_level = 0
            for line_no, line in enumerate(segment.split("\r")):


                # check indent



                # check keyword
                self.check_keyword_upper(line)


        pass

    def check_line_indent(self, query_level, line):
        pass

    def check_keyword_upper(self, line):
        pass

    def split_line_to_word(self, line):
        quote_begin = False

        new_line_list = []
        for word in line.split(" "):
            if word.find("'")>=0:
                if not quote_begin:
                    quote_begin = True
                else:
                    quote_begin = False
                    new_line_list.append()











    def remove_line_comment(self, line):
        if line.strip(" ").startswith("--"):
            return ""

        if line.count("--") > 0:
            qoute_begin = False

            new_line = ""
            for i in line:
                if i == "'":
                    qoute_begin = True if not qoute_begin else False

                if i == "-" and new_line.endswith("-"):
                    if qoute_begin:
                        continue
                    new_line.rstrip("-")
                    break
                new_line += i
            return new_line
        return line


    def fetch_segment_list(self, file):
        with open(file, 'r', encoding="utf8") as f:
            content = f.read()
        content = content.replace("\r\n", "\r").replace("\n", "\r")

        # remove block comment
        segment_list = []
        comment_begin = False
        for line_no, line in enumerate(content.split("\r")):
            if line.find("/*") >= 0 and line.count("'")%2 == 0:
                comment_begin = True

            if line.find("*/") >= 0 and comment_begin:
                comment_begin = False
                continue

            if comment_begin:
                continue
            segment_list.append((line_no, line))

        # combin line to segment
        segment = ""
        segment_begin_no = 0
        segment_begin = False
        for line_no, line in segment_list:
            # remove blank line
            if line.strip(" ") == "":
                continue

            # remove line comment
            new_line = self.remove_line_comment(line)
            if new_line == "":
                continue
            if new_line != line:
                self.warnning_list.append((line_no, "line comment must be at single line"))
            line = new_line

            # permit to use double quotation mark
            if line.find('"') >= 0:
                self.warnning_list.append((line_no, "permit to use double quotation mark"))

            # combin line
            if not segment_begin:
                segment_begin = True
                segment_begin_no = line_no
                segment = line

            if line.endswith(";"):
                segment_list.append((segment_begin_no, segment))
                segment_begin = False
                continue

            segment += line

        return segment_list







