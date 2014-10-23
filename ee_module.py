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
        parent = 'global'
        if self.parent:
            parent = self.parent.fullName()

        if len(self.comment) > 0:
            return const.lineDelim + self.comment
        else:
            return const.lineDelim + const.lineBegin + '@field [parent=#%s] %s' % (parent, self.name) + const.EOL

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
        if not function.name in self.functions:
            function.parent = self
            self.functions.append(function)

    def addField(self, field):
        if not field.name in self.fields:
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
    def getModuleByName(cls, name, skipLast, parents = None, supers = None, renames = None):
        if renames and name in renames:  #处理module重命名的情况
            name = renames[name]

        ms = name.replace(':', '.').split('.')
        assert(len(ms) > 0)
        if len(ms) == 1:
            #需要检查parents
            if parents and ms[0] in parents:
                return cls.getModuleByName(parents[ms[0]]+'.'+ms[0], False, None, supers, renames)
            else:
                return cls.root()

        ret = cls.root()
        if skipLast: ms = ms[:-1]
        for m in ms:
            if m in ret.children:
                ret = ret.children[m]
            else:
                tmp = module(m)
                tmp.parent = ret
                fullname = tmp.fullName()
                if supers and fullname in supers:  #继承关系
                    tmp.extends = supers[fullname]
                ret.children[m] = tmp
                ret = tmp
        return ret

