Install pelican on Debian 10
############################

:tags: pelican, git, virtualenv, github
:category: how-to
:slug: install-pelican-on-debian
:summary: Getting setup a static web site with pelican, publishing on the github page

本文假定系统为全新安装的 DEBIAN 10

一、安装 GIT
------------

执行以下命令安装git并设置git基本配置::

    $ sudo apt install git
    $ git config --global user.email = "recozo@outlook.com"
    $ git config --global user.name = "Recozo"

二、安装 VIRTUALENV
-------------------

执行以下命令安装virtualenv并设置git忽略设置::

    $ sudo apt install virtualenv
    $ vi ~/.gitingore
        参照 https://github.com/github/gitignore/blob/master/Global/VirtualEnv.gitignore
    $ git config --global core.excludesfile '~/.gitignore'

三、安装 PELICAN
----------------

输入以下命令安装pelican并设置相关的运行环境::

    $ virtualenv -p /usr/bin/python3 ~/venvs/pelican
    $ cd ~/venvs/pelican
    $ source bin/activate
    $ git init
    $ touch README.md
    $ vi .gitignore
        参照 https://github.com/github/gitignore/blob/master/Python.gitignore
        加入以下内容：
      	    #pelican
	    output/
    $ pip install pelican ghp-import
    $ pip freeze | grep pelican > requirements.txt
    $ pip freeze | grep ghp-import >> requirements.txt
    $ git add README.md .gitignore requirements.txt
    $ git commit -a -m 'Initial commit'
    $ pelican-quickstart

四、发布第一篇文章
------------------

# 在 content 目录中保存文章::

    vi content/welcome-to-my-blog.rst

示例::

    Welcome to my blog !
    ####################

    :tags: essay
    :category: article
    :slug: welcome-to-my-blog
    :authors: Recozo

    Hello, welcome to my first blog !

保存文件后，运行以下命令生成网站内容::

    $ pelican --autoreload --listen

在浏览器中访问以下地址可检查网站效果::

    http://localhost:8000

五、使用 GITHUB 发布网站以及源文件
----------------------------------

# 在 github.com 创建项目 recozo.github.io，将本地与项目进行绑定::

    $ git remote add origin https://github.com/recozo/recozo.github.io.git

# 将源文件保存为 pelican 分支::

    $ git push -u origin master:pelican

# 发布项目网站(https://recozo.github.io)内容::

    $ pelican content/ -o output -s publishconf.py 
    $ ghp-import output -b gh-pages
    $ git push origin gh-pages:master
