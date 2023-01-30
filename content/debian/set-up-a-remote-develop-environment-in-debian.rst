安装远程开发桌面环境
##################################################

:date: 2020-08-26 16:01
:modified: 2020-08-26 16:01

安装操作系统及辅助功能
--------------------------------------------------

#. 正常安装debian（假定安装时指定的普通用户为 recozo），语言选择英文，时区美国东部时间……，安装软件时桌面环境选择 XFCE，启用 SSH Server，选择 standard system utilities

#. 安装完成后，默认使用普通用户登录，登录后打开一个终端窗口，切换为 root 用户，为普通用户启用 sudo 功能 ::

    $ su - root
    # apt install sudo
    # adduser recozo sudo

#. 安装中文输入法（支持五笔与拼音），安装完后点击右上角的输入法图标进行输入法配置 ::

    # apt install fcitx-table-wubi

#. 安装远程桌面（`参考`__）   
   
   __ https://forums.kali.org/showthread.php?46345-Enabling-Remote-Desktop-and-SSH-access-to-Kali
   
   ::

    # apt install xrdp
    # systemctl start xrdp
    # systemctl start xrdp-sesman
    # systemctl enable xrdp
    # systemctl enable xrdp-sesman


#. 启用远程声音（`参考`__）

   __ https://github.com/neutrinolabs/pulseaudio-module-xrdp/wiki/README

   ::

    # apt install build-essential dpkg-dev libpulse-dev pulseaudio 
    # apt build-dep pulseaudio
    # apt source pulseaudio
    # cd pulseaudio-12.2/
    # ./configure

    # apt install git
    # git clone https://github.com/neutrinolabs/pulseaudio-module-xrdp.git

    # cd pulseaudio-module-xrdp
    # ./bootstrap && ./configure PULSE_DIR=/root/pulseaudio-12.2
    # make
    # make install
    # ls $(pkg-config --variable=modlibexecdir libpulse)
    # cd
    # rm -r pulseaudio*

#. 设置正确的时区 ::

    # timedatectl set-timezone Asia/Shanghai

#. 重新启动系统以确保新的桌面环境正常启动，可在其它电脑上进行远程登录并进行操作

