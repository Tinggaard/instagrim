drop table if exists users;
create table users (
    'id' INTEGER primary key,
    'username' TEXT not null,
    'password' TEXT not null
);
