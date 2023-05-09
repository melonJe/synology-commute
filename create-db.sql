-- Local database definition.
DROP DATABASE IF EXISTS commute;

CREATE DATABASE commute;

USE local_db;

DROP TABLE IF EXISTS books;

CREATE TABLE books (
  id int(10) NOT NULL,
  title varchar(30) NOT NULL DEFAULT '',
  PRIMARY KEY (id)
);

INSERT INTO books VALUES(1, 'Book 1');
INSERT INTO books VALUES(2, 'Book 2');