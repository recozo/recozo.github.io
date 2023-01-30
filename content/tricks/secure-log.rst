#####################
用户登录日志文件
#####################

:tags: wtmp, secure, rsyslog
:category: how-to
:slug: login-log
:authors: Recozo
:date: 2021-11-01 10:43
:modified: 2021-11-01 10:43
:summary: 用户登录日志文件及管理

命令 last 以及 /var/log/wtmp
==================================================

/var/log/wtmp 是一个二进制文件，不能用 vi 直接查看，可能使用 last 或 who 进行查看::

    # last
    # who /var/log/wtmp

找不到 /var/log/secure 文件
==================================================

原来服务器的ssh登录等操作日志都是/var/log/secure，但 linux 的新发行版已经不再使用，改为使用rsyslog。
过程：先检查了一下ssh服务是否正常，vim /etc/ssh/sshd_config，检查到其中::

    LogLevel INFO
    SyslogFacility AUTHPRIV

没有问题。
然后查看rsyslog的配置文件 /etc/rsyslog.d/50-default.conf（我的电脑里是这个）。发现登录的配置为::

    auth,authpriv.*                 /var/log/auth.log

说明系统登录文件是/var/log/auth.log，基于这个文件来写脚本即可。