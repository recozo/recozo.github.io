使用 Pelican 维护静态网站
##################################################

:date: 2020-02-03 13:49
:modified: 2020-08-28 00:49
:tags: pelican, git, github, vscode

Pelican 是一个使用Python编写开发的静态网站静态网站内容生成器。
其实在 github 上有官方推荐的静态网站内容生成器，但是基于以下原因还是选择了 Pelican

* 支持 reStructuredText 编写内容
* 使用 Python 开发
* 打算转向 Python 进行程序开发，好吧，这理由有点勉强……

一、安装系统，可参照安装远程开发桌面环境
--------------------------------------------------

记得执行以下命令设置git用户信息::

    $ sudo apt install git
    $ git config --global user.email "recozo@outlook.com"
    $ git config --global user.name "Recozo"

二、安装 PELICAN
--------------------------------------------------

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
        加入以下内容：
      	    #pelican
	        output/

            #vscode
            .vscode/

    $ git init
    $ git add -A
    $ git commit -a -m 'Initial commit'

三、发布第一篇文章
--------------------------------------------------

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

四、查看网站效果以及内容
-------------------------------------

运行以下命令生成网站内容（网站内容有更新时自动重新生成，忽略缓存以避免更新内容不显示）::

    $ pelican --autoreload --listen --ignore-cache

在浏览器中访问以下地址可检查网站效果::

    http://localhost:8000

可以开几个终端，编辑信息，然后在浏览器中查看编辑后的效果

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

六、使用 GIT 还原
----------------------------------
::

    $ cd ~/Documents
    $ git clone https://github.com/recozo/recozo.github.io.git pelican
    $ cd pelican/
    $ git branch -m master
    $ git fetch origin master:gh-pages
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt

七、关于浏览器缓冲的问题
--------------------------------------------------

将 Pelican 从 4.2 升级到了 4.5 ，当访问 http://127.0.0.1:8000 时，
总是不能打开 index.html，每次都弹出下载界面，无论是 Firefox 还是 Chrome，都这毛病，以为是升级的原因，
重新弄了台虚拟机，重新安装还是出这个问题，浪费了二天的时间找原因（不过也不是完全浪费，学到了如何 DEBUG），
最后发现是浏览器缓存导致的问题，删除缓存后能正常访问，但是由于缓存功能没有关闭，后续仍然会出问题。

不建议停用浏览器的缓存功能， Firefox 支持启用开发者模式时禁用 HTTP 缓存 （F12 进入开发者模式，
F1 进入设置即可在 Advanced settings 看到这个选项 Disable HTTP Cache(when toolbox is open)），
爽不？！

注意，要安装 python-magic ，在 pelican 的 server.py 的 guess_type 是通过 python-magic 进行处理的，
如果未安装，即仍然会弹出下载界面。 

八、在 VSCODE 中调试 Pelican
--------------------------------------------------

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