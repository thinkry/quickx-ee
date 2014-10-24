#!/usr/bin/python
# -*- coding: utf-8 -*-
#生成quick-x所需的ee文件
#
#这个ee文件由三部分组成:
#   1.lua5.1的doclua，直接从LDT下拿过来的，放在lua5.1目录下
#   2.cocos2dx生成的doclua，但格式上与LDT要求的有点差异，需要在本脚本里做些处理
#   3.从quickx framework生成的doclua，这个在本脚本里完成
#有这三部分后，再打包生成zip格式的ee文件
#
#目录和文件说明
#   lua5.1: 存放从LDT里取出来的lua5.1的ee文件（解压后），该目录不会修改，也请不要修改
#   release:  #生成的临时文件和最终文件会放在这里
#   |- api: 存放最终ee文件中的doclua，包括上面的三部分，该目录不存在时会创建
#   |- docs: 存放最终ee文件中的docs，目前只有lua5.1，，该目录不存在时会创建
#   |- quickx3.2-lua5.1.rockspec: 存放最终ee文件中的rockspec文件，该文件不存在时会创建
#   gen_quickx_ee.py:  本脚本

import sys, os, re, shutil, time, ee_gen, ee_cocos2dx, ee_module

#--------------------------------------------------------------------

#初始检查：lua5.1目录是否存在，quickx framework和cocos2dx doclua是否存在
def checkEnv():
    root = ee_module.getCurrDir()
    luaDir = os.path.join(root, 'lua5.1')
    if not os.path.exists(luaDir):
        print 'ERROR: lua5.1 directory not exist!'
        return False
    
    path = ee_gen.getQuickxFrameworkDir()
    if not path or not os.path.exists(path):
        print 'ERROR: quickx framework directory not exist!'
        return False

    path = ee_cocos2dx.getCososDocluaDir()
    if not os.path.exists(path):
        print 'ERROR: cocos2dx doclua directory not exist!'
        return False
    
    return True

#创建release目录及子目录，如果目录已存在则清空目录里的文件
def createDir():
    root = ee_module.getCurrDir()
    releaseDir = os.path.join(root, 'release')
    if os.path.exists(releaseDir):
        shutil.rmtree(releaseDir)
        time.sleep(2)
    os.mkdir(releaseDir)
    os.mkdir(os.path.join(releaseDir, 'api'))

#创建rockspec文件
def createRockspec():
    d =  'package = "quickx3.2-lua5.1"\r\n'
    d += 'version = "3.2"\r\n'
    d += 'flags = { ee = true }\r\n'
    d += 'description = {\r\n'
    d += '    summary = "Quickx 3.2 - Lua 5.1 Execution Environment",\r\n'
    d += '    detailed = [[Quickx 3.2 - Lua 5.1 Execution Environment Support]],\r\n'
    d += '    licence = "MIT",\r\n'
    d += '    homepage= "http://www.lua.org/manual/5.1/manual.html"\r\n'
    d += '}\r\n'
    d += 'api = {\r\n'
    d += '    file="api.zip"\r\n'
    d += '}\r\n'
    d += 'documentation ={\r\n'
    d += '    dir="docs"\r\n'
    d += '}\r\n'
    open(os.path.join(ee_module.getCurrDir(), 'release', 'quickx3.2-lua5.1.rockspec'), 'wb').write(d)

#把lua5.1里的api和docs复制到release目录下的对应位置
def copyLua():
    root = ee_module.getCurrDir()
    src = os.path.join(root, 'lua5.1', 'docs')
    dst = os.path.join(root, 'release', 'docs')
    shutil.copytree(src, dst)

#对quickx framework生成doclua
def handleQuickx():
    p = ee_cocos2dx.docluaParse()
    p.doLua()
    p.doCocos2dx()

#对quickx framework生成doclua
def handleQuickx():
    g = ee_gen.gen()
    g.doQuickx()

#压缩成zip
def zipEe():
    pass

#--------------------------------------------------------------------
def main():
    #初始检查：lua5.1目录是否存在，quickx framework和cocos2dx doclua是否存在
    if not checkEnv(): return

    #创建release目录及子目录，如果目录已存在则清空目录里的文件
    createDir()
    
    #创建rockspec文件
    createRockspec()
    
    #把lua5.1里的docs复制到release目录下的对应位置
    copyLua()

    #把cocos2dx doclua边复制，边处理到对应位置下
    #handleCocos2dx()
    
    #对quickx framework生成doclua
    handleQuickx()

    #输出
    dst = os.path.join(ee_module.getCurrDir(), 'release', 'api')
    ee_module.module.outputAll(dst)

    #压缩成zip
    zipEe()

if __name__ == '__main__':
    main()
