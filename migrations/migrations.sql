-- root, root01

CREATE DATABASE fastapi_db;

CREATE USER 'fastapi_app'@'%' IDENTIFIED BY 'fastapi01';

GRANT ALL PRIVILEGES ON fastapi_review.* TO 'fastapi_app'@'%';

-- logout from root, then login as fastapi_app

CREATE TABLE IF NOT EXISTS user_info (
    id INT AUTO_INCREMENT NOT NULL KEY
    , username VARCHAR(64) NOT NULL
    , password VARCHAR(256) NOT NULL
    , picture VARCHAR(256)
    , privilege SMALLINT NOT NULL DEFAULT 0
    , created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    , updated_at TIMESTAMP
    , last_login_at TIMESTAMP
);
