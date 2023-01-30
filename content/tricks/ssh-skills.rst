SSH 使用说明
####################

:tags: ssh
:category: how-to
:slug: ssh-skills
:authors: Recozo

安装 SSH
==================================================

检查 SSH 是否安装::

    $ apt list --installed | grep ssh
    ## 如果没有安装
    $ sudo apt install openssh-client

如果已经安装，是否需要重新生成 SSH 服务器端钥匙？
如是批安装，或者复制的虚拟机等……
通过以下命令重新生成 SSH 服务端钥匙::

    $ cd /etc/ssh/
    $ sudo mkdir old_keys
    $ sudo mv ssh_host_* old_keys/
    $ sudo dpkg-reconfigure openssh-server
    $ sudo systemctl restart ssh.service

以上重新生成钥匙的操作不会中断当前的 SSH 会话，也就是说可以通过远程 SSH 会话对服务端钥匙重新进行配置。

重新生成 SSH 服务端钥匙后需要更新客户端的 known_hosts 文件::

    ## 在原来访问过该 SSH 服务的客户端上执行
    ## 执行 ssh username@remote-server-name 查看错误提示
    $ ssh-keygen -R "remote-server-name-here"

`直接查看实际配置文件 <autossh systemd service_>`_

SSH 桌面转发（X Forwarding）
==================================================

要使用桌面转发，SSH 服务器端必须安装 xauth(1) 应用程序（在国产系统中，如银河麒麟 v10，默认没有安装）。如果该应用程序存在，则只需要在 sshd_config 启用桌面转发::

    X11Forwarding yes

在 SSH 客户端也可以通过在 ssh_config 中进行设置以使用桌面转发，不过使用命令行直接使用桌面转发更安全与更快捷::

    ssh -CX server          # C压缩传输，X启用桌面转发，进入后，运行桌面程序时，桌面会转发至本机显示
    ssh -CY server          # C压缩传输，Y启用桌面转发，与X相比，Y对桌面程序更信任，授权给多，正常用X即可
    ssh -f server command   # 直接执行命令，此时 ssh 在后台运行，返回命令提示符，并在远程服务器执行命令(命令也可以是桌面程序)

SSH（隧道）端口转发
==================================================

#. 本地端口转发，常用于将不安全地协议进行加密通讯::

    ssh -L localIP:localport:remoteIP:remoteport hostname

    # 也可以省略 localIP 此时默认使用客户端的 127.0.0.1 地址
    ssh -L localport:remoteIP:remoteport hostname

    # 考虑安全，远程服务器地址也应该为 127.0.0.1，因为该回调地址仅本机可访问
    ssh -L 8080:127.0.0.1:80 serverNameOrIP

    如以上最后一条命令，通过访问本机的8080端口，即可以访问远程服务器的80端口，将原来未加密传输的网站内容通过 SSH 进行加密。

#. 远程端口转发，常用于访问防火墙之后的服务::

    ssh -R remoteIP:remoteport:localIP:localport hostname

    # 也可以省略 remoteIP 此时默认使用远程服务器端的 127.0.0.1 地址
    ssh -R remoteport:localIP:localport hostname

    # 考虑安全，本地客户端地址也应该为 127.0.0.1 或 localhost，因为该回调地址仅本机可访问
    ssh -R 2222:localhost:22 serverNameOrIP

    如以上最后一条命令运行后，在 serverNameOrIP 上的用户，通过使用如下命令::

    serverNameOrIP $ ssh -p 2222 localhost

    即可越过防火墙限制，通过2222端口反过来访问本地客户端机器的服务，如 SSH 或 WEB，即借助现有的 SSH 连接创建了一个隧道以访问本地客户端机器的服务。

#. 动态端口转发，常用于SOCKS代理::

    ssh -D localaddress:localport hostname

    # 也可以省略 localaddress 此时默认使用 127.0.0.1 地址
    ssh -D 9999 hostname

    如以上最后一条命令运行后，你可以配置本机浏览器使用 127.0.0.1:9999 SOCKS 代理上网，此时将通过 SSH 服务器上网。

在后台使用转发功能::

    ssh -fNL 2222:localhost:22 hostname &

选项请自行使用 man 。

其它与转发有关的配置项有，在 sshd_config 中的 AllowTcpForwarding 可以控制是否允许端口转发，
在 ssh_config 和 sshd_config 中的 GatewayPorts 可决定是否允许除 127.0.0.1 的 IP 地址进行转发。

TLDR

端口转发主要用途：

Where local port forwarding is usually used to wrap a service with
encryption, remote port forwarding is used to access a service behind a
firewall

本地端口转发（正向代理）：相当于 iptable 的 port forwarding::

    ssh -L 5000:localhost:3306 remoteUser@remoteServer

远程端口转发（反向代理）：相当于 frp 或者 ngrok::

    ssh -R 5000:localhost:80 remoteUser@remoteServer

如要长期高效的服务，应使用对应的专用软件。如没法安装软件，比如当你处在限制环境下想要访问下某个不可达到的目标，或者某个临时需求，那么 ssh 就是你的兜底方案。

本地端口转发：
--------------------------------------------------

在本地启动端口，把本地端口数据转发到远程服务器，使得远程端口本地可以访问（如用于代理）::

    ssh -L [<LocalAddress>]:<LocalPort>:<RemoteHost>:<RemotePort> remoteUser@remoteServer

=============   ==========
参数            解释
=============   ==========
LocalAddress	可选参数，如果未指定，远程端口会绑定在本地的所有接口（0.0.0.0），因而也可以仅绑定到本地的 127.0.0.1
LocalPort	本地端口，该端口接收到的数据会转发至远程服务器进行处理
RemoteHost	远程服务器（remoteServer）上的守护进程所监听的接口，可以是 127.0.0.1，localhost，实际 IP 地址或者 0.0.0.0 （表示所有接口）。
		如果不确定 ，可以执行以下命令查看::

		    netstat -an | grep 3306 | grep LISTEN 

RemotePort	远程服务器（remoteServer）上的实际端口，与 RemoteHost 一起用于接收本地端口（LocalPort）转发的数据
remoteUser	远程服务器（remoteServer）上的 SSH 用户
remoteServer	远程服务器地址（IP或主机名）
=============   ==========

示例：通过本地端口 5000 远程访问 MySQL 服务器::

    ssh -L 5000:localhost:3306 sqlUser@MySQLServer
    ## 或者
    ssh -L 127.0.0.1:5000:localhost:3306 sqlUser@MySQLServer
    mysql --host=127.0.0.1 --port=5000

远程端口转发：
--------------------------------------------------

让远端服务器启动端口，把远端端口数据转发到本地，使得本地端口远程可以访问（如用于内网穿透）::

    ssh -R [<RemoteAddress>]:<RemotePort>:<LocalHost>:<LocalPort> remoteUser@remoteServer

=============   ==========
参数            解释
=============   ==========
RemoteAddress   可选参数，如果未指定，远程端口会绑定在远程服务器的所有接口（0.0.0.0，但是只会在 Loopback 接口上启用？），因而也可以仅绑定到特定的接口。
		注意：如果指定了 RemoteAddress ，必须启用远程服务器上的 GatewayPorts 选项::

		    $ vim /etc/ssh/sshd_config
		    GatewayPorts yes

RemotePort      远程服务器（remoteServer）上的实际端口，与 RemoteAddress 一起用于接收数据，接收到的数据会转发至本地进行处理
LocalHost       本地守护进程所监听的接口，可以是 127.0.0.1，localhost，实际 IP 地址或者 0.0.0.0 （表示所有接口）。
                如果不确定 ，可以执行以下命令查看::

                    netstat -an | grep 80 | grep LISTEN  

LocalPort       本地的实际端口，与 LocalHost 一起用于接收远程服务器转发过来的数据
remoteUser      远程服务器（remoteServer）上的 SSH 用户
remoteServer    远程服务器地址（IP或主机名）
=============   ==========

示例：通过远程服务器（公网地址：109.239.48.64）的端口 5000 访问本地的网站::

    ssh -R 5000:localhost:80 remoteUser@remoteServer
    ## 或者
    ssh -R 109.239.48.64:5000:localhost:80 remoteUser@remoteServer
    ## 通过浏览器访问以下地址即可访问本地的网站内容
    http://109.239.48.64:5000

使用1024以下端口需要 root 权限
--------------------------------------------------
所有系统用户都可以分配1024以上的端口号，但是1024（不含）需要 root 权限，
本地转发时，如果要分配1024以下的本地端口，你需要使用 root 用户或 sudo 执行::

    sudo ssh -L 50:localhost:3306 remoteUser@remoteServer

远程转发时，如果要分配1024以下的远程端口，你必须使用 root 用户进行 SSH 连接::

    ssh -R 50:localhost:80 root@remoteServer

使用优化（隧道选项）
==================================================

=============   ==========
常用参数           解释
=============   ==========
-N		After you connect just hang there (you won’t get a shell prompt)
		SSH man: Do not execute a remote command.
		Note: Only works with SSHv2
-T		Disable pseudo-terminal allocation.
		This makes it also safe for binary file transfer which might contain escape characters such as ~C.
-f		Requests ssh to go to background just before command execution.
-p		Port to connect to on the remote host.
-i		Selects a file from which the identity (private key) for public key authentication is read. 
=============   ==========

使用以上参数构建的命令如下::

    ssh -f -T -N -L 5000:localhost:3306 remoteUser@remoteServer -p 1022 -i ~/.ssh/id_rsa-remoteuser@remoteserver

如果不想每次输入这么长的命令，可以使用 ~/.ssh/config 。

添加用户与主机
--------------------------------------------------

::

    $ vim ~/.ssh/config
    Host cli
	HostName	remoteServer
	User          	remoteUser

以上为用户与主机创建了一个别名 cli，可以将命令简化为::

    ssh -f -T -N -L 5000:localhost:3306 cli -p 1022 -i ~/.ssh/id_rsa-remoteuser@remoteserver

添加端口和证书文件
--------------------------------------------------

::

    $ vim ~/.ssh/config
    Host cli
	HostName     	remoteServer
	User          	remoteUser
	Port		1022
	IdentityFile	~/.ssh/id_rsa-remoteuser@remoteserver

现在可以将命令简化为::

    ssh -f -T -N -L 5000:localhost:3306 cli

添加隧道配置
--------------------------------------------------

::

    $ vim ~/.ssh/config
    Host cli-mysql-tunnel
	HostName     	remoteServer
	User          	remoteUser
	Port		1022
	IdentityFile	~/.ssh/id_rsa-remoteuser@remoteserver
	LocalForward	5000 localhost:3306

.. _ssh by config:

现在可以将命令简化为::

    ssh -f -T -N cli-mysql-tunnel

对照 `autossh by config`_

使用 AUTOSSH
==================================================

SSH 没有断线重连功能，可以使用 autossh 自动重建会话或隧道。

TLDR ::

    autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -L 5000:localhost:3306 remoteUser@remoteServer

或者基于 ~/.ssh/config 配置在后台运行::

    autossh -M 0 -f -T -N cli-mysql-tunnel

安装 autossh
--------------------------------------------------
::

    sudo apt install autossh

用法
--------------------------------------------------
::

    autossh [-V] [-M monitor_port[:echo_port]] [-f] [SSH_OPTIONS]

    ## 如以上通过本地5000端口转发 MySQL
    ssh -L 5000:localhost:3306 sqlUser@MySQLServer
    ## 使用 autossh 命令
    autossh -L 5000:localhost:3306 sqlUser@MySQLServer

注意：

1. 使用 autossh 前，请使用 ssh 先进行操作并确保无误；
2. autossh 的 -f 选项不会传递至 ssh，因此必须使用公私钥匙进行认证，不支持基于密码或私钥密码认证。
#. 生成用户的 ssh 密钥，记得私钥不能启用私钥密码::

    ssh-keygen					# 生成 ssh 使用的密钥
    ssh-copy-id remoteUser@remoteServer		# 将公钥安装到远程服务器

autossh 的 -M 选项
--------------------------------------------------

Setting the monitor port to 0 turns the monitoring function off, 
and autossh will only restart ssh upon ssh's exit. 
For example, if you are using a recent version of OpenSSH, 
you may wish to explore using the ServerAliveInterval and ServerAliveCountMax options to have the SSH client exit 
if it finds itself no longer connected to the server. 
In many ways this may be a better solution than the monitoring port.

以上内容来自 man autossh。

因此推荐方式是::

    autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3"

=====================   ==========
选项                       解释
=====================	==========
ServerAliveInterval	Sets a timeout interval in seconds after which if no data has been received from the server, 
			ssh(1) will send a message through the encrypted channel to request a re‐ sponse from the server.  
			The default is 0, indicating that these messages will not be sent to the server.
ServerAliveCountMax	Sets the number of server alive messages which may be sent without ssh(1) receiving any messages back from the server.  
			If this threshold is reached while server alive messages are being sent, 
			ssh will disconnect from the server, terminating the session. 

			The default value is 3.  
			If, for example, ServerAliveInterval is set to 15 and ServerAliveCountMax is left at the default, 
			if the server becomes unresponsive, ssh will disconnect after approximately 45 seconds.
=====================   ==========

autossh 与 ~/.ssh/config
--------------------------------------------------

autossh 也支持 ~/.ssh/config，因此可以继续使用配置文件进行有关的设置，
继续以上面的配置文件为例，加入 ServerAliveInterval 和 ServerAliveCountMax 二个选项::

    $ vim ~/.ssh/config
    Host cli-mysql-tunnel
	HostName     	remoteServer
	User          	remoteUser
	Port		1022
	IdentityFile	~/.ssh/id_rsa-remoteuser@remoteserver
	LocalForward	5000 localhost:3306
	ServerAliveInterval	30
	ServerAliveCountMax	3

.. _autossh by config:

现在我们可以使用以下命令确保断线重连了::

    autossh -M 0 -f -T -N cli-mysql-tunnel

对照 `ssh by config`_ ,
注意 -f 不会传递给 ssh。

autossh 环境变量
--------------------------------------------------

autossh 也可以通过一些环境变量进行控制，其中比较重要的一个变量是 AUTOSSH_GATETIME:

AUTOSSH_GATETIME
    Specifies how long ssh must be up before we consider it a successful connection. 
    The default is 30 seconds. 
    Note that if AUTOSSH_GATETIME is set to 0, then not only is the gatetime behaviour turned off, 
    but autossh also ignores the first run failure of ssh. 
    This may be useful when running autossh at boot.

其它变量说明请自行参阅 man

autossh systemd service
--------------------------------------------------

可以通过 systemd 在启动时自动建立转发隧道，不过需要注意的是：
autossh -f 在 systemd 环境下不受支持。

* 客户端

    1. 客户端的 systemd 配置::
    
	# apt install autossh

        # vi /etc/systemd/system/autossh-reverse-tunnel.service
        [Unit]
        Description=AutoSSH reverse tunnel service
        After=network.target
        
        [Service]
        Restart=always
        RuntimeMaxSec=86400
        Environment="AUTOSSH_GATETIME=0"
        ExecStart=/usr/bin/autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -NR 2221:localhost:22 sshtunnel@remoteserver -p 222
        
        [Install]
        WantedBy=multi-user.target
    
    2. 启用客户端::
    
        # systemctl daemon-reload
    
        # systemctl start autossh-reverse-tunnel.service
    
        # systemctl enable autossh-reverse-tunnel.service

* 服务端

    1. SSH 服务配置::
    
        # vi /etc/ssh/sshd222_config
    
        Port 222
        PermitRootLogin no
        PasswordAuthentication no
        PermitEmptyPasswords no
        ChallengeResponseAuthentication no
        PrintMotd no
        Banner none
        PidFile /var/run/sshd222.pid
    
    #. 创建用户::
    
        # useradd -d /home/sshtunnel -s /bin/false -m sshtunnel
    
    #. SSH 密钥仅限于隧道::
    
        # mkdir /home/sshtunnel/.ssh
    
        # vi /home/sshtunnel/.ssh/authorized_keys
    
        no-pty,no-X11-forwarding,permitopen="localhost:2221",command="/bin/echo do-not-send-commands" ssh-rsa VeryLongsShkeyBlaBlaBlaBla root@hostname
        
    #. systemd 配置文件::
    
        # vi /etc/systemd/system/ssh222.service
        
        [Unit]
        Description=OpenBSD Secure Shell server
        Documentation=man:sshd(8) man:sshd_config(5)
        After=network.target auditd.service
        ConditionPathExists=!/etc/ssh/sshd_not_to_be_run
        
        [Service]
        EnvironmentFile=-/etc/default/ssh
        ExecStartPre=/usr/sbin/sshd -t -f /etc/ssh/sshd222_config
        ExecStart=/usr/sbin/sshd -D $SSHD_OPTS -f /etc/ssh/sshd222_config
        ExecReload=/usr/sbin/sshd -t -f /etc/ssh/sshd222_config
        ExecReload=/bin/kill -HUP $MAINPID
        KillMode=process
        Restart=on-failure
        RestartPreventExitStatus=255
        Type=notify
        RuntimeDirectory=sshd
        RuntimeDirectoryMode=0755
        
        [Install]
        WantedBy=multi-user.target
        Alias=sshd.service
    
    #. 服务端启用::
    
        # systemctl daemon-reload
    
        # systemctl start ssh222.service
    
        # systemctl enable ssh222.service
    
