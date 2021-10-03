insert into versions values (1);
alter table softwares add name varchar(256);
delete from versions where version != 1;
