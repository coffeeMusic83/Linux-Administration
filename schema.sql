-- Kävijälaskurin tietokanta (MariaDB)
CREATE TABLE IF NOT EXISTS counter (
    id INT PRIMARY KEY,
    visits INT NOT NULL DEFAULT 0
);
INSERT IGNORE INTO counter (id, visits) VALUES (1, 0);
