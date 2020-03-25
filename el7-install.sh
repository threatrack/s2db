#!/bin/bash
if [[ -z "${MYSQL_ROOT_PASS}" ]]; then
	echo "Please set MYSQL_ROOT_PASS env var"
	exit 1
fi
if [[ -z "${S2DB_ADMIN_PASS}" ]]; then
	echo "Please set S2DB_ADMIN_PASS env var"
	exit 1
fi
if [[ -z "${S2DB_SELECT_PASS}" ]]; then
	echo "Please set S2DB_SELECT_PASS env var"
	exit 1
fi
if [[ -z "${S2DB_INSERT_PASS}" ]]; then
	echo "Please set S2DB_INSERT_PASS env var"
	exit 1
fi

echo needs sudo
sudo echo thx

sudo yum -y install python36 python36-pip mariadb-server python36-beautifulsoup4.noarch wkhtmltopdf ssdeep python36-sqlalchemy python36-mysql GeoIP GeoIP-data radare2
sudo pip3.6 install -U virustotal3 fake_useragent requests python-magic requests imgkit ssdeep pefile capstone

sudo systemctl start mariadb
sudo systemctl enable mariadb

mysqladmin -u root password "${MYSQL_ROOT_PASS}"
mysql -u root -p"${MYSQL_ROOT_PASS}" -e "UPDATE mysql.user SET Password=PASSWORD('${MYSQL_ROOT_PASS}') WHERE User='root'"
mysql -u root -p"${MYSQL_ROOT_PASS}" -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1')"
mysql -u root -p"${MYSQL_ROOT_PASS}" -e "DELETE FROM mysql.user WHERE User=''"
mysql -u root -p"${MYSQL_ROOT_PASS}" -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%'"
mysql -u root -p"${MYSQL_ROOT_PASS}" -e "FLUSH PRIVILEGES"

mysql -u root -p"${MYSQL_ROOT_PASS}" -e "delete from mysql.user where user like 's2db%'"
mysql -u root -p"${MYSQL_ROOT_PASS}" -e "drop database s2db"

mysql -u root -p"${MYSQL_ROOT_PASS}" -e "create database s2db character set utf8;"
mysql -u root -p"${MYSQL_ROOT_PASS}" -e "create user 's2db_admin'@'localhost' identified by '${S2DB_ADMIN_PASS}';"
mysql -u root -p"${MYSQL_ROOT_PASS}" -e "grant all on s2db.* to 's2db_admin' identified by '${S2DB_ADMIN_PASS}';"
mysql -u root -p"${MYSQL_ROOT_PASS}" -e "create user 's2db_select'@'localhost' identified by '${S2DB_SELECT_PASS}';"
mysql -u root -p"${MYSQL_ROOT_PASS}" -e "grant select on s2db.* to 's2db_select' identified by '${S2DB_SELECT_PASS}';"
mysql -u root -p"${MYSQL_ROOT_PASS}" -e "create user 's2db_insert'@'localhost' identified by '${S2DB_INSERT_PASS}';"
mysql -u root -p"${MYSQL_ROOT_PASS}" -e "grant insert on s2db.* to 's2db_insert' identified by '${S2DB_INSERT_PASS}';"
mysql -u root -p"${MYSQL_ROOT_PASS}" -e "FLUSH PRIVILEGES"

mysql -u s2db_admin -p"${S2DB_ADMIN_PASS}" <<DBSETUP
use s2db
create table bin (
	bin binary(32) not null,
	name varchar(255) character set utf8 not null,
	ref boolean not null default false,
	primary key (bin)
);

create table bin2seq (
	bin binary(32) not null,
	seq binary(32) not null,
	primary key (bin,seq)
);

create table seq (
	seq binary(32) not null,
	type varchar(32) not null,
	rep varchar(255) character set utf8 not null,
	primary key (seq)
);
DBSETUP

# copy config
mkdir -p ~/.s2db/samples
cp s2db.ini ~/.s2db/.
touch ~/.s2db/upload.log

# bootstrap stuff
cd flask/static
wget https://github.com/twbs/bootstrap/releases/download/v4.4.1/bootstrap-4.4.1-dist.zip -c
if [ ! -d bootstrap-4.4.1-dist/ ]; then
	unzip -o bootstrap-4.4.1-dist.zip
fi
mkdir jquery-3.4.1-dist/js
wget https://code.jquery.com/jquery-3.4.1.min.js -O jquery-3.4.1-dist/js/jquery-3.4.1.min.js -c



