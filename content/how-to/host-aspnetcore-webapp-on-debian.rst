在 DEBIAN 11 上安装 dotnet core 并启用 Serenity
##################################################

:date: 2022-05-02 21:24
:modified: 2022-05-02 21:24
:tags: serenity, asp.net core, dotnet core

本配置在 debian 11 下测试通过，默认环境为全新安装，仅安装 SSH，
创建了一个普通用户 recozo，该用户开启 sudo 功能。

参见：

* https://docs.microsoft.com/en-us/troubleshoot/developer/webapps/aspnetcore/practice-troubleshoot-linux/introduction
* https://docs.microsoft.com/en-us/aspnet/core/host-and-deploy/linux-nginx?view=aspnetcore-6.0

一、安装 DOTNET
--------------------------------------------------

使用以下命令安装 dotnet sdk ::
    
    $ sudo apt intalll wget
    $ wget https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
    $ sudo dpkg -i packages-microsoft-prod.deb
    $ rm packages-microsoft-prod.deb
    $ sudo apt update
    $ sudo apt install -y apt-transport-https
    $ sudo apt install -y dotnet-sdk-6.0
    # 由于目前 serenity 还是使用 aspnetcore 5，暂时还要安装这个
    $ sudo apt install -y aspnetcore-runtime-5.0
    $ dotnet --list-sdks
    $ dotnet --list-runtimes

二、创建测试网站（参照）
--------------------------------------------------

创建一个 aspnetcore 网站 ::
    
    $ dotnet new globaljson -o MySolution/MyProject
    $ dotnet new web -o MySolution/MyProject/
    $ dotnet new sln -o MySolution/
    $ dotnet sln MySolution add MySolution/MyProject
    $ cd MySolution/
    # 以下二条语句怎么不能成功执行了，好像成功执行过的
    $ dotnet run
    $ dotnet run --urls="http://0.0.0.0:5001"
    # 现在要求必须指定项目
    $ dotnet run --project MyProject --urls="http://0.0.0.0:5000;https://0.0.0.0:5001"

生成网站发布代码，一般会将网站代码部署在 /var/www 目录下 ::

    $ dotnet publish --configuration Release
    $ dotnet MyProject/bin/Release/net6.0/publish/MyProject.dll
    $ sudo cp -a ~/MySolution/MyProject/bin/Release/net6.0/publish/ /var/www/web02.rcz.cn/

在实际操作中发现一下问题，就是上面第二句 dotnet MyProject/bin/Release/net6.0/publish/MyProject.dll
，如果是 serenity ，由于默认要读取当前目录下的配置文件，但是由于运行时所在目录与工作目录不一致时，导致出错。
怎么解决？？？ TODO...

三、自动运行网站 ::
--------------------------------------------------

创建该网站 daemon ，以确保重启服务器或出错后能够自动运行网站 ::
    
    $ sudo vi /etc/systemd/system/web02.rcz.cn.service
    $ sudo systemctl enable web02.rcz.cn.service
    $ sudo systemctl start web02.rcz.cn.service
    $ systemctl status web02.rcz.cn.service

web02.rcz.cn.server 代码 ::

    [Unit]
    Description=web02.rcz.cn is a demo website template

    [Service]
    WorkingDirectory=/var/www/web02.rcz.cn/
    ExecStart=/usr/bin/dotnet /var/www/web02.rcz.cn/MyProject.dll
    Restart=always
    # Restart service after 10 seconds if the dotnet service crashes:
    RestartSec=10
    KillSignal=SIGINT
    SyslogIdentifier=web02.rcz.cn-identifier
    User=www-data
    Environment=ASPNETCORE_ENVIRONMENT=Development
    Environment=DOTNET_PRINT_TELEMETRY_MESSAGE=false
    Environment=ASPNETCORE_URLS=http://localhost:5001

    [Install]
    WantedBy=multi-user.target

请根据实际情况修改，默认 aspnetcore 网站分别使用 5000 和 5001 作为网站的 http 与 https 访问端口，
如果要运行多个网站时，可以通过指定 ASPNETCORE_URLS 指定端口。由于我们使用 nginx 反向代理，
不需要 https 。

四、启用 nginx
--------------------------------------------------

使用以下命令安装 nginx ::
    
    $ sudo apt install nginx
    $ systemctl status nginx

启用网站的反向代理 ::
    
    $ sudo vi /etc/nginx/sites-available/web02.rcz.cn
    $ sudo ln -s /etc/nginx/sites-available/web02.rcz.cn /etc/nginx/sites-enabled
    $ sudo nginx -T
    $ sudo nginx -s reload

注意：创建软链接时，必须使用完整路径； nginx 必须进行重新载入才能生效网站配置

五、对网站启用 HTTPS
--------------------------------------------------

使用以下命令安装 certbot ::

    $ sudo apt install snapd
    $ sudo snap install core; sudo snap refresh core
    $ sudo snap install --classic certbot
    # 以下软链接是否有必要，退出再登录后，发现路径中已经加入了 /snap/bin
    $ sudo ln -s /snap/bin/certbot /usr/bin/certbot

使用以下命令获取证书并自动网站配置（需要事先进行域名配置，防火墙上进行公网 IP 与内网服务器 IP 的映射，
简单来说，就要保证能事先通过域名以 HTTP 方式访问网站） ::
    
    $ sudo certbot --nginx
    $ cat /etc/nginx/sites-enabled/web02.rcz.cn

六、常用故障检测命令
--------------------------------------------------

 ::

    $ sudo journalctl -fu web02.rcz.cn.service
    $ sudo ss -tulp
    $ sudo vi /var/log/nginx/error.log

七、在 Debian 环境下运行 serenity 网站
--------------------------------------------------

* https://serenity.is/docs/postgresql

1、安装并配置 postgresql 数据库，参见 POSTGRESQL 学习。
以下假设数据库为 demo_db ，角色密码分别为 demo_role 和 demo_password；

2、修改项目文件以启用 postgresql。
在项目中使用 NUGET， Registering Npgsql Provider；
修改项目文件， Open the Startup.cs file under /Initialization/ and 
register PostgreSQL DbProviderFactory；
修改数据库连接串， 即在 .Net Core appsettings.json 中，Setting Connection Strings；
修改完成后，测试运行。

3、在 visual studio 2022 中生成发布代码并上传至网站服务器的 /var/www/demo_serenity.rcz.cn；

4、参照以上步骤设置网站域名、自动重启、反射代理以及数字证书等。

