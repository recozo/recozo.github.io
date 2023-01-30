自动挂机学习
##################################################

:date: 2020-09-01 00:16
:modified: 2020-10-04 13:07
:tags: chrome, chromedriver, selenium

#. 下载 `Chrome`__ 以及 `ChromeDriver`__ 并安装，注意 Chrome 与 ChromeDriver 的版本要相互支持

   __ https://www.google.com/chrome/
   __ https://chromedriver.chromium.org/downloads

   ::

    $ cd ~/Downloads
    $ sudo apt install ./google-chrome-stable_current_amd64.deb
    $ unzip chromedriver_linux64.zip

#. 安装学习强国学习辅助程序源码 ::

    $ cd Documents/
    $ git clone https://github.com/TechXueXi/TechXueXi.git

#. 安装辅助功能 ::

    $ sudo apt install python3-venv
    $ cd ~/Documents/TechXueXi/SourcePackages
    $ python3 -m venv .venv

    $ source .venv/bin/activate
    $ pip install requests
    $ pip install selenium
    $ cp ~/Downloads/chromedriver ~/Documents/TechXueXi/SourcePackages/

#. 运行辅助学习程序 ::

    $ cd ~/Documents/TechXueXi/SourcePackages
    $ source .venv/bin/activate

    $ python pandalearning.py 

   如果是因为缺少模块而报错，直接使用 pip install 模块名 即可解决。

#. 后续更新操作 ::

    $ cd ~/Documents/TechXueXi
    $ git pull
    
