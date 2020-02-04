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
