Install FreeRadius On Debian 10
##################################################

:tags: FreeRadius, PostgreSQL, MAC Limit
:category: how-to
:slug: install-freeradius-on-debian
:authors: Recozo
:summary: Getting setup freeradius with postgreSQL and support client's device limit

本文假定系统为全新安装的 DEBIAN 10，正常安装DEBIAN，开启SSH，SUDO功能。
通过安装 FreeRadius 和 PostgreSQL，支持常规的安装。
本安装教程最主要的功能在于支持 H3C 的 802.1x，并且限制用户允许登录访问的设备数量。
TODO: 对客户端启用证书的功能待下次测试并完善

一、安装
--------------------------------------------------
::

    # apt install freeradius freeradius-postgresql postgresql postgresql-client

二、配置 PostgreSQL
--------------------------------------------------

参考链接：
https://wiki.freeradius.org/guide/SQL-HOWTO-for-freeradius-3.x-on-Debian-Ubuntu

::

	# passwd postgres
	# su - postgres
	$ psql -c "ALTER USER postgres WITH PASSWORD 'securepassword';"
	$ createdb radius
	$ exit

	# cd /etc/freeradius/3.0/mods-config/sql/main/postgresql
	# psql -h localhost -U postgres radius < schema.sql
	# psql -h localhost -U postgres radius < setup.sql      -- 建议修改数据库访问账户的口令

可选择使用 pgadmin，如果不在同一台电脑上安装，还需要打开监听地址并授权安装了 pgadmin 计算机的访问 ::

    # apt install pgadmin3

    # vi /etc/postgresql/11/main/postgresql.conf
    --------------------EDIT--------------------
        listen_addresses = '*'
    --------------------------------------------

    # vi /etc/postgresql/11/main/pg_hba.conf
    --------------------ADD---------------------
        # 授权安装了 pgadmin 的计算机访问数据库
        host    all             all             xxx.xxx.xxx.xxx/32           md5
    --------------------------------------------

    # systemctl restart postgresql

三、配置 FreeRadius 3 启用 sql
--------------------------------------------------

参考链接： https://networkradius.com/doc/3.0.10/raddb/mods-available/eap/peap.html

::

    # vi /etc/freeradius/3.0/sites-available/default
    --------------------EDIT--------------------
        uncomment sql in authorize, accounting, session, post-auth section
    --------------------------------------------

    # vi /etc/freeradius/3.0/sites-available/inner-tunnel
    --------------------EDIT--------------------
        uncomment sql in authorize, session, post-auth section
    --------------------------------------------

    # vi /etc/freeradius/3.0/mods-available/sql
    --------------------EDIT--------------------
    sql {
        driver = "rlm_sql_postgresql"
        dialect = "postgresql"

        # Connection info:
        server = "localhost"
        port = 5432
        login = "radius"
        password = "setup.sql中设置的口令"

        # Database table configuration for everything except Oracle

        radius_db = "radius"

        # Set to ‘yes’ to read radius clients from the database (‘nas’ table)
        # Clients will ONLY be read on server startup.
        read_clients = yes

        # Table to keep radius client info
        client_table = "nas"
    --------------------------------------------

    # cd /etc/freeradius/3.0/mods-enabled
    # ln -s ../mods-available/sql sql
    # chown -h freerad:freerad /etc/freeradius/3.0/mods-enabled/sql
    # cd /etc/freeradius/3.0/mods-config/sql/main/postgresql

    # vi rczmacsetup.sql
    --------------------ADD---------------------
    /*
    * Table structure for table 'rczmaclimit'
    */
    CREATE TABLE rczmaclimit (
            UserName                text PRIMARY KEY,
            MacLimit                integer NOT NULL DEFAULT 1,  -- 0 Unlimited
            Remark                  text NOT NULL DEFAULT ''
    );
    GRANT SELECT on rczmaclimit TO radius;

    /*
    * Table structure for table 'rczmaccheck'
    */
    CREATE TABLE rczmaccheck (
            id                      serial PRIMARY KEY,
            UserName                text NOT NULL,
            CallingStationId        text NOT NULL,
            AuthDate                timestamp with time zone NOT NULL default now()
    );
    create index rczmaccheck_UserName on rczmaccheck (UserName,CallingStationId);
    GRANT SELECT, INSERT, UPDATE on rczmaccheck TO radius;
    GRANT USAGE, SELECT ON SEQUENCE rczmaccheck_id_seq TO radius;


    /*
    * Stored Procedure for authorize_check_query
    */
    CREATE OR REPLACE FUNCTION rczmac_authorize_check(rczuserName TEXT, rczcallingStationId TEXT)
    RETURNS TABLE (id integer, UserName text, Attribute text, Value text, Op varchar(2))
    LANGUAGE plpgsql    
    AS $$
    DECLARE
        isOk        boolean DEFAULT false;
        tmpMacLimit    integer;
        tmpMacTotal    integer;
    BEGIN
        IF EXISTS(
            SELECT * 
            FROM rczmaccheck
            WHERE rczmaccheck.UserName = rczmac_authorize_check.rczuserName
            AND rczmaccheck.CallingStationId = rczmac_authorize_check.rczcallingStationId
            )
        THEN
            RAISE LOG '用户: % MAC: % ，MAC已登记', rczmac_authorize_check.rczuserName, rczmac_authorize_check.rczcallingStationId;
            isOk = true;
        ELSE
            SELECT MacLimit INTO tmpMacLimit 
            FROM rczmaclimit 
            WHERE rczmaclimit.UserName = rczmac_authorize_check.rczuserName;
            
            IF NOT FOUND THEN
                RAISE LOG '用户: % MAC: % ，MAC上限无记录', rczmac_authorize_check.rczuserName, rczmac_authorize_check.rczcallingStationId;
                tmpMacLimit = 1;
            END IF;

            IF tmpMacLimit = 0 THEN
                RAISE LOG '用户: % MAC: % ，MAC上限为0', rczmac_authorize_check.rczuserName, rczmac_authorize_check.rczcallingStationId;
                isOk = true;
            ELSE
                SELECT COUNT(*) INTO tmpMacTotal 
                FROM rczmaccheck
                WHERE rczmaccheck.UserName = rczmac_authorize_check.rczuserName;

                IF tmpMacLimit > tmpMacTotal THEN
                    RAISE LOG '用户: % MAC: % ，MAC未登记且未达到上限', rczmac_authorize_check.rczuserName, rczmac_authorize_check.rczcallingStationId;
                    isOk = true;
                ELSE
                    RAISE LOG '用户: % MAC: % ，MAC达到上限禁止登录', rczmac_authorize_check.rczuserName, rczmac_authorize_check.rczcallingStationId;
                    isOk = false;
                END IF;
            END IF;
        END IF;

        RAISE LOG '用户: % 的MAC限制检查结果为： %', rczmac_authorize_check.rczuserName, isOk;

        RETURN QUERY
        -- 如果 isOk 不通过，不返回用户检查项
        SELECT radcheck.id, radcheck.UserName, radcheck.Attribute, radcheck.Value, radcheck.Op
        FROM radcheck
        WHERE radcheck.UserName = rczmac_authorize_check.rczuserName AND isOk
        ORDER BY id;
    END;
    $$;

    /*
    * Stored Procedure for post-auth-query
    */
    CREATE OR REPLACE PROCEDURE rczmac_post_auth(rczuserName TEXT, rczPass TEXT, rczReply TEXT, rczcallingStationId TEXT)
    LANGUAGE plpgsql    
    AS $$
    DECLARE
        tmpAuthDate     timestamp DEFAULT now();
    BEGIN
        INSERT INTO radpostauth(username, pass, reply, CallingStationId, authdate)
        VALUES (rczuserName, rczPass, rczReply, rczcallingStationId, tmpAuthDate);

        IF rczReply = 'Access-Accept' THEN
            IF EXISTS(
                SELECT * 
                FROM rczmaccheck
                WHERE rczmaccheck.UserName = rczmac_post_auth.rczuserName
                AND rczmaccheck.CallingStationId = rczmac_post_auth.rczcallingStationId
                )
            THEN
                RAISE LOG '用户: % MAC: % ，MAC已存在', rczmac_post_auth.rczuserName, rczmac_post_auth.rczcallingStationId;
            ELSE
                RAISE LOG '用户: % MAC: % ，MAC已新增', rczmac_post_auth.rczuserName, rczmac_post_auth.rczcallingStationId;

                INSERT INTO rczmaccheck(UserName, CallingStationId, AuthDate)
                VALUES (rczuserName, rczcallingStationId, tmpAuthDate); 
            END IF;
        END IF;
    END;
    $$;
    --------------------------------------------

    # psql -h localhost -U postgres radius < rczmacsetup.sql

    # vi /etc/freeradius/3.0/mods-config/sql/main/postgresql/queries.conf
    --------------------EDIT--------------------
    authorize_check_query = "\
        SELECT * FROM rczmac_authorize_check( \
            '%{User-Name}', \
            '%{Calling-Station-Id}')"
    post-auth {
        query = "CALL rczmac_post_auth( \
                    '%{User-Name}', \
                    '%{%{User-Password}:-Chap-Password}', \
                    '%{reply:Packet-Type}', \
                    '%{Calling-Station-Id}')"
    --------------------------------------------

    # vi /etc/freeradius/3.0/sites-available/inner-tunnel
    --------------------ADD---------------------
    #
    #  Look in an SQL database.  The schema of the database
    #  is meant to mirror the "users" file.
    #
    #  See "Authorization Queries" in sql.conf
    update request {
            &Calling-Station-Id := outer.request:Calling-Station-Id
    }
    sql
    --------------------------------------------

    # systemctl enable freeradius
    # systemctl restart freeradius

四、验证SQL是否安装正确（可选）
-------------------------------------------------

开二个终端，分别运行 FreeRadius 和 测试

终端一 ::

    # systemctl stop freeradius
    # freeradius -X

终端二 ::

    # psql -h localhost -U postgres radius
    radius=# insert into nas (nasname, shortname, secret, description) values ('xxx.xxx.xxx.xxx', 'Short Name', 'secure secret', 'description'); 	-- 加入要允许访问的NAS设备信息
    radius=# insert into radcheck (username,attribute,op,value) values('username', 'Cleartext-Password', ':=', 'password');	-- 加入要允许访问的用户信息
    radius=# \q
    # radtest username password localhost 0 testing123

五、生成 eapol_test 工具并验证 eap （可选）
-------------------------------------------------

开二个终端，分别运行 FreeRadius 和 测试

终端一 ::

    # systemctl stop freeradius
    # freeradius -X

终端二首先生成 eapol_test ::

    $ sudo apt install pkg-config
    $ sudo apt install build-essential 
    $ sudo apt install libssl-dev 
    $ sudo apt install libnl-genl-3-dev
    $ sudo apt install libdbus-1-dev
    $ wget https://w1.fi/releases/wpa_supplicant-2.9.tar.gz
    $ tar -zxf wpa_supplicant-2.9.tar.gz 
    $ cd wpa_supplicant-2.9/wpa_supplicant/
    $ cp defconfig .config
    $ vi .config 
    -------------------EDIT---------------------
        CONFIG_EAPOL_TEST=y
    --------------------------------------------
    $ make eapol_test
    $ mkdir ~/bin
    $ cp eapol_test ~/bin

继续在终端二测试 eap 功能 ::

    $ cd ~/bin
    $ vi eap-ttls-pap.conf
    -------------------ADD----------------------
    network={
        key_mgmt=WPA-EAP
        eap=TTLS
        identity="username"
        anonymous_identity="anonymous"
        password="password"
        phase2="auth=PAP"
    }
    --------------------------------------------
    $ ./eapol_test -c eap-ttls-pap.conf -s testing123

六、生成 eap 证书（可选，但是强烈建议）
-------------------------------------------------

参考链接： https://networkradius.com/doc/FreeRADIUS-Implementation-Ch6.pdf

参考链接： http://deployingradius.com/documents/configuration/certificates.html

一般来说，802.1X 下建议使用自己的CA，生成自签名证书并将根证书安装在用户终端上。
如果用户终端不安装根证书或使用第三方证书的话，存在以下安全隐患：
1、不安装根证书时，存在伪造服务器的可能（创建一个同名SSID的无线，使用伪造的radius服务器），导致用户名与密码泄露；
2、如果启用 EAP-TLS 并使用第三方根证书的话，此时只要是该机构签发的用户证书均有效，导致用户证书不受控。
一般情况下这不是我们想要的结果；因此，如果要使用其它CA的证书，请仔细考虑清楚。

注意：debian 下的 freeradius 会自动对 EAP 使用 ssl-cert 所生成的 ssl-cert-snakeoil 证书。
该证书是基于debian的自签名证书，主要用于方便需要创建SSL证书的软件包安装，
如果 snakeoil 证书过期，可以使用以下命令重新生成 sudo make-ssl-cert generate-default-snakeoil --force-overwrite ，
也就是不用进行证书生成操作，也可以保证 freeradius 支持 EAP。
不过在生产环境下不应该使用该证书，而应根据实际生成或使用对应的证书。
测试中发现在 debian 环境下的 freeradius -X 不会自动生成证书（这点似乎与freeradius 官方的说明不一致）。

删除原来生成的证书（生产环境下慎用） ::

    # cd /etc/freeradius/3.0/certs
    # rm -f *.pem *.der *.csr *.crt *.key *.p12 serial* index.txt*

生成根证书 ::

    # vi /etc/freeradius/3.0/certs/ca.cnf
    --------------------EDIT--------------------
    [ CA_default ]
    default_days            = 3600

    [ req ]
    input_password = whateverCA
    output_password = whateverCA

    [certificate_authority]
    countryName             = CN
    stateOrProvinceName     = Jiangxi
    localityName            = Pingxiang
    organizationName        = Organization Name
    emailAddress            = radius@example.com
    commonName              = "XXXXXX Certificate Authority"
    --------------------------------------------

    # make ca.pem
    # make ca.der

生成服务器证书（countryName, stateOrProvinceName, localityName 要与根证书一致？？） ::

    # vi /etc/freeradius/3.0/certs/server.cnf
    --------------------EDIT--------------------
    [ CA_default ]
    default_days            = 3600

    [ req ]
    input_password = whateverSVR
    output_password = whateverSVR

    [server]
    countryName             = CN
    stateOrProvinceName     = Jiangxi
    localityName            = Pingxiang
    organizationName        = Organization Name
    emailAddress            = radius@example.com
    commonName              = "XXXXXX Server Certificate"
    --------------------------------------------

    # make server.pem

修改 eap 配置以使用新创建的证书 ::

    # vi /etc/freeradius/3.0/mods-available/eap
    --------------------EDIT--------------------
    tls-config tls-common {
        private_key_password = whateverSVR
        private_key_file = ${cadir}/server.key
        certificate_file = ${cadir}/server.pem
        ca_file = ${cadir}/ca.pem
    }
    --------------------------------------------

    # chown freerad:freerad server.key
    # chown freerad:freerad server.pem
    # chown freerad:freerad ca.pem

    # systemctl restart freeradius

七、在 H3C 设备上配置 Radius 并启用（无线）802.1x
-------------------------------------------------

八、配置终端的 802.1x 访问
-------------------------------------------------

参考链接： https://schoolsysadmin.blogspot.com/2016/03/freeradius-production-ssl-certificates.html

将根CA文件（ca.der）公开，方便用户在终端设备上导入；

windows 下配置无线

