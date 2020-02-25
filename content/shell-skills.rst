Linux Shell Skills
####################

:tags: linux, shell
:category: how-to
:slug: linux-shell-skills
:authors: Recozo

What's the difference between /sbin/nologin and /bin/false ?
    When /sbin/nologin is set as the shell, if user with that shell logs in, they'll get a polite message saying 'This account is currently not available.' This message can be changed with the file /etc/nologin.txt.
    
    /bin/false is just a binary that immediately exits, returning false, when it's called, so when someone who has false as shell logs in, they're immediately logged out when false exits. Setting the shell to /bin/true has the same effect of not allowing someone to log in but false is probably used as a convention over true since it's much better at conveying the concept that person doesn't have a shell.
    
    Looking at nologin's man page, it says it was created in 4.4 BSD (early 1990s) so it came long after false was created. The use of false as a shell is probably just a convention carried over from the early days of UNIX.
    
    nologin is the more user-friendly option, with a customizable message given to the user trying to log in, so you would theoretically want to use that; but both nologin and false will have the same end result of someone not having a shell and not being able to ssh in.

