import sqlite3

def clear_database():
    # Connect to SQLite database
    conn = sqlite3.connect('railway.db')
    cursor = conn.cursor()

    # Truncate the tables (delete all rows)
    cursor.execute('DELETE FROM book')
    cursor.execute('DELETE FROM train')
    cursor.execute('DELETE FROM user')

    # Commit the transaction
    conn.commit()

    # Close the connection
    conn.close()
    print("All data has been cleared from the tables!")

if __name__ == "__main__":
    clear_database()
