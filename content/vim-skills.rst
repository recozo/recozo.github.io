Vim skills
##########

:tags: vi, vim
:category: how-to
:slug: vim-skills
:authors: Recozo

在10行和112行之间插入4空格::

    10,112 s/^/    /

删除空行以及只有空格的行::

    :g/^\s*$/d

恢复删除操作::

    vi对删除(d or x)或复制(y)有各自专用的 buffer，
    删除buffer会自动保留最近的9个删除操作(行内删除除外)至buffer，9个删除自动按照1-9保存，最近一次删除保存在1；
    可以使用 "1pu.u.u etc 命令查看各个删除的内容

    复制buffer可保留26个命名（从a-z）复制内容，如果复制时未使用命名，自动使用a??
    "d7yy
    "a5dd
    此处注意dd操作会分别保存在删除buffer 1中和复制buffer a 中
