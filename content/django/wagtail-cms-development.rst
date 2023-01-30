基于 wagtail 创建网站应用
##################################################

:date: 2020-10-03 14:12
:modified: 2022-04-03 14:12
:tags: wagtail, django, postgresql, git

参考链接

* https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-debian-10
* https://www.digitalocean.com/community/tutorials/how-to-set-up-a-scalable-django-app-with-digitalocean-managed-databases-and-spaces

系统运行环境配置
--------------------------------------------------

设置开发与运行环境，默认环境为全新安装，仅安装 SSH 和 基础工具软件，
创建了一个普通用户 recozo，为该用户开启 sudo 功能。

#. 以 root 用户安装 sudo ::

    # apt install sudo
    # adduser recozo sudo

#. 以 recozo 用户登录
#. 安装 postgresql数据库 ::

	$ sudo apt install postgresql postgresql-client curl nginx

   切换至 postgres 用户 ::

    $ sudo -i -u postgres
    $ psql

   通过 psql 创建数据库角色与数据库 ::

	>> CREATE ROLE mywagtail_admin LOGIN PASSWORD 'password';
	>> CREATE DATABASE mywagtail WITH owner = mywagtail_admin;

	退出 postgres 用户，回到 recozo 用户环境

* 安装用于支持 pillow 图片处理的库 ::

    $ sudo apt install libjpeg-dev zlib1g-dev

* 安装用于支持PYTHON虚拟环境的库 ::

    $ sudo apt install python3-venv

二、新建一个 wagtail 网站程序
--------------------------------------------------

初始化网站程序 ::

	$ mkdir ~/mywagtail && cd ~/mywagtail

	$ python3 -m venv .venv
	$ source .venv/bin/activate
	$ pip install wheel wagtail wagtail-2fa gunicorn psycopg2-binary

	$ wagtail start project .
	$ vi project/settings/base.py

使用以下内容更新 base.py 内容 ::

	# 修改并使用POSTGRESQL数据库
	DATABASES = {
	    'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': 'mywagtail',
		'USER': 'mywagtail_admin',
		'PASSWORD': 'password',
		'HOST': '127.0.0.1',
		'PORT': '5432',
	    }
	}

	# 启用双因子验证
	# 用户可安装 microsoft autherticator
	# 当用户首次登录后，会弹出二维码扫描，使用microsoft autherticator绑定设备
	# 以后每次登录成功后都要到 microsoft autherticator 获取 OTP 并正确输入后才能成功登录
	# https://wagtail-2fa.readthedocs.io/en/latest/
	INSTALLED_APPS = [
	    # ...
	    'wagtail_2fa',
	    'django_otp',
	    'django_otp.plugins.otp_totp',
	    # ...
	]
	MIDDLEWARE = [
	    # .. other middleware
	    # 'django.contrib.auth.middleware.AuthenticationMiddleware',

	    'wagtail_2fa.middleware.VerifyUserMiddleware',

	    # 'wagtail.core.middleware.SiteMiddleware',
	    # .. other middleware
	]
	WAGTAIL_2FA_REQUIRED = True
	# 启用双因子验证

	# 修改并设置中文及时区
	LANGUAGE_CODE = 'zh-hans'
	TIME_ZONE = 'Asia/Shanghai

** 注意 **

To avoid possible confusion as to effective scope, in django 4.0 the private internal 
utility is_safe_url() is renamed to url_has_allowed_host_and_scheme().

在 wagtail-2fa 中使用了 is_safe_url，暂时解决方案如下 ::

	$ vi .venv/lib/python3.9/site-packages/wagtail_2fa/views.py
	from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url

** 注意 **

执行以下命令分别生成数据库，网站管理员以及启动网站测试 ::

	$ python manage.py migrate
	$ python manage.py createsuperuser
	$ python manage.py runserver

记得在正式发布时，必须在生产机上运行 python manage.py collectstatic

利用 GITHUB 分发现有程序
--------------------------------------------------

#.	克隆现有程序 ::

	    $ git clone https://github.com/recozo/mywagtail.git recozo_com

#.	还原应用程序运行环境 ::

		$ cd recozo_com
		$ python3 -m venv .venv
		$ pip install -r requirements.txt
		$ vi project/settings/base.py

#. 修改 base.py 使用对应的 POSTGRESQL 数据库 ::

	DATABASES = {
	    'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': 'mywagtail',
		'USER': 'mywagtail_admin',
		'PASSWORD': 'password',
		'HOST': '127.0.0.1',
		'PORT': '5432',
	    }
	}

#.	继续还原参数配置 ::

	    $ vi project/settings/production.py

#.	修改 production.py 使用正确的域名以及模板目录名	::

		ALLOWED_HOSTS = ['recozo.com']
		RCZ_TEMPLATE_ACTIVE_DIR = 'recozo_com'

#.	基于该现有 wagtail 程序创建一个新的网站

	#.	统一为模板指定模板活动目录的变量（在 project/context_processors.py中设置）
	#.	在 project/settings/dev.py中设置RCZ_TEMPLATE_ACTIVE_DIR
		（该目录统一设置在 home 的templates目录下，注意，如果正式发布，请在production.py中进行相同设置）
	#.	版面模板及相关的CSS和JS均保存在home目录下，参见 recozo_com 的实现

#.	根据实际选择执行以下命令 ::

		$ python manage.py migrate
		$ python manage.py createsuperuser
		$ python manage.py collectstatic
		$ python manage.py runserver

通过 nginx 发布网站
--------------------------------------------------

创建 systemd socket 文件 ::

	$ sudo vi /etc/systemd/system/gunicorn.recozo_com.socket

将以下内容写入 socket 文件 ::

	[Unit]
	Description=gunicorn recozo_com socket

	[Socket]
	ListenStream=/run/gunicorn.recozo_com.sock

	[Install]
	WantedBy=sockets.target

创建 systemd 服务文件 ::

	$ sudo vi /etc/systemd/system/gunicorn.recozo_com.service

将以下内容写入 service 文件 ::

	[Unit]
	Description=gunicorn daemon
	Requires=gunicorn.recozo_com.socket
	After=network.target

	[Service]
	User=recozo
	Group=www-data
	WorkingDirectory=/home/recozo/recozo_com
	ExecStart=/home/recozo/recozo_com/.venv/bin/gunicorn \
			--access-logfile - \
			--workers 3 \
			--bind unix:/run/gunicorn.recozo_com.sock \
			project.wsgi:application

	[Install]
	WantedBy=multi-user.target

启用 socket 与 service ::

	$ sudo systemctl start gunicorn.recozo_com.socket
	$ sudo systemctl enable gunicorn.recozo_com.socket

检查 socket 文件与激活 ::

	$ sudo systemctl status gunicorn.recozo_com.socket
	$ file /run/gunicorn.recozo_com.sock
	$ sudo journalctl -u gunicorn.recozo_com.socket

	$ sudo systemctl status gunicorn.recozo_com.service
	$ curl --unix-socket /run/gunicorn.recozo_com.sock 10.62.1.132
	$ sudo systemctl status gunicorn.recozo_com.service
	$ sudo journalctl -u gunicorn.recozo_com.service

如果修改了/etc/systemd/system/gunicorn.recozo_com.service ::

	$ sudo systemctl daemon-reload
	$ sudo systemctl restart gunicorn.recozo_com.service

配置 nginx 代理 gunicorn ::

	$ sudo vi /etc/nginx/sites-available/recozo_com

使用以下内容更新站点配置文件 ::

	server {
		listen 80;
		server_name jw.luxi.gov.cn or 10.62.1.132;

		# 增加上传文件的最大限制为10M，为防范DOS，默认只有1M
    	client_max_body_size 10M;

		location = /favicon.ico { access_log off; log_not_found off; }
		location /static/ {
			root /home/recozo/recozo_com;
		}
		location /media/ {
			root /home/recozo/recozo_com;
		}

		location / {
			include proxy_params;
			proxy_pass http://unix:/run/gunicorn.recozo_com.sock;
		}
	}

启用 nginx 网站 ::

	$ sudo ln -s /etc/nginx/sites-available/recozo_com /etc/nginx/sites-enabled
	$ sudo nginx -t
	$ sudo systemctl restart nginx

参考资料
--------------------------------------------------

#. 	分类功能

	参见：https://posts-by.lb.ee/building-a-configurable-taxonomy-in-wagtail-django-94ca1080fb28

	源码：https://gist.github.com/lb-/fda43b343cbf24c44c2c74ec69f2eafd#file-final_models-py


#.	翻译功能

	https://docs.wagtail.io/en/v2.9/advanced_topics/customisation/admin_templates.html

	目前 wagtail 好像只支持对本身提供的管理后台本地化，
	即只能对 .venv/lib/python3.7/site-packages/wagtail/admin/locale/zh_Hans/LC_MESSAGES/django.po 
	这个文件进行本地化，比如 wagtail_2fa 这个模块要进行中文处理，只能将其 PO 文件内容复制到 wagtail 的django.po 文件中去
	不知道是不是我还没有找到正确的实现办法
	
	更新 po 文件后，使用 django-admin compilemessages 生成 mo 文件即可。

#.	注意事项

	由于中文翻译，导致 truncatechars 后边未带...，
	请自行修改中文 .venv/lib/python3.7/site-packages/wagtail/admin/locale/zh_Hans/LC_MESSAGES/django.po 文件中的
	msgctxt "String to return when truncating text"，
	
	然后执行 django-admin compilemessages 生成 mo 文件即可

