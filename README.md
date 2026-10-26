📚 Library — Lab 3
It manages authors and their books, with full add / edit / remove support and image upload (book covers and author photos).

✨ Features
ID	Feature
F2.1	Show a table of books (with each book's author_id) and a table of authors
F2.2	Add a book and add an author
F2.3	Edit a book and edit an author
F2.4	Remove a book
F2.5	Remove an author (all of the author's books are deleted too, via ON DELETE CASCADE)
Bonus	Upload a cover image for each book and a photo for each author
🗂️ Project structure

lab3-<student-id>/

├── problem2_DDL.sql        # Problem 2: library database (AUTHOR, BOOK)
├── problem2_DML.sql        # Problem 2: seed data (3 authors, 6 books)
├── README.md
└── website/
    ├── app.py              # Flask routes
    ├── db.py               # MySQL connection helpers
    ├── requirements.txt
    ├── .env.example        # copy to .env and fill in your password
    ├── templates/          # HTML pages (Jinja2)
    └── static/             # style.css and uploaded images

🗄️ Database schema (Problem 2)
AUTHOR (author_id, name, country, photo)
BOOK   (book_id, title, price, author_id, cover)
BOOK.author_id is a foreign key to AUTHOR.author_id with ON DELETE CASCADE.
photo and cover store the file name of the uploaded image (the files live in website/static/uploads/).

⚙️ Requirements
Python 3.9+
MySQL Server 8.0+ and the mysql command-line client
pip (comes with Python)
🚀 How to run (step by step)
1. Clone the repository
bash
git clone <repository-url>
cd lab3-2304043-2304113
2. Build the databases

Run the scripts in this order. Each DDL script drops and recreates its database, so you can re-run it at any time.

bash
# Problem 2 (library database, used by the website)
mysql -u root -p < problem2_DDL.sql
mysql -u root -p < problem2_DML.sql

To check the data by hand:

bash
mysql -u root -p library
mysql> SELECT * FROM AUTHOR;
mysql> SELECT * FROM BOOK;
3. Configure the connection
bash
cd website
cp .env.example .env        # on Windows: copy .env.example .env

Open .env and set your MySQL password:

DB_HOST=localhost
DB_USER=root
DB_PASSWORD= ########
DB_NAME=library
4. Install the dependencies
bash
python -m venv venv
source venv/bin/activate    # on Windows: venv\Scripts\activate
pip install -r requirements.txt
5. Start the website
bash
python app.py

Open http://127.0.0.1:5000 in your browser.

🧪 Quick test
Open Books and Authors: you should see the 6 books and 3 authors from the seed data.
Add a new author, then add a book for that author (optionally upload an image).
Edit the book and the author.
Remove a book.
Remove an author: their books disappear from the Books page as well.
🛠️ Troubleshooting
Problem	Fix
Access denied for user 'root'	Check DB_PASSWORD in website/.env.
Unknown database 'library'	Run problem2_DDL.sql first.
ModuleNotFoundError	Activate the virtual environment and run pip install -r requirements.txt.
Can't connect to MySQL server	Make sure the MySQL service is running.
Port 5000 already in use	Stop the other program, or change the port in the last line of app.py.
👤 Author
Name: Ezz Eldeen Gamal
Name: Eyad Ashrf
Student ID: 2304043
Student ID: 2304113
