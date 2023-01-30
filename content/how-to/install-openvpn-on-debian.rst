使用 OpenVPN 安全访问业务网络
##################################################

:date: 2020-09-01 10:12
:modified: 2020-10-02 10:43
:tags: openvpn, usb key, ca

本配置方法用于正常使用OPENVPN的同时，启用CA与证书令牌，
如有需要还可附加启用RADIUS用户与口令认证。

本配置在 debian 11 下测试通过，默认环境为全新安装，仅安装 SSH 和 基础工具软件，
创建了一个普通用户 recozo，该用户开启 sudo 功能，并且配置好了内外网卡地址。

参见：

* https://www.digitalocean.com/community/tutorials/how-to-set-up-an-openvpn-server-on-debian-10
* https://www.osradar.com/openvpn-authentication-with-freeradius/
* https://openvpn.net/community-resources/how-to/#using-alternative-authentication-methods

零、初始化
--------------------------------------------------

进入 root 用户，使用以下命令初始化系统 ::

	# apt install sudo
	# adduser recozo sudo
	# timedatectl set-timezone Asia/Shanghai

一、安装OpenVPN
--------------------------------------------------

使用以下命令安装 OpenVPN ::

	$ sudo apt install openvpn

二、创建服务器证书和加密文件等
--------------------------------------------------

安装完OPENVPN后，默认自动安装了 easyrsa，可简化证书的日常管理操作。

以下使用普通用户 recozo 进行操作，假定 CA 工作目录为 ~/bizCA
（该目录名可以根据需要自行设定，也可以在以后的操作中修改目录名，甚至可以删除该目录，前提是你要作废或重置 CA ）

#. 初始化 easy-rsa ::

	$ make-cadir ~/bizCA && cd ~/bizCA
	$ vi vars

   对以下参数进行配置，以设置新证书的默认值 ::

		set_var EASYRSA_REQ_COUNTRY     "US"
		set_var EASYRSA_REQ_PROVINCE    "California"
		set_var EASYRSA_REQ_CITY        "San Francisco"
		set_var EASYRSA_REQ_ORG         "Copyleft Certificate Co"
		set_var EASYRSA_REQ_EMAIL       "me@example.net"
		set_var EASYRSA_REQ_OU          "My Organizational Unit"
   
   初始化 ca 环境 ::

	$ ./easyrsa init-pki

#. 生成CA证书 ::

	$ ./easyrsa build-ca nopass

   以上命令会生成 ca.crt 和 ca.key 两个文件，分别代表该 CA 的公钥与私钥(私钥必须严格保密),
   根据实际可设置 Common Name(如 Company-Name CA)或使用默认值

   将以上生成的 ca 证书复制到 OpenVPN 目录下 ::

	$ sudo cp pki/ca.crt /etc/openvpn/

#. 生成服务器证书 ::

	$ ./easyrsa gen-req VPNSVR nopass
	$ ./easyrsa sign-req server VPNSVR

   或者 ::

    $ ./easyrsa build-server-full VPNSVR nopass

   将以上生成的服务器证书复制到 OpenVPN 目录下 ::
  
	$ sudo cp pki/private/VPNSVR.key /etc/openvpn/
	$ sudo cp pki/issued/VPNSVR.crt /etc/openvpn/

#. 生成用于密钥交换的dh ::

	$ ./easyrsa gen-dh
	$ sudo cp pki/dh.pem /etc/openvpn/dh2048.pem

#. 生成的HMAC签名 ::

	$ sudo openvpn --genkey secret ta.key
	$ sudo chown recozo:recozo ta.key
	$ sudo cp ta.key /etc/openvpn/

三、配置 OpenVPN 服务端
--------------------------------------------------

#. 配置服务端配置文件 ::

	$ sudo cp /usr/share/doc/openvpn/examples/sample-config-files/server.conf /etc/openvpn/
	$ sudo vi /etc/openvpn/server.conf

   更新 server.conf 文件内容 ::

	;proto tcp
	proto udp

	ca ca.crt
	cert VPNSVR.crt
	key VPNSVR.key

	dh dh2048.pem

	topology subnet

	push "redirect-gateway def1 bypass-dhcp"	# 将客户端所有流量均从VPN转发，需要在防火墙设置NAT转换
	push "dhcp-option DNS 208.67.222.222"		# 视情况，DNS也可以不设置
	push "dhcp-option DNS 208.67.220.220"		# 视情况，DNS也可以不设置

	tls-auth ta.key 0				# This file is secret

	cipher AES-256-CBC
	auth SHA256
	
	user nobody					# Windows 下无须设置
	group nogroup					# Windows 下无须设置

	log-append  /var/log/openvpn/openvpn.log	# 启用日志功能

	# sndbuf 0					# 网上搜索解决OPENVPN速度过慢的解决方案
	# rcvbuf 0					# 不过好像没有什么用啊
	sndbuf 393216
	rcvbuf 393216

	push "sndbuf 393216"
	push "rcvbuf 393216"

#. 启用 IP 转发（需要完成以下配置防火墙步骤，以启用NAT转发） ::

	$ sudo vi /etc/sysctl.conf

   修改 sysctl.conf 内容 ::

	net.ipv4.ip_forward=1

   激活转发 ::

	$ sudo sysctl -p

#. 启用服务端 ::

	$ sudo systemctl start openvpn@server
	$ sudo systemctl enable openvpn@server

四、配置防火墙
--------------------------------------------------

如果客户端要访问除OPENVPN所在服务器外的其它网络地址，配置 NAT 转换 ::

	$ sudo apt install iptables
	$ sudo iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o eth0 -j MASQUERADE

以下为防火墙强化操作，请根据需要使用，适用于不安全环境下使用。
使用 iptables-persistent 持久化保存防火墙规则，根据需要，仅启用IPV4，关闭IPV6。
以下默认使用双网口，eth0为外网口，eth1为内（业务）网口，如果为单网口，请自行脑补。

参考链接：
https://www.linode.com/docs/networking/vpn/set-up-a-hardened-openvpn-server/

#. 安装 iptables-persistent ::

	$ sudo apt install iptables-persistent

#. 编辑IPV4规则 ::

	$ sudo vi /etc/iptables/rules.v4

   将该文件的内容替换为以下内容 ::

	*filter

	# Allow all loopback (lo) traffic and reject anything
	# to localhost that does not originate from lo.
	-A INPUT -i lo -j ACCEPT
	-A INPUT ! -i lo -s 127.0.0.0/8 -j REJECT
	-A OUTPUT -o lo -j ACCEPT

	# Allow ping and ICMP error returns.
	-A INPUT -p icmp -m state --state NEW --icmp-type 8 -j ACCEPT
	-A INPUT -p icmp -m state --state ESTABLISHED,RELATED -j ACCEPT
	-A OUTPUT -p icmp -j ACCEPT

	# Allow SSH.
	-A INPUT -i eth0 -p tcp -m state --state NEW,ESTABLISHED --dport 22 -j ACCEPT
	-A OUTPUT -o eth0 -p tcp -m state --state ESTABLISHED --sport 22 -j ACCEPT

	# 允许管理电脑互通访问
	-A INPUT -i eth0 -s 10.62.192.252/30 -j ACCEPT
	-A OUTPUT -o eth0 -d 10.62.192.252/30 -j ACCEPT

	# 只允许业务电脑访问，Allow UDP traffic on port 1194.
	-A INPUT -i eth0 -p udp -s 10.62.200.0/21 -m state --state NEW,ESTABLISHED --dport 1194 -j ACCEPT
	-A OUTPUT -o eth0 -p udp -d 10.62.200.0/21 -m state --state ESTABLISHED --sport 1194 -j ACCEPT

	# Allow DNS resolution and limited HTTP/S on eth0.
	# Necessary for updating the server and timekeeping.
	-A INPUT -i eth0 -p udp -m state --state ESTABLISHED --sport 53 -j ACCEPT
	-A OUTPUT -o eth0 -p udp -m state --state NEW,ESTABLISHED --dport 53 -j ACCEPT
	-A INPUT -i eth0 -p tcp -m state --state ESTABLISHED --sport 53 -j ACCEPT
	-A OUTPUT -o eth0 -p tcp -m state --state NEW,ESTABLISHED --dport 53 -j ACCEPT

	-A INPUT -i eth0 -p tcp -m state --state ESTABLISHED --sport 80 -j ACCEPT
	-A OUTPUT -o eth0 -p tcp -m state --state NEW,ESTABLISHED --dport 80 -j ACCEPT
	-A INPUT -i eth0 -p tcp -m state --state ESTABLISHED --sport 443 -j ACCEPT
	-A OUTPUT -o eth0 -p tcp -m state --state NEW,ESTABLISHED --dport 443 -j ACCEPT

	# Allow traffic on the TUN interface so OpenVPN can communicate.
	-A INPUT -i tun0 -j ACCEPT
	-A FORWARD -i tun0 -j ACCEPT
	-A OUTPUT -o tun0 -j ACCEPT

	# Allow forwarding traffic only from the VPN.
	-A FORWARD -i tun0 -o eth1 -s 10.8.0.0/24 -j ACCEPT
	-A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

	# Log any packets which don't fit the rules above.
	# (optional but useful)
	-A INPUT -m limit --limit 3/min -j LOG --log-prefix "iptables_INPUT_denied: " --log-level 4
	-A FORWARD -m limit --limit 3/min -j LOG --log-prefix "iptables_FORWARD_denied: " --log-level 4
	-A OUTPUT -m limit --limit 3/min -j LOG --log-prefix "iptables_OUTPUT_denied: " --log-level 4

	# then reject them.
	-A INPUT -j REJECT
	-A FORWARD -j REJECT
	-A OUTPUT -j REJECT

	COMMIT

#. 编辑IPV6规则（由于我们不需要IPV6，全部禁用） ::

	$ sudo vi /etc/iptables/rules.v6

   将该文件的内容替换为以下内容 ::

	*filter

	-A INPUT -j REJECT
	-A FORWARD -j REJECT
	-A OUTPUT -j REJECT

	COMMIT

#. 启用防火墙规则 ::

	$ sudo iptables-restore < /etc/iptables/rules.v4
	$ sudo ip6tables-restore < /etc/iptables/rules.v6
	$ sudo iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o eth1 -j MASQUERADE

#. 保存规则 ::

	$ sudo dpkg-reconfigure iptables-persistent

#. 禁用IPV6功能 ::

	$ sudo vi /etc/sysctl.d/99-sysctl.conf

   添加或修改以下内容 ::

	net.ipv6.conf.all.disable_ipv6 = 1
	net.ipv6.conf.default.disable_ipv6 = 1
	net.ipv6.conf.lo.disable_ipv6 = 1
	net.ipv6.conf.eth0.disable_ipv6 = 1

   激活以上配置 ::

	$ sudo sysctl -p

   注释掉IPV6的localhost解析 ::

	$ sudo vi /etc/hosts
	
	#::1     localhost ip6-localhost ip6-loopback

#. 查看防火墙规则与日志 ::

	$ sudo iptables -S					# 查看规则
	$ sudo tail -f /var/log/messages 			# 查看日志

五、配置业务路由示例（双网卡）
--------------------------------------------------

::

	$ sudo vi /etc/network/interfaces

参考以下内容更新 interfaces 文件 ::

	# The primary network interface
	allow-hotplug eth0
	iface eth0 inet static
		address 10.62.9.10/24
		# gateway 10.62.9.114
		# post-up ip route add default via 10.62.9.254 dev eth0
		# luxi vip hosts
		post-up ip route add 10.62.1.0/24 via 10.62.9.254 dev eth0
		post-up ip route add 10.62.192.252/30 via 10.62.9.254 dev eth0
		# luxi business private networks
		post-up ip route add 10.62.200.0/21 via 10.62.9.254 dev eth0
		# dns-* options are implemented by the resolvconf package, if installed
		dns-nameservers 10.62.9.114

	# The vlan716 network interface
	allow-hotplug eth1
	iface eth1 inet static
		address 172.10.85.253/25
		post-up ip route add default via 172.10.85.254 dev eth1

六、下发 OpenVPN 路由
--------------------------------------------------

可以根据需要在 /etc/openvpn/server.conf 中配置以下命令来指定客户端的路由设置 ::

	push "route 10.62.9.100 255.255.255.255 net_gateway"

以上配置用于确保客户端能够正常访问指定的（安全认证）服务器。

参见以下示例 ::

	# redirect all default traffic via the VPN
	push "redirect-gateway def1"
	# redirect the Intranet network 192.168.1/24 via the VPN
	push "route 192.168.1.0 255.255.255.0"
	# redirect another network to NOT go via the VPN
	push "route 10.10.0.0 255.255.255.0 net_gateway"
	# redirect a host using a domainname to NOT go via the VPN
	push "route www.google.ca 255.255.255.255 net_gateway"

七、准备客户端配置管理文件
--------------------------------------------------

为方便客户端的配置管理，创建一个专用目录和用于自动生成客户端配置的文件 ::

	$ mkdir -p ~/client-configs/files

不使用令牌认证的常规配置
``````````````````````````````````````````````````

::

	$ cp /usr/share/doc/openvpn/examples/sample-config-files/client.conf ~/client-configs/base.conf
	$ vi ~/client-configs/base.conf

使用以下内容更新 base.conf 内容 ::

	proto udp				# 与 server.conf 保持一致
	remote 10.62.9.24 1194			# 修改为本OPENVPN服务器的IP地址与端口号
	user nobody				# 仅适用于LINUX 客户端
	group nogroup				# 仅适用于LINUX 客户端
	#ca ca.crt				# 注释掉，包含在OVPN文件中
	#cert client.crt			# 注释掉，包含在OVPN文件中
	#key client.key				# 注释掉，包含在OVPN文件中
	#tls-auth ta.key 1			# 注释掉，包含在OVPN文件中
	key-direction 1
	cipher AES-256-CBC			# 与 server.conf 保持一致
	auth SHA256				# 与 server.conf 保持一致
	auth-nocache				# 避免出现安全警告

	# script-security 2			# 仅适用于LINUX 客户端，自行决定是否添加
	# up /etc/openvpn/update-resolv-conf	# 仅适用于LINUX 客户端，自行决定是否添加
	# down /etc/openvpn/update-resolv-conf	# 仅适用于LINUX 客户端，自行决定是否添加

生成 OVPN 的脚本 ::

	$ vi ~/client-configs/make_config.sh

使用以下内容生成 make_config.sh 内容 ::
	
	#!/bin/bash

	# First argument: Client identifier

	CA_DIR=~/bizCA/
	OUTPUT_DIR=~/client-configs/files
	BASE_CONFIG=~/client-configs/base.conf

	cat ${BASE_CONFIG} \
		<(echo -e '<ca>') \
		${CA_DIR}pki/ca.crt \
		<(echo -e '</ca>\n<cert>') \
		${CA_DIR}pki/issued/${1}.crt \
		<(echo -e '</cert>\n<key>') \
		${CA_DIR}pki/private/${1}.key \
		<(echo -e '</key>\n<tls-auth>') \
		${CA_DIR}/ta.key \
		<(echo -e '</tls-auth>') \
		> ${OUTPUT_DIR}/${1}.ovpn

将脚本修改为可执行文件 ::

	$ chmod 700 ~/client-configs/make_config.sh

使用飞天令牌的安全认证
``````````````````````````````````````````````````
启用epass1000ND的令牌认证，需要在客户端上预先安装epass1000ND的中间件
（使用EPASS1000ND（支持win10） v2.5 2015发布的），
然后在客户端配置文件中增加pkcs11-providers和pkcs11-id，
令牌制作方法见生成客户端证书以及配置文件 ::

	$ cp /usr/share/doc/openvpn/examples/sample-config-files/client.conf ~/client-configs/tokenbase.conf
	$ vi ~/client-configs/tokenbase.conf

使用以下内容更新 tokenbase.conf 内容 ::

	proto udp				# 与 server.conf 保持一致
	remote 10.62.9.24 1194			# 修改为本OPENVPN服务器的IP地址与端口号
	user nobody				# 仅适用于LINUX 客户端
	group nogroup				# 仅适用于LINUX 客户端
	#ca ca.crt				# 注释掉，包含在OVPN文件中
	#cert client.crt			# 注释掉，包含在OVPN文件中
	#key client.key				# 注释掉，包含在OVPN文件中
	#tls-auth ta.key 1			# 注释掉，包含在OVPN文件中
	key-direction 1
	cipher AES-256-CBC			# 与 server.conf 保持一致
	auth SHA256				# 与 server.conf 保持一致
	auth-nocache				# 避免出现安全警告
	# script-security 2			# 仅适用于LINUX 客户端，自行决定是否添加
	# up /etc/openvpn/update-resolv-conf	# 仅适用于LINUX 客户端，自行决定是否添加
	# down /etc/openvpn/update-resolv-conf	# 仅适用于LINUX 客户端，自行决定是否添加

	pkcs11-providers 'c:\windows\system32\ngp11v211.dll'
	pkcs11-id 'TODO'			# 需要生成令牌后获取实际 ID 后替换 TODO

生成 OVPN 的脚本 ::

	$ vi ~/client-configs/tokenmake_config.sh

使用以下内容生成 tokenmake_config.sh 内容 ::

	#!/bin/bash

	# First argument: Client identifier

	CA_DIR=/home/recozo/bizCA
	OUTPUT_DIR=/home/recozo/client-configs/files
	BASE_CONFIG=/home/recozo/client-configs/tokenbase.conf

	cat ${BASE_CONFIG} \
		<(echo -e '<ca>') \
		${CA_DIR}/pki/ca.crt \
		<(echo -e '</ca>\n<tls-auth>') \
		${CA_DIR}/ta.key \
		<(echo -e '</tls-auth>') \
		> ${OUTPUT_DIR}/${1}.ovpn

将脚本修改为可执行文件 ::

	$ chmod 700 ~/client-configs/tokenmake_config.sh

八、生成客户端证书以及配置文件
--------------------------------------------------		

生成客户端证书 ::

	$ ./easyrsa gen-req VPNCLI0520-001 nopass
	$ ./easyrsa sign-req client VPNCLI0520-001

或者 ::

	$ ./easyrsa build-client-full VPNCLI-001 nopass

不使用令牌认证的常规配置
``````````````````````````````````````````````````

执行脚本生成 OVPN 文件 ::

	$ ~/client-configs/make_config.sh VPNCLI-001

以上命令会在 ~/client-configs/files 目录下生成 VPNCLI-001.ovpn 文件，
将该配置文件复制给客户端即可(具体使用请参考客户端的程序说明)


使用飞天令牌的安全认证
``````````````````````````````````````````````````

启用epass1000ND的令牌认证，需要在客户端上预先安装 PUTTY 和 epass1000ND 的中间件
（使用EPASS1000ND（支持win10） v2.5 2015发布的），
然后修改 ovpn 文件中的 pkcs11-id。

在服务器上生成 ovpn 与 证书文件 ::

	$ ~/client-configs/tokenmake_config.sh VPNCLI0520-001
	$ ./easyrsa export-p12 VPNCLI0520-001 noca

以上命令会在 pki/private 目录中生成 pkcs#12 证书文件，可用于导入至 epass1000ND
（附：$ ./easyrsa 可以查看该命令所支持的全部功能）

将证书文件导入令牌的注意事项：

* 目前只在windows环境下成功完成了操作（ windows 7 以及 windows 10 ）
* 使用的令牌管理软件（目录）为 EPASS1000ND（支持win10）\\win2.5\\pki\\V2.5-20150919\\PKIcdrom\\CDROM_CN\\PKI
* 令牌（USB KEY）第一次使用时，要进行初始化，插入 USB KEY 后，执行 
  EPASS1000ND（支持win10）\\win2.5\\pki\\V2.5-20150919\\PKIcdrom\\CDROM_CN\\PKI\\Utilities\\PKIINIT\\PKIInit_M32.exe
* 令牌的管理与用户密码统一设置规则定义： 管理密码为路由器密码，用户密码为vlan号+id 
  (如：VPNCLI0716-001 的用户密码为 0716 + 001 = 0717)
* 使用 EPASS1000ND（支持win10）\\win2.5\\pki\\V2.5-20150919\\PKIcdrom\\CDROM_CN\\PKI\\Utilities\\ePassNgMgr.exe 
  导入前面所生成的证书

以下命令在安装了 OpenVPN 的 Windows 环境下运行，首先借助 pscp 复制刚才在服务器上生成的 ovpn 与 证书文件 ::

	C:\Users\recozo>pscp recozo@10.62.9.24:client-configs/files/VPNCLI0520-001.ovpn ./
	C:\Users\recozo>pscp recozo@10.62.9.24:bizCA/pki/private/VPNCLI0520-001.p12 ./

将p12导入令牌后，立即获取 Serialized id 
（注意：openvpn2.4版本下显示的 Serialized id 不被支持，必须使用 openvpn 2.3版本获取 Serialized id，
你可以将 2.3版的文件复制到 windows 上，运行以下命令前定位到 2.3 版本的目录下） ::

	.\openvpn --show-pkcs11-ids "c:\windows\system32\ngp11v211.dll"

将获取的 Serialized id 替换 ovpn 文件中的 pkcs11-id （即 TODO），
将该配置文件和令牌给客户即可。

九、为 OpenVPN 服务器安装 RadiusPlugin
--------------------------------------------------

#. 解决依赖问题 ::

	# apt-get install libgcrypt20-dev build-essential

#. 下载插件 ::

	# wget http://www.nongnu.org/radiusplugin/radiusplugin_v2.1a_beta1.tar.gz

#. 解压缩 ::

	# tar xf radiusplugin_v2.1a_beta1.tar.gz 
	# cd radiusplugin_v2.1a_beta1
	# make

#. 把编译好的模块拷贝适合的位置 ::

	# mkdir /etc/openvpn/radius
	# cp radiusplugin.so /etc/openvpn/radius
	# cp radiusplugin.cnf /etc/openvpn/radius

#. 配置 radiusplugin.cnf，配置前请在FreeRadius中增加nas记录 ::

	（insert into nas (nasname, shortname, secret, description) values ("Your Server IP", "NAS001", "password", "单位名称 VLAN ID 的 OPENVPN"); ）

	# vi /etc/openvpn/radius/radiusplugin.cnf

   修改 radiusplugin.cnf 内容 ::

		NAS-IP-Address=Your Server IP		#根据本机实际修改
		server
		{
			# The UDP port for radius accounting.
			acctport=1813
			# The UDP port for radius authentication.
			authport=1812
			# The name or ip address of the radius server.
			name=Your Radius Server IP		#根据FreeRadius服务器实际修改
			# How many times should the plugin send the if there is no response?
			retry=1
			# How long should the plugin wait for a response?
			wait=1
			# The shared secret.
			sharedsecret=password	# 与 FreeRadius 中的 nas 记录一致
		}

#. 启用RADIUS

   修改 server.conf ::

	# vi /etc/openvpn/server.conf

   在 server.conf 中增加以下内容 ::

	plugin /etc/openvpn/radius/radiusplugin.so /etc/openvpn/radius/radiusplugin.cnf

   修改 base.conf 或 tokenbase.conf ::

	# vi /etc/openvpn/client/base.conf

   在文件中加入下面这行内容 ::

	auth-user-pass
