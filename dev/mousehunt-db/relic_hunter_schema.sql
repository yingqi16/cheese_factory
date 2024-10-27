-- docker compose will only create one db upon initialisation

CREATE TABLE if not exists relic_hunter (date_utc0 date not null, id VARCHAR(100), name VARCHAR(100),
       article VARCHAR(100), region VARCHAR(100), title VARCHAR(100), PRIMARY KEY (date_utc0));


