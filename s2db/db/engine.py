import os
import sys
import sqlalchemy
import datetime

_S2DB_ROOT = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
sys.path.append(_S2DB_ROOT)

from common.config import config
from common.log import get_logger

logger = get_logger(__name__)

engine = sqlalchemy.create_engine(config["db"]["uri"], echo=False)
connection = engine.connect()


DB_VERSION = 0


def db_insert(query, params={}):
	query = sqlalchemy.sql.text(query)
	connection.execute(query,params)


def db_select(query, params={}):
	query = sqlalchemy.sql.text(query)
	cursor = connection.execute(query,params)
	rows = cursor.fetchall()
	return [(dict(row.items())) for row in rows]


def db_insertfromfile(file):
	querys = open(_S2DB_ROOT+"/db/"+file,"r").read()
	with engine.begin() as transaction:
		# TODO: make this better, but psycopg2 doesn't allow mulitple queries
		for query in querys.split(";"):
			query = query.strip()
			if query and query != "":
				q = sqlalchemy.sql.text(query)
				transaction.execute(query)


def db_get_version():
	db_insert("create table if not exists versions (version int not null unique)")
	versions = db_select("select * from versions order by version asc limit 1")
	if versions:
		return versions[0]['version']
	return None


def db_init():
	if not config["db"]["uri"].startswith("postgresql"):
		raise Exception("Only postgresql DB supported")
	version = db_get_version()
	if version is None:
		# DB does not exist
		db_insertfromfile("create.sql")
	elif version != DB_VERSION:
		if version > DB_VERSION:
			raise Exception("DB version from the future. DB downgrade not supported.")
		for v in range(version, DB_VERSION):
			logger.info("Migrating from "+str(v)+" to "+str(v+1))
			print("Migrate: "+str(v))
			db_insertfromfile("migrations/"+str(v+1)+".sql")
	version = db_get_version()
	if version is None or version != DB_VERSION:
		raise Exception("DB migration or creation failed")


def db_sequencer_task_add(hash, path, parent=None, cls=None, family=None, name=None, time=int(datetime.datetime.utcnow().timestamp())):
	db_insert("insert into sequencer_tasks (hash, path, parent, class, family, name, time_added) values (:hash, :path, :parent, :class, :family, :name, :time)",
		{"hash":hash, "path":path, "parent":parent, "class":cls, "family":family, "name":name, "time":time})


def db_sequencer_task_get_and_set_start(worker, time=int(datetime.datetime.utcnow().timestamp())):
	db_insert("update sequencer_tasks set time_started=:time, worker=:worker where path = (select path from sequencer_tasks where worker is null order by time_added asc limit 1)",
		{"time":time, "worker":worker})
	rows = db_select("select path, parent, class, family, name from sequencer_tasks where worker=:worker limit 1",
		{"worker":worker})
	if rows == []:
		return None
	return rows[0]


def db_sequencer_task_remove(path):
	db_insert("delete from sequencer_tasks where path=:path", {"path":path})


def db_sequences_add(software, sequences):
	query_sequences = "insert into sequences (type, hash, representation, signature) values (:type, :sequence, :representation, :signature) on conflict do nothing"
	query_softwaressequences = "insert into softwaressequences (software, sequence) values (:software, :sequence)"
	for sequence in sequences:
		db_insert(query_sequences, {"type":sequence["type"], "sequence":sequence["sequence"], "representation":sequence["representation"], "signature":sequence["signature"]})
		db_insert(query_softwaressequences, {"software":software, "sequence":sequence["sequence"]})


def db_software_add(hash, mime, parent=None, cls=None, family=None, name=None, first_seen=int(datetime.datetime.utcnow().timestamp())):
	db_insert("insert into softwares (hash, mime, parent, class, family, name, first_seen) values (:hash, :mime, :parent, :class, :family, :name, :first_seen)",
		{"hash":hash, "mime":mime, "parent":parent, "class":cls, "family":family, "name":name, "first_seen":first_seen})


def db_get_softwares(limit=10000,offset=0):
	return db_select("select * from softwares limit :limit offset :offset",{"limit":limit,"offset":offset})


def db_get_software(hash):
	softwares = db_select("select * from softwares where hash=:hash",{"hash":hash})
	if softwares:
		return softwares[0]
	return None


def db_get_softwaretree(hash):
	return db_select("select m.hash,p.hash parent_hash,p.class parent_class,p.family parent_family,p.name parent_name,c.hash child_hash,c.class child_class,c.family child_family,c.name child_name from softwares m left join softwares p on m.parent = p.hash left join softwares c on m.hash = c.parent where m.hash=:hash",
		{"hash":hash})


def db_software_exists(hash):
	return len(db_select("select * from softwares where hash=:hash",{"hash":hash})) > 0


def db_get_softwaressequencesgrouped(hash):
	return db_select("""
select * from (
select class,jsonb_agg(data) as data from (
select class,jsonb_build_object('family',family,'data',json_agg(data)) as data from (
select class,family,jsonb_build_object('type',type,'data',jsonb_agg(data)) as data from (
select array_agg(distinct class) as class,array_agg(distinct family) as family,b.type,jsonb_build_object('sequence',a.sequence,'representation',b.representation,'signature',b.signature,'softwares',jsonb_agg(data)) as data from (
select c.class,c.family,a.sequence,jsonb_build_object('name',c.name,'hash',c.hash) as data
from softwaressequences a
join softwaressequences b on a.software = :hash and a.sequence = b.sequence
join softwares c on c.hash != :hash and b.software = c.hash
group by c.class,c.family,a.sequence,c.name,c.hash,data ) as a 
join sequences b on a.sequence = b.hash
group by b.type,a.sequence,b.representation,b.signature) as a
group by class,family,type ) as a
group by class,family order by cardinality(family)) as a
group by class order by cardinality(class)) as a where cardinality(class) <= 1
	""",
		{'hash':hash})


def db_get_softwaressequences(hash):
	return db_select("""
select class,family,type,representation,signature,name,c.hash from softwaressequences a join softwaressequences b on a.software = :hash and a.sequence = b.sequence join softwares c on c.hash != :hash and b.software = c.hash join sequences d on a.sequence = d.hash
	""",
		{'hash':hash})


def db_set_classfamilyname(hash, cls, family, name=None):
	if name:
		db_insert("update softwares set class=:class, family=:family, name=:name where hash = :hash",
			{'class':cls, 'family':family, 'name':name, 'hash':hash})
	else:
		db_insert("update softwares set class=:class, family=:family where hash = :hash",
			{'class':cls, 'family':family, 'hash':hash})


# TODO: find better place for this
os.makedirs(config['storage'].get('path', raw=True), exist_ok=True)
db_init()

