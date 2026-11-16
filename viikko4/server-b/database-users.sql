-- Week 4 database users (passwords removed – replace <password> when setting up)

-- ===== Server A (master) =====
-- Replication user: can only read the binary log, and only from server B's private IP.
CREATE USER 'repl'@'192.168.1.64' IDENTIFIED BY '<password>';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'192.168.1.64';

-- ===== Server B (replica) =====
-- Read-only user for the /viikko4/ page: SELECT on the counter table + replication monitoring.
CREATE USER 'viikko4reader'@'localhost' IDENTIFIED BY '<password>';
GRANT SELECT ON viikko2.counter TO 'viikko4reader'@'localhost';
GRANT SLAVE MONITOR ON *.* TO 'viikko4reader'@'localhost';

FLUSH PRIVILEGES;

-- Start replication on B (values from: mariadb-dump --single-transaction --master-data=2 viikko2 counter)
-- CHANGE MASTER TO
--   MASTER_HOST='192.168.1.204',
--   MASTER_USER='repl',
--   MASTER_PASSWORD='<password>',
--   MASTER_LOG_FILE='mysql-bin.000001',
--   MASTER_LOG_POS=328;
-- START SLAVE;
