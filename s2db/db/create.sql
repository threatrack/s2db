create table if not exists versions (
	version int not null unique
);
insert into versions values (0);

create table if not exists sequencer_tasks (
	hash         char(64) not null unique,
	path         text     not null unique,
	parent       char(64),
	class        varchar(64),
	family       varchar(64),
	name         varchar(256),
	time_added   int      not null,
	worker       int,
	time_started int,
	error        text
);

create table if not exists unpacker_tasks (
	hash         char(64) not null unique,
	path         text     not null unique,
	time_added   int      not null,
	worker       int,
	time_started int,
	error        text
);

create table if not exists softwares (
	hash       char(64)     not null unique,
	first_seen int          not null,
	mime       varchar(256) not null,
	parent     char(64),
	class      varchar(64),
	family     varchar(64),
	name       varchar(256)
);

create table if not exists softwaressequences (
	software char(64) not null,
	sequence char(64) not null
);

create table if not exists sequences (
	hash           char(64)    not null unique,
	type           varchar(16) not null,
	representation text        not null,
	signature      text        not null
);

create index if not exists idx_software_hash               on softwares (hash);
create index if not exists idx_softwaressequences_sequence on softwaressequences (software);
create index if not exists idx_softwaressequences_sequence on softwaressequences (sequence);
create index if not exists idx_sequences_hash              on sequences (hash);

analyze softwares;
analyze softwaressequences;
analyze sequences;

