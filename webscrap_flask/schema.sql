-- drop existing tables 
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post_urls;

-- creating new empty tables
CREATE TABLE user(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post_urls(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   user_id INTEGER NOT NULL,
   created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   title TEXT NOT NULL,
   url TEXT NOT NULL,
   FOREIGN KEY (user_id) REFERENCES user(id)

);