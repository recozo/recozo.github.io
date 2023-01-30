如何修改主机名和重置SSH
##################################################

:date: 2020-10-02 00:34
:modified: 2020-10-02 00:34

虚拟机下常用功能
--------------------------------------------------

一、修改主机名称::

    # hostnamectl set-hostname HostA
    # vi /etc/hosts
    # vi /etc/network/interfaces
    # vi /etc/resolv.conf 

二、重新生成SSH主机KEY::

    # rm -v /etc/ssh/ssh_host_*
    # dpkg-reconfigure openssh-server

三、更新系统::

    # apt update
    # apt upgrade

四、删除某个 systemd 服务

    # systemctl stop [servicename]
    # systemctl disable [servicename]
    # rm /etc/systemd/system/[servicename]
    # rm /etc/systemd/system/[servicename] # and symlinks that might be related
    # rm /usr/lib/systemd/system/[servicename] 
    # rm /usr/lib/systemd/system/[servicename] # and symlinks that might be related
    # systemctl daemon-reload
    # systemctl reset-failed

https://superuser.com/questions/513159/how-to-remove-systemd-services

五、彻底删除某应用

    # sudo apt autoremove --purge [applicationname]

https://howtoinstall.co/en/debian/wheezy/bind9?action=remove

六、清除 BASH 历史

    cat /dev/null > ~/.bash_history && history -c && exit

四、阿里云主机IP的设置::

    # cd /etc/systemd/network
    # ls