import mysql.connector

def drop_unused_tables():
    # Connect to MySQL
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="srihitha",
        database="moneymate"
    )
    
    cursor = db.cursor()
    
    # Drop tables in correct order (group_member first due to foreign key)
    try:
        print("Dropping unused tables...")
        
        # Drop group_member first as it depends on group
        cursor.execute("DROP TABLE IF EXISTS group_member")
        print("- Dropped group_member table")
        
        # Then drop group table
        cursor.execute("DROP TABLE IF EXISTS `group`")
        print("- Dropped group table")
        
        db.commit()
        print("\nUnused tables have been successfully removed!")
        
    except mysql.connector.Error as err:
        print(f"An error occurred: {err}")
        db.rollback()
    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    # Ask for confirmation
    response = input("This will remove unused tables (group, group_member). Are you sure? (yes/no): ")
    if response.lower() == 'yes':
        drop_unused_tables()
    else:
        print("Operation cancelled.") 