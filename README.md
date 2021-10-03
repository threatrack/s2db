# s2db: Software Sequences Database

**This is a prototype still in development.**

## Install

### Docker

- Ubuntu 20.04:

```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose
```

- Once Docker is installed you can  build the containers via:

```
sudo docker-compose build
```

- Fix permissions on persistent data directory:

```
sudo chown $USER -R s2db-data-web/
```

- Then you can run the service(s) via:

```
S2DB_DOCKER_UID=$(id -u) docker-compose up --remove-orphans
```

- Visit `https://localhost/`.

**If you run the Docker as is you do not need to configure anything else.**

### Config file

Edit [`s2db.conf`](s2db/s2db.conf) and place in one of the paths traversed in [`common/config.py`](s2db/common/config.py).


## Architecture

```
services.sequencer +-- runs endless service while loop
                   |
                   +-- uses -- common.config, common.log, db.engine
                   +-- checks for tasks via -- db_sequencer_task_get_and_set_start
                   |
                   +-- uses plugins from -- services.sequencers.{pe,strings}
                   |
                   +-- commits extracted sequences to db via -- db.query

services.unpacker +-- runs endless serivce while loop
                  |
                  +-- uses -- common.config, common.log, db.engine
                  +-- checks for tasks via -- TODO
                  |
                  +-- uses plugins from -- services.unpacker.{pe,strings}
                  |
                  |-- stores unpacked software components to config["storage"]["path"]
                  +-- adds new sequencer task via -- db_sequencer_task_add

web.app +-- runs Flask app
        |
        +-- uses common.config, common.log, db.engine, web/templates
	|
	+-- 
	|
	+-- adds new sequencer task via -- db_sequencer_task_add

```

## Debugging

### API

- Run web.app on its own for development and debugging:

```
. venv/bin/active
pip install -r requirements-web.txt
docker-compose -f docker-compose-dev.yml up
cp s2db/s2db.conf s2db.conf
vim s2db.conf # point db.uri to localhost, storage.path to s2db-data-web/uploads, and log.path to s2db-data-web/s2db.log
python3 s2db/web/app.py
```

- You can then access a development version of the web interface and API on `localhost:5000` (running in parallel to the production version running in the Docker container).

- Run services.sequencer on its own for development and debugging:

```
. venv/bin/active                                                                
pip install -r requirements-web.txt                                              
docker-compose -f docker-compose-dev.yml up                                      
cp s2db/s2db.conf s2db.conf                                                      
vim s2db.conf # point db.uri to localhost, storage.path to s2db-data-web/uploads, and log.path to s2db-data-web/s2db.log
python3 s2db/services/sequencer.py -w 2
```

- Upload files via API:

```
curl -F file=@tests/aO0_x64.exe http://localhost:5000/api/v0/software
```

### DB

```
docker exec -it s2db_db bash
root@b4364911b35b:/# psql -d s2db -U s2db_user
psql (13.3 (Debian 13.3-1.pgdg100+1))
Type "help" for help.

s2db=# select * from softwares;
[...]
```

## TODO

- TODO: `app.html`: Add class, family and name setting
- TODO: `app.html`: Add familysequences display
- TODO: `app.html`: YARA/ClamAV export: 1. select sequences; 2. export to YARA or ClamAV
- TODO: Unpacker service via CAPE sandbox
- TODO: `app.html`: Better group softwaressequences display
	- `softwaressequencesgrouped` API endpoint already exists, but it requires proper displaying
- TODO: `app.html`: Sorting options
- TODO: `app.html`: cache API results so navigation won't cause new API request but uses previous cached results 
- FIXME: Error handling
	- FIXME: Error handling in sequencer.py, sequencers/pe.py, ...
- TODO: Check IDA and Ghidra basic block models for compatibility to ease plugin development employing our API for basic block lookup.
- FIXME: handle wait for DB and Docker container dependencies
	- FIXME: `app.py`: Add proper wait for DB
	- FIXME: `sequencer.py`: Add proper wait for DB
- TODO: Improve services
	- TODO: Change endless while-work-sleep-loop to task queue or similar
	- FIXME: Store relative path in DB for sequencers to get files
	- TODO: maybe handle worker tasks via API instead of DB queries; results could also be added via API; this would allow running the sequencer services distributed over multiple systems

