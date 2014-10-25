#!/usr/bin/python
# -*- coding: utf-8 -*-
# 简单的lua doc解析器

import re

class token:
    def __init__(self, name, pattern):
        self.name = name
        self.pattern = pattern
        self.match = None
        self.end = False    #还没结束
    
    #执行一次搜索
    def search(self, s, pos):
        if self.end: return
        if not self.match or self.match.start() < pos:
            self.match = self.pattern.search(s, pos)
            if not self.match:
                self.end = True

    #返回匹配到的start,end
    def range(self):
        if self.end or not self.match: return -1, -1
        return self.match.start(), self.match.end()

class parser:
    def __init__(self, s):
        self.__s = s
        self.__pos = 0
        self.__tokens = []
        self.addToken('blockComment', r'--\[(=*)\[.*?\]\1\]', re.S)  #多行注释
        self.addToken('lineComment', r'--(?!\[=*\[).*')  #单行注释
        self.addToken('singleString', r"'[^'\\]*(?:(?:\\.[^'\\]*)+)*'")  #单引号字符串
        self.addToken('doubleString', r'"[^"\\]*(?:(?:\\.[^"\\]*)+)*"')  #双引号字符串
        self.addToken('multiString', r'\[(=*)\[.*?\]\1\]', re.S)  #多行字符串
        self.addToken('function', r'\bfunction\b')  #function
        self.addToken('if', r'\bif\b')  #if
        self.addToken('for', r'\bfor\b') #for
        self.addToken('while', r'\bwhile\b') #while
        self.addToken('end', r'\bend\b') #end

    def addToken(self, name, pattern, flags=0):
        self.__tokens.append(token(name, re.compile(pattern, flags)))

    def nextToken(self):
        #对各pattern进行搜索
        rtoken, rstart, rend = None, -1, -1
        for token in self.__tokens:
            token.search(self.__s, self.__pos)
            if not token.end:
                tstart, tend = token.range()
                if rstart < 0 or (tstart >= 0 and tstart < rstart):
                    rtoken = token
                    rstart, rend = token.range()

        #找到最近的那个token后
        if rtoken:
            self.__pos = rend

        return rtoken
