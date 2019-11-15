drop table if exists users;
create table users (
    'id' INTEGER primary key,
    'username' TEXT not null unique,
    'password' TEXT not null
);


drop table if exists posts;
create table posts (
    'id' TEXT primary key,
    'user_id' INTEGER not NULL,
    'url' TEXT not null,
    'message' TEXT,
    'date' INTEGER not NULL
);
