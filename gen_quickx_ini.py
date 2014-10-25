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
    
    #不处理的文件
    comments = ['.\\init.lua', 
                '.\\cc\\init.lua', 
                '.\\cc\\mvc\\init.lua', 
                '.\\cc\\net\\init.lua', 
                '.\\cc\\ui\\init.lua', 
                '.\\cc\\uiloader\\CCSSceneLoader.lua', 
                '.\\cc\\uiloader\\CCSUILoader.lua', 
                '.\\cc\\uiloader\\UILoaderUtilitys.lua', 
                '.\\cc\\utils\\init.lua', 
                '.\\deprecated\\deprecated_functions.lua', 
                '.\\platform\\android.lua', 
                '.\\platform\\ios.lua', 
                '.\\platform\\mac.lua'
                ]
    
    #特别处理的文件
    specails = {
        # src : [vars, parents, supers, renames]
        '.\\functions.lua' : ['string', '', '', ''], 
        '.\\json.lua' : ['', '', '', ''], 
        '.\\shortcodes.lua' : ['', 'Node>cc|Sprite>cc|Layer>cc', '', ''], 
        '.\\cc\\components\\behavior\\EventProtocol.lua' : ['', 'EventProtocol>cc.components', 'EventProtocol>cc.components.Component', ''],
        '.\\cc\\components\\behavior\\StateMachine.lua' : ['', 'StateMachine>cc.components', 'StateMachine>cc.components.Component', ''],
        '.\\cc\\components\\ui\\BasicLayoutProtocol.lua' : ['', 'BasicLayoutProtocol>cc.components', 'BasicLayoutProtocol>cc.components.Component', ''], 
        '.\\cc\\components\\ui\\DraggableProtocol.lua' : ['', 'DraggableProtocol>cc.components', 'DraggableProtocol>cc.components.Component', ''],
        '.\\cc\\components\\ui\\LayoutProtocol.lua' : ['', 'LayoutProtocol>cc.components', 'DraggableProtocol>cc.components.BasicLayoutProtocol', ''],
        #'.\\cc\\net\\SocketTCP.lua' : ['', 'SocketTCP>cc.net', '', ''],
        '.\\cc\\sdk\\Store.lua' : ['', 'pay>cc.sdk', '', 'Store>pay'], 
        '.\\cc\\ui\\UIBoxLayout.lua' : ['UIBoxLayout', 'UIBoxLayout>cc.ui', 'UIBoxLayout>cc.ui.UILayout', ''], 
        '.\\cc\\ui\\UICheckBoxButton.lua' : ['UICheckBoxButton', 'UICheckBoxButton>cc.ui', 'UICheckBoxButton>cc.ui.UIButton', ''], 
        '.\\cc\\ui\\UICheckBoxButtonGroup.lua' : ['UICheckBoxButtonGroup', 'UICheckBoxButtonGroup>cc.ui', 'UICheckBoxButtonGroup>cc.ui.UIGroup', ''], 
        '.\\cc\\ui\\UIPushButton.lua' : ['UIPushButton', 'UIPushButton>cc.ui', 'UIPushButton>cc.ui.UIButton', ''], 
        '.\\cc\\uiloader\\init.lua' : ['uiloader', 'uiloader>cc', '', ''], 
        '.\\cc\\utils\\ByteArrayVarint.lua' : ['ByteArrayVarint', 'ByteArrayVarint>cc.utils', 'ByteArrayVarint>cc.utils.ByteArray', ''], 
        '.\\cocos2dx\\Cocos2d.lua' : ['cc', '', '', ''], 
        '.\\cocos2dx\\Cocos2dConstants.lua' : ['cc', '', '', ''], 
        '.\\cocos2dx\\DrawNodeEx.lua' : ['cc', 'DrawNode>cc', '', ''], 
        '.\\cocos2dx\\Event.lua' : ['c', '', '', 'c>cc'],
        '.\\cocos2dx\\NodeEx.lua' : ['c', 'Node>cc', '', 'c>cc'], 
        '.\\cocos2dx\\OpenglConstants.lua' : ['gl', '', '', ''], 
        '.\\cocos2dx\\SceneEx.lua' : ['c', 'Scene>cc', '', 'c>cc'], 
        '.\\cocos2dx\\SpriteEx.lua' : ['c', 'Sprite>cc', '', 'c>cc'], 
        '.\\cocos2dx\\StudioConstants.lua' : ['ccs', '', '', '']
    }

    cwd = os.getcwd()
    os.chdir(docluaDir)
    ret = '#luafile, vars, parent_module, super, renames' + os.linesep
    for root, dirs, files in os.walk('.'):
        for file in files:
            isComment = False
            src = os.path.join(root, file)
            basename = os.path.basename(src)
            
            #要忽略的文件
            if src in comments:
                isComment = True

            #特别处理的文件
            if src in specails:
                if isComment: ret += '#'
                srcv = specails[src]
                ret += '%s, %s, %s, %s, %s' % (src, srcv[0], srcv[1], srcv[2], srcv[3]) + os.linesep
            else:
                module = os.path.splitext(basename)[0]
                tmp = src.split(os.sep)
                if len(tmp) > 1:
                    parent = '.'.join(tmp[0:-1])
                    if parent == '.': parent = ''
                    else: parent = parent.strip('.')
                else:
                    parent = ''
                    
                if isComment: ret += '#'
                if parent == '':
                    ret += '%s, %s, , , ' % (src, module) + os.linesep
                else:
                    ret += '%s, %s, %s>%s, , ' % (src, module, module, parent) + os.linesep
            
    os.chdir(cwd)
    open('quickx.ini', 'wb').write(ret)

if __name__ == '__main__':
    main()
