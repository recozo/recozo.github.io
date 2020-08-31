Linux Shell Skills
####################

:tags: linux, shell
:category: how-to
:slug: linux-shell-skills
:authors: Recozo

如何查看 debian 包中的文件
================================================================================================================================================================================================================================================
::

    dpkg -L packagename

What's the difference between /sbin/nologin and /bin/false ?
================================================================================================================================================================================================================================================
When /sbin/nologin is set as the shell, if user with that shell logs in, they'll get a polite message saying 'This account is currently not available.' This message can be changed with the file /etc/nologin.txt.

/bin/false is just a binary that immediately exits, returning false, when it's called, so when someone who has false as shell logs in, they're immediately logged out when false exits. Setting the shell to /bin/true has the same effect of not allowing someone to log in but false is probably used as a convention over true since it's much better at conveying the concept that person doesn't have a shell.

Looking at nologin's man page, it says it was created in 4.4 BSD (early 1990s) so it came long after false was created. The use of false as a shell is probably just a convention carried over from the early days of UNIX.

nologin is the more user-friendly option, with a customizable message given to the user trying to log in, so you would theoretically want to use that; but both nologin and false will have the same end result of someone not having a shell and not being able to ssh in.

`Five find command Linux: find, locate, whereis, which, type <https://www.programering.com/a/MjM5gDMwATg.html>`_
================================================================================================================================================================================================================================================
find
    Find is the most common and most powerful search command, you can find anything you want to find the file in it. 
locate
    The locate command is "another way find -name", but it is much faster than the latter, because it does not search the directory, but search a database (/var/lib/locatedb), containing all the local file information in the database. Automatic creation of the database of Linux system, and automatic daily updated, so use the locate command to not check the latest change file. To avoid this situation, can before using locate, first useupdatedbCommand, to update the database manually. 
whereis
    The whereis command can only be used for the program name search, and search a binary file (parameter -b), the man description file (parameter -m) and source code files (parameter -s). If you omit the argument, it returns all the information. 
which
    The which command is the role of the PATH variable, in the path specified in the search, a command position, return the first search results and. That is to say, use the which command, you can see a system command exists, and what a position command. 
type
    The type command can not find command, which is used to distinguish between a command what is included with the shell, or provided by independent binary files outside the shell. If a command is an external command, then use the -p parameter, the command will display the path, the equivalent of the which command. 
    ::

	type -a echo

    `There are two classes of builtins <https://unix.stackexchange.com/questions/1355/why-is-echo-a-shell-built-in-command>`_

    1. Some commands have to be built into the shell program itself because they cannot work if they are external.

    2. The other class of commands are built into the shell purely for efficiency.

`What is the difference between executing a Bash script vs sourcing it? <https://superuser.com/questions/176783/what-is-the-difference-between-executing-a-bash-script-vs-sourcing-it>`_
================================================================================================================================================================================================================================================
::

    ./myscript

    . myscript
    source myscript

./ 代表的是当前目录。
. myscript 与 source myscript 是一样的，This "spelling" is the official one as defined by POSIX. Bash defined source as an alias to the dot.

Executing a script will run the commands in a new shell process. 

Sourcing a script will run the commands in the current shell process. 

Use source if you want the script to change the environment in your currently running shell. use execute otherwise.

