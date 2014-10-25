#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, re, ee_module, ee_parser

def getQuickxFrameworkDir():
    ret = os.environ.get('QUICK_COCOS2DX_ROOT')
    if not ret or len(ret) == 0:
        ret = os.environ.get('QUICK_V3_ROOT')
    if not ret or len(ret) == 0:
        print 'ERROR: QUICK_COCOS2DX_ROOT and QUICK_V3_ROOT not found in os.environ'
        return None
    docluaDir = os.path.join(ret, 'quick', 'framework')
    return docluaDir

class quickxParser:
    def __getModuleByName(self, name, skipLast):
        return ee_module.module.getModuleByName(name, skipLast, self.parents, self.supers, self.renames)

    #-------------------------------------------------------
    #处理有注释的函数
    def __parseCommentFunction(self, funcName, comment):
        m = self.__getModuleByName(funcName, True)
        if not m: return

        shortName = funcName.replace(':', '.').split('.')[-1]
        parent = m.name
        s = '\n' + comment.strip('-[]\r\n\t ').strip()

        #每行前面加上-- ，这是ee的要求
        p = re.compile(r'(\n[- \t]*)(.*)')
        s = p.sub(r'\n-- \2', s).lstrip()

        #在把@function插入在合适的地方
        pos = s.find('@')
        if pos >= 0:
            tmp = ee_module.const.lineDelim + s[:pos] + '@function [parent=#%s] %s%s-- ' % (parent, shortName, ee_module.const.EOL) + s[pos:] + ee_module.const.EOL
        else:
            tmp = ee_module.const.lineDelim + s + ee_module.const.EOL + '-- @function [parent=#%s] %s%s' % (parent, shortName, ee_module.const.EOL)

        #把@param string这种替换为@param #string
        p = re.compile(r'(.*)(@param[ \t]+)(string|number|table|function|integer|boolean|mixed)([^\n\r]*)')
        tmp = p.sub(r'\1\2#\3\4', tmp)

        f = ee_module.function(shortName)
        f.comment = tmp
        m.addFunction(f)

    #处理无注释的函数
    def __parseFunction(self, funcName):
        m = self.__getModuleByName(funcName, True)
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
            return

        if commentStart >= 0 and commentEnd >= 0:
            #检查注释块和函数之间只有空白字符
            m = self.data[commentEnd:functionStart].strip()
            if m == '':
                self.__parseCommentFunction(funcName, self.data[commentStart:commentEnd])
                return
        self.__parseFunction(funcName)

    #-------------------------------------------------------
    #处理有注释的变量
    def __parseCommentVar(self, varName, comment):
        m = self.__getModuleByName(varName, True)
        if not m: return

        shortName = varName.split('.')[-1]
        parent = m.name
        s = '\n' + comment.strip('-[]\r\n\t ').strip()

        #每行前面加上-- ，这是ee的要求
        p = re.compile(r'(\n[- \t]*)(.*)')
        s = p.sub(r'\n-- \2', s).lstrip()
        tmp = ee_module.const.lineDelim + s + ee_module.const.EOL + '-- @field [parent=#%s] %s' % (parent, shortName) + ee_module.const.EOL        

        f = ee_module.field(shortName)
        f.comment = tmp
        m.addField(f)

    #处理无注释的变量
    def __parseVar(self, varName):
        m = self.__getModuleByName(varName, True)
        if not m: return

        shortName = varName.split('.')[-1]
        f = ee_module.field(shortName)
        m.addField(f)

    #返回变量名
    def __getVarName(self, varStart, varEnd):
        ret = self.data[varStart:varEnd].strip()
        return ret

    #处理变量
    def __doCommentVar(self, commentStart, commentEnd, varStart, varEnd):
        #先获取变量名
        varName = self.__getVarName(varStart, varEnd)
        if varName == '':
            print 'ERROR: can not get var name!'
            return

        if commentStart >= 0 and commentEnd >= 0:
            #检查注释块和变量之间只有空白字符
            m = self.data[commentEnd:varStart].strip()
            if m == '':
                self.__parseCommentVar(varName, self.data[commentStart:commentEnd])
                return
        self.__parseVar(varName)

    #判断是local函数吗
    def __isLocalFunction(self, funcpos):
        pos = self.data.rfind('\n', 0, funcpos)
        if pos < 0: pos = 0
        s = self.data[pos:funcpos].strip()
        return s == 'local'

    #处理参数
    def __handleArgs(self, vars, parents, supers, renames):
        pat = re.compile(r'\s')
        self.vars = pat.sub('', vars or '')
        parents = pat.sub('', parents or '')
        supers = pat.sub('', supers or '')
        renames = pat.sub('', renames or '')
        
        self.parents = {}
        self.supers = {}
        self.renames = {}
        
        if parents <> '':
            for item in parents.split('|'):
                arr = item.split('>')
                assert(len(arr) == 2)
                self.parents[arr[0]] = arr[1]

        if supers <> '':
            for item in supers.split('|'):
                arr = item.split('>')
                assert(len(arr) == 2)
                self.supers[arr[0]] = arr[1]

        if renames <> '':
            for item in renames.split('|'):
                arr = item.split('>')
                assert(len(arr) == 2)
                self.renames[arr[0]] = arr[1]

    #处理单个lua文件
    # @param src 要处理的lua文件
    # @param vars 用来指定src中要捕获变量的模块名，例如  cc.TEST = 1这种就需要填cc，多个模块名用|连接，例如cc|ccs
    # @param parents 用来指定模块的父模块信息，例如Store>cc|Socket>cc.net，模块名是shortname，父模块名是fullname
    # @param supers 用来指定模块的基类信息，例如Store>cc.Ref|Socket>cc.Ref，模块名是shortname，基类是fullname
    # @param renames 用来指定模块的重命名信息，例如Store>pay|Socket>socket，模块名是shortname，新名字也是shortname
    def doFile(self, src, vars = None, parents = None, supers = None, renames = None):
        self.__handleArgs(vars, parents, supers, renames)

        self.data = open(src, 'rb').read().replace('\r', '')

        parser = ee_parser.parser(self.data)

        #加入vars的token
        if self.vars <> '':
            parser.addToken('var', r'\b(%s)\.\w+\s*=' % self.vars)

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
            elif type == 'var':
                end = self.data.find('=', start)
                if preType == 'blockComment' or preType == 'lineComment':
                    self.__doCommentVar(preStart, preEnd, start, end)
                else:
                    self.__doCommentVar(-1, -1, start, end)

    def doQuickx(self):
        #获取framework目录
        docluaDir = getQuickxFrameworkDir()
        if not docluaDir:
            return

        #获取ini文件
        my = ee_module.getCurrDir()
        data = open(os.path.join(my, 'quickx.ini'), 'rb').read()
        lines = data.split('\n')
        for line in lines:
            line = line.strip()
            pos = line.find('#')  #去掉注释
            if pos >= 0:
                line = line[:pos]
            if line == '': continue
            items = line.split(',')
            if len(items) <> 5:
                print '%s invalid' % line
            self.doFile(os.path.join(docluaDir, items[0]), items[1], items[2], items[3], items[4])
