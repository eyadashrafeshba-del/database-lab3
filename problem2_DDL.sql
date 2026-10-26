DROP DATABASE IF EXISTS libraryDB;
CREATE DATABASE libraryDB;

USE libraryDB;

CREATE TABLE Author(
	author_id INT NOT NULL AUTO_INCREMENT,
    `name` NVARCHAR(150) NOT NULL,
    country NVARCHAR(150) NOT NULL,
    image_url NVARCHAR(500) NULL,
    CONSTRAINT PK_Author PRIMARY KEY (author_id)
);
CREATE TABLE Book(
	book_id INT NOT NULL AUTO_INCREMENT,
    title NVARCHAR(150) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    author_id INT NOT NULL,
    image_url NVARCHAR(500) NULL,
    CONSTRAINT PK_Book PRIMARY KEY (book_id),
    CONSTRAINT FK_Book_author_id FOREIGN KEY (author_id) REFERENCES Author(author_id)
        ON DELETE CASCADE,
    CONSTRAINT CK_Book_price CHECK(price > 0.0)
);
