使用 Pelican 维护静态网站
##################################################

:date: 2020-02-03 13:49
:modified: 2020-08-28 00:49
:tags: pelican, git, github, vscode
:slug: install-pelican-on-debian

Pelican 是一个使用Python编写开发的静态网站静态网站内容生成器。
其实在 github 上有官方推荐的静态网站内容生成器，但是基于以下原因还是选择了 Pelican

* 支持 reStructuredText 编写内容
* 使用 Python 开发
* 打算转向 Python 进行程序开发，好吧，这理由有点勉强……

安装系统，可参照安装远程开发桌面环境
==================================================

记得执行以下命令设置git用户信息::

    $ sudo apt install git
    $ git config --global user.email "recozo@outlook.com"
    $ git config --global user.name "Recozo"

安装 PELICAN
==================================================

输入以下命令安装pelican并设置相关的运行环境::

    $ cd ~/Documents
    $ mkdir mysite && cd mysite
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install pelican python-magic wheel ghp-import sphinx sphinx-autobuild rstcheck
    $ pip freeze | grep pelican > requirements.txt
    $ pip freeze | grep python-magic > requirements.txt
    $ pip freeze | grep ghp-import >> requirements.txt
    $ pip freeze | grep sphinx >> requirements.txt
    $ pip freeze | grep sphinx-autobuild >> requirements.txt
    $ pip freeze | grep rstcheck >> requirements.txt
    $ pelican-quickstart
    $ touch README.rst    
    $ vi .gitignore

参照 https://github.com/github/gitignore/blob/master/Python.gitignore
以及以下内容录入 .gitignore 内容 ::

    #pelican
    output/

继续执行以下命令 ::

    $ git init
    $ git add -A
    $ git commit -a -m 'Initial commit'

发布第一篇文章
==================================================

# 在 content 目录中保存文章::

    vi content/welcome-to-my-blog.rst

示例::

    Welcome to my blog !
    ####################

    :date: 2020-08-28 01:30
    :modified: 2020-08-29 10:15
    :tags: essay
    :category: article

    Hello, welcome to my first blog !

保存文件。

查看当前所有配置
==================================================

使用以下命令可以查看当前的所有配置（包括默认配置）::

    $ pelican --print-settings

使用主题
==================================================

在社区管理维护的 `Pelican Themes <https://github.com/getpelican/pelican-themes>`_ 中，
有多个主题可供使用，目前我们使用的是 Flex 。
尽管可以直接通过 Pelican Themes 安装并使用主题，但是更新有所滞后，
所以我们还是直接克隆 Flex 的 github 库（在我们自己的 Fork）。

#.  下载主题

    .. code-block:: bash

       $ cd ~/Documents
       $ git clone https://github.com/recozo/Flex.git

#.  安装主题

    .. code-block:: bash

        $ pelican-themes --install ~/Documents/Flex --verbose
        $ pelican-themes --list

#.  使用主题，可以通过 pelican content -t your-theme-path 
    也可以通过在配置文件中定义 THEME 启用主题

    .. code-block:: python

        # pelicanconf.py
        THEME = './.venv/lib/python3.10/site-packages/pelican/themes/Flex'


链接到内部内容
==================================================

内部内容指保存在 content 目录中的文件（如图片、PDF等）

#. 使用 filename

    `a link relative to the current image file <{filename}../images/test01.jpeg>`_
    `a link relative to the current pdf file <{filename}../pdfs/PythonTestingWithSelenium.pdf>`_

#. 使用 static，此时即使指定的文件所在目录不在 STATIC_PATHS 中，
   该文件（及目录）也会被复制到 output 目录中 

    `a link static to the current image file <{static}../images/test01.jpeg>`_
    `a link static to the current pdf file <{static}../pdfs/PythonTestingWithSelenium.pdf>`_

启用 restructuredtext 扩展
==================================================

安装 reStructuredText 扩展后， `请查看使用该扩展前的前置依赖 <https://docs.restructuredtext.net/articles/prerequisites>`_

第一次使用时，可使用 sphinx-quickstart 创建相关配置。

查看网站效果以及内容
==================================================

运行以下命令生成网站内容（网站内容有更新时自动重新生成，忽略缓存以避免更新内容不显示）::

    $ pelican --autoreload --listen --ignore-cache

在浏览器中访问以下地址可检查网站效果::

    http://localhost:8000

可以开几个终端，编辑信息，然后在浏览器中查看编辑后的效果

使用 GITHUB 发布网站以及源文件
==================================================

#. 在 github.com 创建项目 recozo.github.io，将本地与项目进行绑定::

    $ git remote add origin https://github.com/recozo/recozo.github.io.git

#. 将源文件保存为 pelican 分支::

    $ git push -u origin master:pelican

#. 发布项目网站(https://recozo.github.io)内容::

    $ pelican content/ -o output -s publishconf.py 
    $ ghp-import output -b gh-pages
    $ git push origin gh-pages:master

使用 GIT 在本地还原 recozo.github.io 项目
==================================================

::

    $ cd ~/Documents
    $ git clone https://github.com/recozo/recozo.github.io.git pelican
    $ cd pelican/
    $ git branch -m master
    $ git fetch origin master:gh-pages
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt

利用 GIT 恢复或撤销操作
==================================================

如果需要恢复或撤销已经提交了的操作

*   git reset --soft HEAD~
    把该分支移动回原来的位置，而不会改变索引和工作目录
*   git reset [--mixed] HEAD~
    撤销一上次的提交，还会取消暂存区所有的东西
*   git reset --hard HEAD~
    撤销了最后的提交、git add 和 git commit 命令 以及 工作目录中的所有工作

如果需要同时撤销已经发布到GITHUB的操作 ::

    # 查看提交的日志（版本）
    git log
    # 本地仓库回退到某一版本
    git reset --hard xxxx
    # 强制 PUSH，此时远程分支已经恢复成指定的 commit 了
    git push origin master --force

关于浏览器缓冲的问题
==================================================

将 Pelican 从 4.2 升级到了 4.5 ，当访问 http://127.0.0.1:8000 时，
总是不能打开 index.html，每次都弹出下载界面，无论是 Firefox 还是 Chrome，都这毛病，以为是升级的原因，
重新弄了台虚拟机，重新安装还是出这个问题，浪费了二天的时间找原因（不过也不是完全浪费，学到了如何 DEBUG），
最后发现是浏览器缓存导致的问题，删除缓存后能正常访问，但是由于缓存功能没有关闭，后续仍然会出问题。

不建议停用浏览器的缓存功能， Firefox 支持启用开发者模式时禁用 HTTP 缓存 （F12 进入开发者模式，
F1 进入设置即可在 Advanced settings 看到这个选项 Disable HTTP Cache(when toolbox is open)），
爽不？！

注意，要安装 python-magic ，在 pelican 的 server.py 的 guess_type 是通过 python-magic 进行处理的，
如果未安装，即仍然会弹出下载界面。 

在 VSCODE 中调试 Pelican
==================================================

在 .vscode 目录下新建一个 launch.json 文件，录入以下内容，即可在 VSCODE 中对 Pelican 进行断点调试了::

    {
        // Use IntelliSense to learn about possible attributes.
        // Hover to view descriptions of existing attributes.
        // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
        "version": "0.2.0",
        "configurations": [
            
            {
                "name": "Python: Module",
                "type": "python",
                "request": "launch",
                "module": "pelican",
                "args":["--listen"],
                "justMyCode": false,
            }
        ]
    }