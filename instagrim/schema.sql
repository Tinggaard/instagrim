drop table if exists users;
create table users (
    'id' INTEGER primary key, -- unique id of user
    'username' TEXT not NULL unique, -- username
    'password' TEXT not NULL -- hashed password of user
);




drop table if exists posts;
create table posts (
    'id' TEXT primary key,  -- url without ending
    'user_id' INTEGER not NULL, -- id of user who posted
    'url' TEXT not NULL, -- url WITH ending
    'message' TEXT, -- message along with post
    'date' INTEGER not NULL -- POSIX timestamp
);


drop table if exists likes;
create table likes (
    'id' INTEGER primary key, -- unique id of entry
    'post_id' TEXT not NULL, -- id of post liked
    'user_id' INTEGER not NULL -- id of used who liked post
);

-- Not implemented yet...
drop table if exists followers;
create table followers(
    'id' INTEGER primary key, -- identifier
    'followee' INTEGER not NULL, -- user_id being followed
    'follower' INTEGER not NULL -- user_id of follower
);




-- Create 'admin' user with no password
INSERT INTO users (username, password) VALUES ('admin','e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');
