#!/bin/bash
DATABASE_ROOT_PASS="asdf1234"
DATABASE_USER_PASSWORD="asdf1234"

echo needs sudo
sudo echo thx

sudo yum -y install python36 python36-pip mariadb-server python36-beautifulsoup4.noarch wkhtmltopdf ssdeep python36-sqlalchemy python36-mysql GeoIP GeoIP-data radare2
sudo pip3.6 install -U virustotal3 fake_useragent requests python-magic requests imgkit ssdeep pefile capstone

sudo systemctl start mariadb
sudo systemctl enable mariadb

mysqladmin -u root password "$DATABASE_ROOT_PASS"
mysql -u root -p"$DATABASE_ROOT_PASS" -e "UPDATE mysql.user SET Password=PASSWORD('$DATABASE_ROOT_PASS') WHERE User='root'"
mysql -u root -p"$DATABASE_ROOT_PASS" -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1')"
mysql -u root -p"$DATABASE_ROOT_PASS" -e "DELETE FROM mysql.user WHERE User=''"
mysql -u root -p"$DATABASE_ROOT_PASS" -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%'"
mysql -u root -p"$DATABASE_ROOT_PASS" -e "FLUSH PRIVILEGES"

mysql -u root -p"$DATABASE_ROOT_PASS" -e "create database b3 character set utf8;"
mysql -u root -p"$DATABASE_ROOT_PASS" -e "create user 'b3user'@'localhost' identified by '$DATABASE_USER_PASSWORD';"
mysql -u root -p"$DATABASE_ROOT_PASS" -e "grant all on b3.* to 'b3user' identified by '$DATABASE_USER_PASSWORD';"
mysql -u root -p"$DATABASE_ROOT_PASS" -e "FLUSH PRIVILEGES"

mysql -u b3user -p"$DATABASE_USER_PASSWORD" <<DBSETUP
use b3
create table bin (
	bin binary(32) not null,
	name varchar(255) character set utf8 not null,
	ref boolean not null default false,
	primary key (bin)
);

create table b2b (
	bin binary(32) not null,
	block binary(32) not null,
	primary key (bin,block)
);

create table block (
	block binary(32) not null,
	type varchar(16) not null,
	rep varchar(255) character set utf8 not null,
	primary key (block)
);
DBSETUP


# bootstrap stuff
cd b3db/flask/static
wget https://github.com/twbs/bootstrap/releases/download/v4.4.1/bootstrap-4.4.1-dist.zip -c
unzip -o bootstrap-4.4.1-dist.zip
mkdir jquery-3.4.1-dist/js
wget https://code.jquery.com/jquery-3.4.1.min.js -O jquery-3.4.1-dist/js/jquery-3.4.1.min.js -c


