POSTGRESQL 学习
##################################################

:date: 2020-10-03 20:16
:modified: 2022-05-03 00:33
:tags: postgresql, database

安装配置 PostgreSQL
==================================================

安装 postgresql 并登录至 postgres 用户环境 ::

    $ sudo apt install postgresql
    $ sudo -i -u postgres
    $ psql

创建角色以及数据库 ::

    >> CREATE ROLE demo_role LOGIN PASSWORD 'demo_password';
    >> CREATE DATABASE demo_db WITH owner = demo_role;

默认安装时，只允许本机访问，可以选择开启远程访问 ::

    $ vi /etc/postgresql/13/main/postgresql.conf
    # 修改 listen_addresses = '*'， 表示在所有接口上监听，默认只在 127.0.0.1 监听

    $ vi /etc/postgresql/13/main/pg_hba.conf
    # 增加一条如下记录，表示允许以下 IP 范围使用角色密码访问
    # host    all             all             10.62.1.0/24            md5

修改后要重新启动 postgresql ::

    $ sudo systemctl restart postgresql.service
    

Roles
==================================================

PostgreSQL represents accounts as roles.
Roles that can log in are called login roles.
Roles that contain other roles are called group roles.
Roles that are group and can log in are called group login roles.
However, for easier maintainability and security, DBAs generally don't grant login rights to group roles.
A role can be designated as superuser.
Recent versions of PostgreSQL no longer use the terms users and groups.
For backward compatibility, CREATE USER and CREATE GROUP still work in current version, but shun them and use CREATE ROLE instead.

Creating Login Roles
--------------------------------------------------

Example 2-4. Creating login roles ::

    CREATE ROLE leo LOGIN PASSWORD 'king' CREATEDB VALID UNTIL 'infinity';

Example 2-5. Creating superuser roles ::

    CREATE ROLE regina LOGIN PASSWORD 'queen' SUPERUSER VALID UNTIL '2020-1-1 00:00';

Creating Group Roles
--------------------------------------------------

::

    CREATE ROLE royalty INHERIT;
    GRANT royalty TO leo;
    GRANT royalty TO regina;

Inheriting rights from group roles
--------------------------------------------------

::

    SET ROLE some_role
    SET SESSION AUTHORIZATION some_role

*   Only superusers can execute SET SESSION AUTHORIZATION ,
    and it allows them to impersonate any user regardless of role membership.
*   SET SESSION AUTHORIZATION changes the values of the current_user and session_user variables 
    to those of the user being impersonated. 
    SET ROLE changes only the current_user variable.
*   Because both the current_user and session_user are changed by SET SESSION AUTHORIZATION , 
    subsequent SET role commands are limited to those allowed by the user being impersonated. 
    After SET ROLE , roles can be set to any role that the original user has rights to impersonate.

通过编辑 pg_hba.conf 可以修改用户（ROLE）的认证方法，默认使用 peer ，会要求有相应的系统用户，
通过修改为 md5，可以使用密码验证 或修改为 trust， 可以直接登录无须验证。

参见： https://www.postgresql.org/docs/current/auth-methods.html

Database Creation
==================================================

::

    CREATE DATABASE mydb;

This creates a copy, owned by the login role that issued the command, 
of the template1 default. Any role with CREATEDB rights can create new databases.

Template Databases
--------------------------------------------------

A template database is a database that serves as a model for other databases. 
The default PostgreSQL installation comes with two template databases: template0 and template1 .
If you don’t specify a template database to follow when you create a database, 
the template1 database is used as the template for the new database.

::

    CREATE DATABASE my_db TEMPLATE my_template_db;
    UPDATE pg_database SET datistemplate = TRUE WHERE datname = 'mydb';

Using Schemas
--------------------------------------------------

Schemas organize your database into logical groups.
It’s up to you how to organize your schemas.

Another common way to organize schemas is by roles.
We can take advantage of the default search path set in postgresql.conf::

	search_path = "$user", public;

Another practice that we strongly advocate is to create schemas to house extensions::

    CREATE SCHEMA my_extensions;
    ALTER DATABASE mydb SET search_path='"$user", public, my_extensions';

Privileges
==================================================

Privileges (often called permissions) can be tricky to administer in PostgreSQL 
because of the fine granular control at your disposal. 
Security can bore down to the object level. 
You could assign different privileges to each column of your table, if that ever becomes necessary.

Types of Privileges
--------------------------------------------------

Some of the object-level privileges you find in PostgreSQL are 
SELECT , INSERT , UPDATE , ALTER , EXECUTE , TRUNCATE , 
and a qualifier to those called WITH GRANT .
Note that privileges are relevant only with respect to a particular database asset. 
For example, TRUNCATE for functions and EXECUTE for tables make no sense.

Getting Started
--------------------------------------------------

#.  PostgreSQL creates one superuser and one database for you at installation, both named postgres. 
    Log into your server as postgres .
#.  Before creating your first database, create a role that will own the database and can log in, 
    such as::

	    CREATE ROLE mydb_admin LOGIN PASSWORD 'something';

#.  Create the database and set the owner::

    	CREATE DATABASE mydb WITH owner = mydb_admin;

#.  Now log in as the mydb_admin user and start setting up additional schemas and tables.

GRANT
--------------------------------------------------

The GRANT command assigns privileges to others. The basic usage is::

	GRANT some_privilege TO some_role;

A few things to keep in mind when it comes to GRANT :

*   You need to be the holder of the privilege that you’re granting 
    and you must have grant privilege yourself. You can’t give away what you don’t have.
*   Some privileges always remain with the owner of an object and can never be granted away. 
    These include DROP and ALTER .
*   The owner of an object already has all privileges. 
    Granting an owner privilege in what it already owns is unnecessary.
*   When granting privileges, you can add WITH GRANT OPTION .
    This means that the grantee can grant onwards::

	    GRANT ALL ON ALL TABLES IN SCHEMA public TO mydb_admin WITH GRANT OPTION;

*   To grant all relevant privileges on an object use ALL instead of the specific privilege::

    	GRANT SELECT, REFERENCES, TRIGGER ON ALL TABLES IN SCHEMA my_schema TO PUBLIC;

*   The ALL alias can also be used to grant for all objects within a database or schema::

	    GRANT SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA my_schema TO PUBLIC;

*   To grant privileges to all roles, you can use the alias PUBLIC ::

    	GRANT USAGE ON SCHEMA my_schema TO PUBLIC;

Some privileges are by default granted to PUBLIC . 
These are CONNECT and CREATE TEMP TABLE for databases, EXECUTE for functions, and USAGE for languages. 
In many cases you might consider revoking some of defaults for your own safety. 
Use the REVOKE command::

	REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA my_schema FROM PUBLIC;


Default Privileges
--------------------------------------------------

PostgreSQL 9.0 introduced default privileges, 
which allow users to set privileges on all database assets within a particular schema or database, 
as well as in advance of their creation. 
Adding or changing default privileges won’t affect current privilege settings.

Example 2-6. Defining default privileges on a schema::

    GRANT USAGE ON SCHEMA my_schema TO PUBLIC;
    ALTER DEFAULT PRIVILEGES IN SCHEMA my_schema GRANT SELECT, REFERENCES ON TABLES TO PUBLIC;
    ALTER DEFAULT PRIVILEGES IN SCHEMA my_schema GRANT ALL ON TABLES TO mydb_admin WITH GRANT OPTION;
    ALTER DEFAULT PRIVILEGES IN SCHEMA my_schema GRANT SELECT, UPDATE ON SEQUENCES TO public;
    ALTER DEFAULT PRIVILEGES IN SCHEMA my_schema GRANT ALL ON FUNCTIONS TO mydb_admin WITH GRANT OPTION;
    ALTER DEFAULT PRIVILEGES IN SCHEMA my_schema GRANT USAGE ON TYPES TO PUBLIC;

Privilege Idiosyncrasies
--------------------------------------------------

Unlike in other database products, 
being the owner of a PostgreSQL database does not give you access to all objects in the database, 
but it does grant you privileges to whatever objects you create and allows you to drop the database.

Another role can create objects that you can’t access in your owned database. 
Interestingly, though, you can still drop the whole database.

People often forget to set GRANT USAGE ON SCHEMA or GRANT ALL ON SCHEMA. 
Even if your tables and functions have rights assigned to a role, 
these tables and functions will still not be accessible 
if the role has no USAGE rights to the schema.

