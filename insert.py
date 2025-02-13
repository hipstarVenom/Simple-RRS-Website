import sqlite3

def insert_trains():
    # Connect to the SQLite database
    conn = sqlite3.connect('railway.db')
    cursor = conn.cursor()

    # List of sample trains in Tamil Nadu (train name, from station, to station, depart time, available seats, amount per seat)
    trains = [
        ("Vaigai Express", "Madurai", "Chennai", "06:00", 100, 500),
        ("Rockfort Express", "Trichy", "Chennai", "07:30", 120, 550),
        ("Chendur Express", "Chennai", "Madurai", "08:15", 150, 600),
        ("Kochuveli Express", "Kochi", "Chennai", "09:00", 80, 650),
        ("Duronto Express", "Coimbatore", "Chennai", "10:30", 200, 750),
        ("Madura Express", "Madurai", "Coimbatore", "11:00", 90, 500),
        ("Cochin Mail", "Chennai", "Kochi", "14:00", 110, 600),
        ("Nilgiri Express", "Coimbatore", "Ooty", "15:00", 70, 550),
        ("Kanniyakumari Express", "Chennai", "Kanyakumari", "17:30", 130, 800),
        ("Udhagamandalam Express", "Chennai", "Ooty", "19:00", 60, 700)
    ]

    # Insert data into the 'train' table
    cursor.executemany('''
        INSERT INTO train (name, from_station, to_station, depart_time, available_seats, amount_per_seat)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', trains)

    # Commit the transaction
    conn.commit()

    # Close the connection
    conn.close()
    print("Trains inserted successfully!")

if __name__ == "__main__":
    insert_trains()
