将音频（视频）转录为文字
##################################################

:tags: speech recognition
:category: how-to
:slug: speech-recognition
:authors: Recozo

以下操作在 Windows 10 环境下

1. 下载 Virtual Audio Cable。下载地址：https://www.vb-audio.com/Cable/index.htm

#. 安装后，会生成了二个虚拟设备：CABLE Input 和 CABLE Output，并且被分别设置为播放和录制的默认设备；

    此时你会发现播放音频或视频没有声音了，你可以理解为声音已经被传送至 CABLE Input 了，并且被作为 CABLE Output 的输入了，
    也就是我们已经将音频或视频的声音作为话筒的输入了。
    如果你录制的同时还想听到音频或视频的声音，可以打开 CABLE Output 的属性，点击 *侦听* 面板，选择 *侦听此设备* ，然后 *通过此设备播放* 选择你的实际播放设备即可。
    也可以继续下载VB-Audio Additional Virtual Cables，那么还可以另外再创建4个虚拟声卡；
    想玩大点的（如声音混合等），可以下载该网站的其它软件。

#. 下载 youtube 视频

    * 通过在youtube链接中插入my，即可以在线下载该视频，缺点是不支持1080P或以上，不支持选择视频分辨率，也不支持只下载音频；
      假如 youtube 地址是 https://www.youtube.com/watch?v=q2adWg-Ct6Y ，只须将地址更换为 https://www.youtubemy.com/watch?v=q2adWg-Ct6Y ，就会出现下载界面。

    * 通过桌面程序下载，目前我正在使用的是 4K Video Downloader ，主要是因为可以免费使用，并支持下载 youtube 的视频文件或只下载音频文件；

#. 打开网页 https://www.textfromtospeech.com/zh/voice-to-text/ ，通过播放你下载的视频或音频文件，即可在线转录成文字了。

    使用这个网站是因为发现国内访问速度还行，谷歌也有在线转录功能，但是由于延时太长，导致转录效果不佳。

如何将文字转换为语音
==================================================

win10 环境下，无需安装第三方软件，利用 edge 浏览器的朗读功能和录音机功能实现。

edge 可以通过在地址栏使用 file://d:/filename.txt 打开本地文件，这样的话无须网站支持。