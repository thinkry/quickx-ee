#!/usr/bin/python
# -*- coding: utf-8 -*-
#处理cocos2dx生成的doclua

import sys, os, re, ee_module

def getCososDocluaDir():
    cocos = os.environ.get('COCOS2DX_ROOT')
    if not cocos or len(cocos) == 0:
        print 'ERROR: COCOS2DX_ROOT not found in os.environ'
        return None
    docluaDir = os.path.join(cocos, 'cocos', 'scripting', 'lua-bindings', 'auto', 'api')
    return docluaDir

class docluaParse:
    #解析模块信息
    def __parseModule(self, s):
        m = re.search(r'--\s+@module\s+(\w+)', s)
        if not m:
            print '%s not @module' % file
            return None
        modname = m.group(1).strip()

        parents = {}
        m = re.search(r'--\s+@parent_module\s+(\w+)', s)
        if m:
            parents[modname] = m.group(1).strip()
        
        supers = {}
        m = re.search(r'--\s+@extend\s+(\w+)', s)
        if m:
            supers[modname] = m.group(1).strip()
        
        mod = ee_module.module.getModuleByName(modname, False, parents, supers)
        mod.comment = re.compile(r'@extend[ \t]+').sub(r'@extends ', s)  #把@extend改为extends
        return mod

    #处理每一块
    def __parseItem(self, s, mod):
        if re.search(r'--\s@field.*preloaded module', s): #是preloaded module块
            return
        if re.search(r'--\s@type\b', s): #lua5.1 io.doclua中有个@type定义，我们跳过
            return
        m = re.search(r'--\s+@(function|field)\s*\[\s*parent\s*=\s*#(\w+)\s*\]\s+(?:#\w+\s*)*(\w+)', s)
        if not m:
            print 'invalid item: ' + s
            return

        (type, parent, name) = m.groups()
        if type == 'function':
            f = ee_module.function(name)
        else:
            f = ee_module.field(name)
        f.comment = s

        if parent <> mod.name:
            mod = ee_module.module.getModuleByName(parent, False)

        if type == 'function':
            mod.addFunction(f)
        else:
            mod.addField(f)

    def doFile(self, file):
        self.data = open(file, 'rb').read().replace('\r', '')
        arr = re.findall(r'-{3,}\n(?:--[^-].*?\n)+', self.data, re.S)
        
        #第一块必须是module
        mod = self.__parseModule(arr[0])

        #处理每一块
        for item in arr[1:]:
            self.__parseItem(item, mod)

    def doLua(self):
        my = getCurrDir()
        docluaDir = os.path.join(my, 'lua5.1', 'api')
        for root, dirs, files in os.walk(docluaDir):
            for file in files:
                src = os.path.join(root, file)
                self.doFile(src)

    def doCocos2dx(self):
        docluaDir = docluaParse.getCososDocluaDir()
        if not docluaDir:
            return

        for root, dirs, files in os.walk(docluaDir):
            for file in files:
                src = os.path.join(root, file)
                self.doFile(src)
