#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, re

class const:
    EOL = '\n'
    lineDelim = '-------------------------------------------------------------------------------' + EOL
    lineBegin = '-- '

class field:
    def __init__(self, name):
        self.name = name
        self.comment = ''
        self.parent = None

    def str(self):
        return const.lineDelim + '%s@field [parent=#%s] %s %s' % (const.lineBegin, self.parent, self.name, self.comment) + const.EOL + const.EOL

class function:
    def __init__(self, name):
        self.name = name
        self.comment = ''
        self.parent = None

    def str(self):
        if len(self.comment) > 0:
            return const.lineDelim + self.comment
        
        parent = 'global'
        if self.parent:
            parent = self.parent.fullName()
        return const.lineDelim + '%s@function [parent=#%s] %s' % (const.lineBegin, parent, self.name) + const.EOL

class module:
    __root = None
    
    @classmethod
    def root(cls):
        if not cls.__root:
            cls.__root = module('global')
        return cls.__root

    def __init__(self, name):
        self.name = name    #模块的short name
        self.comment = ''
        self.parent = None
        self.extends = ''
        self.fields = []
        self.functions = []
        self.children = {}   #子模块

    def str(self):
        ret = const.lineDelim + const.lineBegin + '@module %s' % module + const.EOL
        if self.parent and self.parent <> '':
            ret += const.lineBegin + '@extends %s#%s' % (self.parent, self.parent) + const.EOL
        ret += const.EOL
        return ret

    #返回模块的全名
    def fullName(self):
        ret = self.name
        p = self.parent
        while p and p.parent:
            ret = p.name + '.' + ret
            p = p.parent
        return ret

    def addFunction(self, function):
        function.parent = self
        self.functions.append(function)

    def addField(self, field):
        field.parent = self
        self.fields.append(field)

    def output(self, dir):
        s = const.lineDelim
        s += const.lineBegin + '@module %s' % self.name + const.EOL
        if self.extends <> '':
            s += const.lineBegin + '@extends %s' % self.extends + const.EOL
        s += const.EOL + const.EOL

        for field in self.fields:
            s += field.str() + const.EOL
        for function in self.functions:
            s += function.str() + const.EOL
            
        s += const.EOL + 'return nil' + const.EOL
        f = open(os.path.join(dir, self.fullName() + '.lua'), 'wb')
        f.write(s)
        f.close()

    #根据一个字符串返回module
    #skipLast = True时表明字符串的最后一段是函数或变量, 例如cc.net.Socket:test  cc.sdk.pay
    @classmethod
    def getModuleByNames(cls, names, skipLast):
        ms = names.replace(':', '.').split('.')
        if len(ms) == 0:
            print '%s invalid' % names
            return None       
        if len(ms) == 1:
            return cls.root()

        ret = cls.root()
        if skipLast: ms = ms[:-1]
        for m in ms:
            if m in ret.children:
                ret = ret.children[m]
            else:
                tmp = module(m)
                tmp.parent = ret
                ret.children[m] = tmp
                ret = tmp
        return ret

