百度 API 应用
##################################################

:date: 2020-09-15 00:16
:modified: 2020-09-15 00:16
:tags: baidu, api

百度分享的使用
==================================================

百度分享的网站目前已经关了，不过功能目前好像还有用，暂时先用着吧……

参考： https://www.cnblogs.com/cyhan/p/11671566.html

这里完整的展示一下插件如何编写。

#.  插入百度分享插件js文件

    官方插件不支持https，如果要用https的话可下载 `支持HTTPS百度分享插件 <https://github.com/hrwhisper/baiduShare/>`_ 。 
    
    下载后需要把 static 文件夹放在网站的根目录下，
    并将百度分享代码中的 http://bdimg.share.baidu.com/ 改为 / 。 ::

        with (document) 0[(getElementsByTagName('head')[0] || body)
            .appendChild(createElement('script'))
            .src = '/static/api/js/share.js?v=89860593.js?cdnversion=' + ~(-new Date() / 36e5)];

#.  代码结构

    分享代码可以分为三个部分：HTML、设置和js加载，示例如下：

    代码结构 ::
    
        <div class="bdsharebuttonbox" data-tag="share_1">
	        <!-- 此处添加展示按钮 -->
        </div>
        <script>
            window._bd_share_config = {
            //此处添加分享具体设置
            }

            //以下为js加载部分
            with(document)0[(getElementsByTagName('head')[0]||body)
                .appendChild(createElement('script'))
                .src='http://bdimg.share.baidu.com/static/api/js/share.js?cdnversion='+~(-new Date()/36e5)];
        </script>

#.  按钮标签

    按钮标签代码 ::

        <div class="bdsharebuttonbox" data-tag="share_1">
            <a class="bds_mshare" data-cmd="mshare"></a>
            <a class="bds_qzone" data-cmd="qzone" href="#"></a>
            <a class="bds_tsina" data-cmd="tsina"></a>
            <a class="bds_baidu" data-cmd="baidu"></a>
            <a class="bds_renren" data-cmd="renren"></a>
            <a class="bds_tqq" data-cmd="tqq"></a>
            <a class="bds_more" data-cmd="more">更多</a>
            <a class="bds_count" data-cmd="count"></a>
        </div>

    说明：

    只有普通页面分享需要按钮标签。划词分享、图片分享无需添加HTML结构。

    HTML结构可以放在body的任意位置，可复制多份。

    class＝"bdsharebuttonbox" 部分为dom选择器，请勿改动。

    data-tag属性为分享按钮标识，用于实现同一页面中多分享按钮不同配置，详见设置部分。

    data-cmd属性为分享目标标识，取值请参见：分享媒体id对应表。此外值为more时点击展现更多弹窗，值为count时展现分享数。

    HTML代码中其他部分均可自定义。


在网页嵌入百度地图
==================================================

参考： http://lbsyun.baidu.com/jsdemo.htm#a7_1

::

    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
        <style type="text/css">
            #allmap {height:400px;width: 600px;margin: 0;overflow: hidden;font-family:"微软雅黑";}
        </style>
        <script type="text/javascript" src="//api.map.baidu.com/api?v=2.0&ak=您的密钥"></script>
        <title>关闭默认地图POI事件</title>
    </head>
    <body>
        <div id="allmap"></div>
    </body>
    </html>
    <script type="text/javascript">
            // 百度地图API功能
        var map = new BMap.Map("allmap");
        var point = new BMap.Point(114.040208,27.635682);
        map.centerAndZoom(point, 17);
        var marker = new BMap.Marker(point);  // 创建标注
        map.addOverlay(marker);               // 将标注添加到地图中
        marker.setAnimation(BMAP_ANIMATION_BOUNCE); //跳动的动画
        map.enableScrollWheelZoom(true);     //开启鼠标滚轮缩放
    </script>
