import sqlite3

def print_table(table_name, columns):
    """Helper function to print each table in a nice tabular format."""
    conn = sqlite3.connect('railway.db')
    cursor = conn.cursor()

    # Fetch all rows from the given table
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Print table header
    print(f"{table_name.capitalize()} Table:")
    print(f"{' | '.join(columns)}")
    print("=" * (len(' | '.join(columns)) + 3))

    # Print rows
    if rows:
        for row in rows:
            print(' | '.join(str(cell) for cell in row))
    else:
        print("No data found in this table.")

    print("\n" + "="*50)  # Separator for better readability
    conn.close()


def print_all_tables():
    # Columns for each table
    user_columns = ['user_id', 'name', 'email', 'password']
    train_columns = ['train_id', 'train_name', 'from_station', 'to_station', 'depart_time', 'available_seats', 'amount_per_seat']
    book_columns = ['book_id', 'user_id', 'train_id', 'status', 'no_of_seats', 'total_amount']

    # Print data from each table
    print_table('user', user_columns)
    print_table('train', train_columns)
    print_table('book', book_columns)


if __name__ == "__main__":
    print_all_tables()
