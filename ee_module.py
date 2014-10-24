#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, re

#获取脚本文件的当前路径
def getCurrDir():
    #获取脚本路径
    path = sys.argv[0]
    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
       return path
    elif os.path.isfile(path):
       return os.path.dirname(path)

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
            return self.comment
        else:
            return const.lineDelim + const.lineBegin + '@field [parent=#%s] %s' % (parent, self.name) + const.EOL

class function:
    def __init__(self, name):
        self.name = name
        self.comment = ''
        self.parent = None

    def str(self):
        if len(self.comment) > 0:
            return self.comment
        
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
        #先输出module信息
        if len(self.comment) > 0:
            s = self.comment + const.EOL + const.EOL
        else:
            s = const.lineDelim
            s += const.lineBegin + '@module %s' % self.name + const.EOL
            if self.extends <> '':
                s += const.lineBegin + '@extends %s' % self.extends + const.EOL
            s += const.EOL + const.EOL

        #输出preloaded module信息
        for child in self.children:
            modname = self.children[child].name
            s += const.lineDelim
            s += const.lineBegin + '@field [parent = #%s] %s#%s %s preloaded module' % (self.fullName(), modname, modname, modname) + const.EOL + const.EOL

        for function in self.functions:
            s += function.str() + const.EOL
            
        for field in self.fields:
            s += field.str() + const.EOL
            
        s += const.EOL + 'return nil' + const.EOL
        f = open(os.path.join(dir, self.fullName() + '.doclua'), 'wb')
        f.write(s)
        f.close()

    #根据一个字符串返回module
    # @param name
    # @param skipLast 表明name的最后一段是不是函数或变量, 例如cc.net.Socket:test  cc.sdk.pay
    # @param parents 用来指定模块的父模块信息，例如Store>cc，模块名是shortname，父模块名是fullname
    # @param supers 用来指定模块的基类信息，例如Store>cc.Ref，模块名是shortname，基类是fullname
    # @param renames 用来指定模块的重命名信息，例如Store>pay，模块名是shortname，新名字也是shortname
    @classmethod
    def getModuleByName(cls, name, skipLast, parents = None, supers = None, renames = None):
        ms = name.strip().replace(':', '.').split('.')
        if len(ms) == 1:
            if skipLast: return cls.root()  #类似printf/class这种顶级函数

            m = ms[0]
            if m == 'global':
                return cls.root()

            #处理module重命名的情况
            if renames and m in renames:
                if m <> renames[m]:  #pay>pay这种错误写法导致的死循环
                    return cls.getModuleByName(renames[m], False, parents, supers)

            #需要检查parents
            if parents and m in parents:
                #拼成完整的name再次getModuleByName
                return cls.getModuleByName(parents[m]+'.'+m, False, None, supers)

            #说明是顶级mod
            root = cls.root()
            if m in root.children:
                return root.children[m]
            else:
                mod = module(m)
                mod.parent = root
                if supers and m in supers:  #继承关系
                    mod.extends = supers[m]
                root.children[m] = mod
                return mod
        else:
            ret = cls.root()
            if skipLast: ms = ms[:-1]
            for m in ms:
                if m in ret.children:
                    ret = ret.children[m]
                else:
                    tmp = module(m)
                    tmp.parent = ret
                    if supers and m in supers:  #继承关系
                        tmp.extends = supers[m]
                    ret.children[m] = tmp
                    ret = tmp
            return ret


    @staticmethod
    def __output(m, dir):
        if m:
            m.output(dir)
            for child in m.children:
                module.__output(m.children[child], dir)

    #把所有的module信息写到dir目录下
    @classmethod
    def outputAll(cls, dir):
        module.__output(cls.root(), dir)
