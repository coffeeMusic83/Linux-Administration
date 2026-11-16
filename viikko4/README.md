# Week 4: Server cloning, backups and database replication

Server **A** (`195.148.21.16`) runs the Week 2 visitor counter and the Week 3 report.
Server **B** (`128.214.255.114`) was created from a cPouta snapshot of A and works as
a backup target and a read-only MariaDB replica.

- Server A counter (increments): http://195.148.21.16/viikko2/
- Server B replica page (read-only + documentation): http://128.214.255.114/viikko4/

```
A: /viikko2/ → Flask → MariaDB (master, binlog) ══ replication ══> B: MariaDB (replica, read_only) → Flask → /viikko4/
A: /var/www/html ══ cron every hour (tar over SSH) ══> B: /srv/backups/server-a/
```

Replication and backups use the cPouta private network (A = `192.168.1.204`, B = `192.168.1.64`).

## Files

| File | Server | Purpose |
|---|---|---|
| `backup.sh` | A | Packs `/var/www/html` and streams it to B as `html-YYYYMMDD-HHMMSS.tar.gz`, logs SUCCESS/FAILED, keeps the newest 48 |
| `crontab.txt` | A | Crontab of user `ubuntu` (`7 * * * *` = backup every hour at minute 7) |
| `server-a/60-replication.cnf` | A | MariaDB master settings → `/etc/mysql/mariadb.conf.d/` |
| `server-b/60-replication.cnf` | B | MariaDB replica settings (`read_only = 1`) → `/etc/mysql/mariadb.conf.d/` |
| `server-b/app.py` | B | Flask page that only reads the counter from B's local replica |
| `server-b/viikko4.service` | B | systemd service (Gunicorn on `127.0.0.1:8001`) |
| `server-b/nginx-default.conf` | B | Nginx site config, `/viikko4/` → `127.0.0.1:8001` |
| `server-b/database-users.sql` | A + B | Database users and privileges (passwords removed) |

## Setup summary

1. **Server B:** snapshot of A in cPouta → new instance from the snapshot, same flavor, network,
   security group and key pair → new floating IP. On B: `hostnamectl set-hostname server-b`,
   `systemctl disable --now viikko2.service`.
2. **Firewall:** cPouta security group rule TCP 3306 ingress only from `192.168.1.64/32`.
3. **Replication:** master config on A, replication user `repl@192.168.1.64`, replica config on B,
   start position taken from `mariadb-dump --master-data=2`, then `CHANGE MASTER TO ...; START SLAVE;` on B.
4. **Backups:** Linux user `webbackup` on B (SSH key only, `from="192.168.1.204"`, `no-pty`),
   `/srv/backups/server-a` mode 700. SSH key `~/.ssh/backup_to_b` on A. `backup.sh` + cron on A.
5. **Replica page:** DB user `viikko4reader` (SELECT only), `app.py` + `viikko4.service` + Nginx on B.

## Checking the status

```bash
# B: replication
sudo mariadb -e "SHOW SLAVE STATUS\G" | grep -E "Slave_IO_Running|Slave_SQL_Running|Seconds_Behind"
# A: backup log
cat ~/backup-logs/backup.log
# B: backup files
sudo ls -l /srv/backups/server-a
```

## Why replication does not replace backups

Replication copies every change immediately, including mistakes such as a deleted table.
Timestamped backups keep older versions, so data can be restored to the state before the mistake.

## Not in this repository

Passwords (`.env` files), private SSH keys, SQL dumps and backup archives are never committed.
