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

四、阿里云主机IP的设置::

    # cd /etc/systemd/network
    # ls