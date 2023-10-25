import pymysql.cursors
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = 3306

print("db_name below")
print(DB_NAME)

def create_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def table_exists(table_name, connection):
    with connection.cursor() as cursor:
        # Check if the table exists
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        return cursor.fetchone() is not None

def create_tables(connection):
    with connection.cursor() as cursor:
        # Create the tours table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tours (
                id INT PRIMARY KEY AUTO_INCREMENT,
                tour_name VARCHAR(255) NOT NULL,
                destination VARCHAR(255) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                max_capacity INT NOT NULL,
                details TEXT,
                image_url VARCHAR(255),
                CHECK (start_date < end_date)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Booking (
                id INT PRIMARY KEY AUTO_INCREMENT,
                tour_id INT NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                contact_number VARCHAR(20) NOT NULL,
                head_count INT NOT NULL,
                -- Add other columns as needed
                FOREIGN KEY (tour_id) REFERENCES tours(id)
            )
        """)




def load_tours_from_db():
    tours = []
    try:
        # Use a context manager for the database connection
        with create_connection() as connection:
            with connection.cursor() as cursor:

                if not table_exists('tours', connection):
                    create_tables(connection)
                sql = "SELECT * FROM tours"
                cursor.execute(sql)
                results = cursor.fetchall()
                print("results")
                for row in results:
                    tours.append(row)

    except pymysql.MySQLError as e:
        # Handle MySQL errors
        print(f"MySQL error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return tours

def load_tour_from_db(id):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tours WHERE id = %s", (id,))
            row = cursor.fetchone()

            if row is None:
                return None
            else:
                return dict(row)
            

def add_booking_to_db(tour_id, data):
    try:

        print("adding to db.")
        with create_connection() as connection:
            with connection.cursor() as cursor:

                query = """
                    INSERT INTO Booking (tour_id, full_name, email, contact_number, head_count)
                    VALUES (%s, %s, %s, %s, %s)
                """

                cursor.execute(query, (
                    tour_id,
                    data['full_name'],
                    data['email'],
                    data['contact_number'],
                    data['head_count']
                ))
                connection.commit()
                print("added to db.")
    except pymysql.MySQLError as e:
        # Handle MySQL errors
        print(f"MySQL error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


