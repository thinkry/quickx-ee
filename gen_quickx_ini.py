#!/usr/bin/python
# -*- coding: utf-8 -*-
#生成quick-x framework的ini文件

import sys, os, ee_module

#--------------------------------------------------------------------
def main():
    #获取framework目录
    ret = os.environ.get('QUICK_COCOS2DX_ROOT')
    if not ret or len(ret) == 0:
        ret = os.environ.get('QUICK_V3_ROOT')
    if not ret or len(ret) == 0:
        print 'ERROR: QUICK_COCOS2DX_ROOT and QUICK_V3_ROOT not found in os.environ'
        return
    docluaDir = os.path.join(ret, 'quick', 'framework')
    if not os.path.exists(docluaDir):
        print 'ERROR: quickx framework directory not exist!'
        return
    
    cwd = os.getcwd()
    os.chdir(docluaDir)
    ret = '#luafile, vars, parent_module, super, renames' + os.linesep
    for root, dirs, files in os.walk('.'):
        for file in files:
            isComment = False
            src = os.path.join(root, file)
            basename = os.path.basename(src)
            
            #注释掉各模块的init.lua
            if basename == 'init.lua':
                isComment = True
            
            #这些文件也注释掉
            if src in ['.\deprecated\deprecated_functions.lua', '.\debug.lua']:
                isComment = True

            module = os.path.splitext(basename)[0]
            tmp = src.split(os.sep)
            if len(tmp) > 1:
                parent = '.'.join(tmp[0:-1])
                if parent == '.': parent = ''
                else: parent = parent.strip('.')
            else:
                parent = ''
                
            if isComment:
                ret += '#'
            if parent == '':
                ret += '%s, %s, , , ' % (src, module) + os.linesep
            else:
                ret += '%s, %s, %s>%s, , ' % (src, module, module, parent) + os.linesep
            
    os.chdir(cwd)
    open('quickx.ini', 'wb').write(ret)

if __name__ == '__main__':
    main()
