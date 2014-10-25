quickx-ee
=========

推荐使用LuaDevelopmentTools(LDT)来开发quickx项目，它能够语法高亮、调试quickx项目。

LDT的自动完成功能比较弱，而quickx-ee的作用是生成带lua5.1/cocos2dx3.2/quickx3.2自动完成的LDT Execution Environment(ee)。

quickx-ee很好的实现了lua5.1/cocos2dx3.2/quickx3.2的函数及变量的自动完成，还包括基类的函数和变量


快速使用
--------
quickx-ee.zip是生成好的ee文件，按一下步骤加入到LDT中:

    1、Windows->Preferences->Lua->Execution Environment->Add...，选中quickx-ee.zip，这样就加入了我们的ee了
    2、在创建lua项目时，在Targeted Execution Environment里选择我们刚加入的ee，名字为quickx3.2-lua5.1...


老项目如何改用quickx-ee
-----------------------
    1、Project->Properties->Lua->Build Path
    2、在Build Path对话框中选择Libraries，先删除原来的ee，一般是lua-5.1
    3、再加入quickx-ee，点击Add Library...，选择Lua Execution Environment，再选择quickx-ee

如何生成新的quickx-ee
---------------------
    1、需安装python2.7
    2、下载cocos2dx3.2的代码并解压
    3、在系统环境变量中配置COCOS2DX_ROOT，指向上面解压的cocos2dx目录，例如d:\cocos\cocos2d-x-3.2\
    4、在系统环境变量中配置QUICK_COCOS2DX_ROOT，指向quickx的根目录，例如：d:\cocos\quick-cocos2d-x-3.2rc1\
    5、执行python gen_quickx_ee.py即生成quickx-ee.zip
    
注意：quickx3.2目录下虽然有cocos2dx的部分源码，但缺少cocos\scripting\lua-bindings\auto\api\下生成的lua文件，所以才有上面的第2、3步
