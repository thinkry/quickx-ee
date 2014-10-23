#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, re, ee_module, ee_parser

class gen:
    def __init__(self):
        pass
        
    #处理有注释的函数
    def __parseCommentFunction(self, funcName, comment):
        m = ee_module.module.getModuleByNames(funcName, True)
        if not m: return

        shortName = funcName.replace(':', '.').split('.')[-1]
        parent = m.fullName()
        s = '\n' + comment.strip('-[]\r\n\t ').strip()

        #每行前面加上-- ，这是ee的要求
        p = re.compile(r'(\n[- \t]*)(.*)')
        s = p.sub(r'\n-- \2', s).lstrip()

        #在把@function插入在合适的地方
        pos = s.find('@')
        if pos >= 0:
            tmp = s[:pos] + '@function [parent=#%s] %s%s-- ' % (parent, shortName, ee_module.const.EOL) + s[pos:] + ee_module.const.EOL
        else:
            tmp = s + ee_module.const.EOL + '-- @function [parent=#%s] %s%s' % (parent, shortName, ee_module.const.EOL)
            
        #把@param string这种替换为@param #string
        p = re.compile(r'(.*)(@param[ \t]+)(string|number|table|function|integer|boolean|mixed)([^\n\r]*)')
        tmp = p.sub(r'\1\2\4,\3', tmp)
        
        f = ee_module.function(shortName)
        f.comment = tmp
        m.addFunction(f)

    #解析无注释的函数
    def __parseFunction(self, funcName):
        m = ee_module.module.getModuleByNames(funcName, True)
        if not m: return

        shortName = funcName.replace(':', '.').split('.')[-1]
        f = ee_module.function(shortName)
        m.addFunction(f)

    #返回函数名
    def __getFuncName(self, functionStart, functionEnd):
        ret = self.data[functionStart:functionEnd].strip()
        arr = re.findall(r'function[ \t]+([a-zA-Z0-9_\.:]+)[ \t]*', ret)
        if len(arr) > 0:
            return arr[0]
        else:
            return ''

    #处理函数
    def __doCommentFunction(self, commentStart, commentEnd, functionStart, functionEnd):
        #先获取函数名
        funcName = self.__getFuncName(functionStart, functionEnd)
        if funcName == '':
            print 'ERROR: can not get function name!'
            return

        if commentStart >= 0 and commentEnd >= 0:
            #检查注释块和函数之间只有空白字符
            pat = re.compile(r'\s*', re.S)
            m = pat.match(self.data, commentEnd, functionStart)
            if m:
                self.__parseCommentFunction(funcName, self.data[commentStart:commentEnd])
                return
        self.__parseFunction(funcName)

    #判断是local函数吗
    def __isLocalFunction(self, funcpos):
        pos = self.data.rfind('\n', 0, funcpos)
        if pos < 0: pos = 0
        s = self.data[pos:funcpos].strip()
        return s == 'local'

    #处理单个lua文件
    # @param src 要处理的lua文件
    # @param vars 用来指定src中要捕获变量的模块名，例如  cc.TEST = 1这种就需要填cc，多个模块名用|连接，例如cc|ccs
    # @param parents 用来指定src中出现的模块名的父模块，例如UIButton->cc.ui|Socket->cc.net，父模块请填写全名
    # @param supers 用来指定src中出现的模块名的基类，例如UICheckBoxButton->cc.ui.UIButton，基类请填写全名
    # @param renames 用来指定src中出现的模块名的重命名信息，例如Store->cc.sdk.pay，新名字请写全名
    def doFile(self, src, vars = None, parents = None, supers = None, renames = None):
        self.vars = vars
        self.parents = parents
        self.supers = supers
        self.renames = renames
        self.data = open(src, 'rb').read()

        parser = ee_parser.parser(self.data)
        #加入vars的token
        
        type, start, end = '', -1, -1
        depth = 0   #用于end的配对
        while True:
            preType, preStart, preEnd = type, start, end
            
            token = parser.nextToken()
            if not token: break
            type = token.name
            start, end = token.range()
            
            if type == 'function':
                depth = depth + 1
                if self.__isLocalFunction(start):  #说明是local
                    continue
                if depth > 1:  #说明是函数的内部函数
                    continue

                end = self.data.find('(', start)
                if preType == 'blockComment' or preType == 'lineComment':
                    self.__doCommentFunction(preStart, preEnd, start, end)
                else:
                    self.__doCommentFunction(-1, -1, start, end)
            elif type in ['if', 'for', 'while']:
                depth = depth + 1
            elif type == 'end':
                depth = depth - 1

    @staticmethod
    def __output(m, dir):
        if m:
            m.output(dir)
            for child in m.children:
                gen.__output(m.children[child], dir)

    def output(self, dir):
        gen.__output(ee_module.module.root(), dir)

def main():
    g = gen()
    g.doFile('d:\\cocos\\quick-cocos2d-x-3.2rc1\\quick\\framework\\functions.lua')
    #g.doFile('c:\\functions.lua')
    g.output('c:\\work')

if __name__ == '__main__':
    main()
