import mysql.connector

def show_tables():
    # Connect to MySQL
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="srihitha",
        database="moneymate"
    )
    
    cursor = db.cursor()
    
    # Show all tables
    cursor.execute("SHOW TABLES")
    print("\nTables in the database:")
    tables = cursor.fetchall()
    for table in tables:
        print(f"- {table[0]}")
    
    cursor.close()
    db.close()

if __name__ == '__main__':
    show_tables() 