import sqlite3

def create_database():
    # Connect to SQLite (it will create the database file if it doesn't exist)
    conn = sqlite3.connect('railway.db')
    cursor = conn.cursor()

    # Create the 'user' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create the 'train' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS train (
            train_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            from_station TEXT NOT NULL,
            to_station TEXT NOT NULL,
            depart_time TEXT NOT NULL,
            available_seats INTEGER NOT NULL,
            amount_per_seat INTEGER NOT NULL
        )
    ''')

    # Create the 'book' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            train_id INTEGER,
            status TEXT ,
            no_of_seats INTEGER NOT NULL,
            total_amount INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES user(user_id),
            FOREIGN KEY(train_id) REFERENCES train(train_id)
        )
    ''')

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    print("Database and tables created successfully!")

if __name__ == "__main__":
    create_database()
