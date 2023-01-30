使用 BIND9 创建DNS服务器
##################################################

:date: 2020-11-21 10:12
:modified: 2020-11-21 10:43
:tags: bind9, dns

本配置在 debian 10 下测试通过，默认环境为全新安装，仅安装 SSH 和 基础工具软件，
创建了一个普通用户 recozo，该用户开启 sudo 功能。

参见：

* https://wiki.debian.org/bind9
* https://www.linuxbabe.com/debian/dns-resolver-debian-10-buster-bind9

一、安装 BIND9
--------------------------------------------------

使用以下命令安装 BIND9 ::

	$ sudo apt install bind9 bind9-doc dnsutils resolvconf

检查版本及运行信息 ::

    $ sudo named -v
    $ systemctl status bind9
    $ sudo netstat -lnptu | grep named
    $ sudo rndc status

二、Configurations for a Local DNS Resolver
--------------------------------------------------

::

    sudo vi /etc/bind/named.conf.options

In the options clause, add the following lines. Replace IP addresses in the allow-recursion statement with your own local network addresses.

::

    directory "/var/cache/bind";

    // If there is a firewall between you and nameservers you want
    // to talk to, you may need to fix the firewall to allow multiple
    // ports to talk.  See http://www.kb.cert.org/vuls/id/800113

    // If your ISP provided one or more IP addresses for stable
    // nameservers, you probably want to use them as forwarders.
    // Uncomment the following block, and insert the addresses replacing
    // the all-0's placeholder.

    // forwarders {
    //      0.0.0.0;
    // };

    //========================================================================
    // If BIND logs error messages about the root key being expired,
    // you will need to update your keys.  See https://www.isc.org/bind-keys
    //========================================================================
    // dnssec-validation auto;

    // listen-on-v6 { any; };

    // add by Recozo begin

    // enable the query log
    querylog yes;

    // Transmit requests to 192.168.1.1 if
    // this server doesn't know how to resolve them
    forward only;
    forwarders { 202.101.224.68; };

    auth-nxdomain no;    # conform to RFC1035

    // From 9.9.5 ARM, disables interfaces scanning to prevent unwanted stop listening
    interface-interval 0;
    // Listen on local interfaces only(IPV4)
    listen-on-v6 { none; };
    listen-on { 127.0.0.1; 10.62.9.105; };

    // Accept requests for internal network only
    allow-query { 127.0.0.1; 10.62.0.0/16; };

    // Do not make public version of BIND
    version none;

    // add by Recozo end

::

    $ sudo named-checkconf
    $ sudo systemctl restart bind9
    $ dig xxx.domainname.com
    $ sudo journalctl -eu bind9

三、Setting the Default DNS Resolver on Debian 10 Buster Server

::

    sudo systemctl start bind9-resolvconf

    sudo systemctl enable bind9-resolvconf