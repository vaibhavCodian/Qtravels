import pymysql.cursors
import os
import base64
import tempfile
# from dotenv import load_dotenv

# Load environment variables from the .env file
# load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = 3306

client_cert = os.getenv('DB_SSL_CERT', '')
client_key = os.getenv('DB_SSL_KEY', '')
server_ca = os.getenv('DB_SSL_CA', '')

with tempfile.NamedTemporaryFile(mode='w', delete=False) as client_cert_file:
    client_cert_file.write(client_cert)
    client_cert_file_path = client_cert_file.name

with tempfile.NamedTemporaryFile(mode='w', delete=False ) as client_key_file:
    client_key_file.write(client_key)
    client_key_file_path = client_key_file.name

with tempfile.NamedTemporaryFile(mode='w', delete=False) as server_ca_file:
    server_ca_file.write(server_ca)
    server_ca_file_path = server_ca_file.name

print(DB_HOST)

def create_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        ssl={
            'cert': client_cert_file_path,
            'key': client_key_file_path,
            'ca': server_ca_file_path,
            'check_hostname': False 
        }
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


# Insert
# INSERT INTO tours (tour_name, destination, start_date, end_date, max_capacity, details, image_url)
# VALUES
#     ('Sacred Kedarnath Pilgrimage', 'Kedarnath, Uttarakhand', '2023-11-01', '2023-11-07', 50, 'Embark on a spiritual journey to the holy Kedarnath Temple nestled in the Himalayas.', 'https://images.pexels.com/photos/11305767/pexels-photo-11305767.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
#     ('Vrindavan Spiritual Retreat', 'Vrindavan, Uttar Pradesh', '2023-12-01', '2023-12-10', 30, 'Experience the divine atmosphere of Vrindavan and connect with your spiritual self.', 'https://media.gettyimages.com/id/1247805327/photo/hindu-devotees-are-seen-throwing-colourful-powders-inside-radhaballav-temple-of-vrindavan.jpg?s=612x612&w=0&k=20&c=jPIM1QrZGlaghjvgMFGjdQA-QJe1JFGOqMtG0JT9Xd0='),
#     ('Kaichi Dham Meditation Expedition', 'Dehradun, Uttarakhand', '2024-01-15', '2024-01-21', 20, 'Discover peace and tranquility in the serene surroundings of Kaichi Dham in Dehradun.', 'https://th.bing.com/th/id/OIP.8Sy5DXYuDmuYlPP03757fgHaDf?pid=ImgDet&rs=1'),
#     ('Divine Kedarnath Yatra', 'Kedarnath, Uttarakhand', '2024-02-10', '2024-02-17', 40, 'Join this sacred journey to Kedarnath and experience the profound spirituality of the region.', 'https://images.pexels.com/photos/11305767/pexels-photo-11305767.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
#     ('Spiritual Bliss in Vrindavan', 'Vrindavan, Uttar Pradesh', '2024-03-05', '2024-03-12', 25, 'Immerse yourself in the blissful atmosphere of Vrindavan and explore its sacred sites.', 'https://th.bing.com/th?id=OSK.HERO3LZ_AT5NZt9G1v5-62SpTUETdqTNd4x-sKtEQLnKTk4&w=472&h=280&c=1&rs=2&o=6&pid=SANGAM'),
#     ('Kaichi Dham Yoga Retreat', 'Dehradun, Uttarakhand', '2024-04-02', '2024-04-09', 35, 'Rejuvenate your mind and body with yoga and meditation in the scenic beauty of Kaichi Dham.', 'https://images.pexels.com/photos/11305767/pexels-photo-11305767.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
#     ('Kedarnath Spiritual Sojourn', 'Kedarnath, Uttarakhand', '2024-05-10', '2024-05-17', 30, 'Experience the spiritual essence of Kedarnath through meditation and introspection.', 'https://images.pexels.com/photos/11305767/pexels-photo-11305767.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
#     ('Vrindavan Cultural Expedition', 'Vrindavan, Uttar Pradesh', '2024-06-01', '2024-06-07', 40, 'Explore the rich cultural heritage of Vrindavan through this enlightening cultural expedition.', 'https://images.pexels.com/photos/11305767/pexels-photo-11305767.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1'),
#     ('Kaichi Dham Nature Retreat', 'Dehradun, Uttarakhand', '2024-07-15', '2024-07-22', 28, 'Connect with nature and spirituality in the tranquil environment of Kaichi Dham.', 'kaichi_dham_nature_image'),
#     ('Kedarnath Adventure and Pilgrimage', 'Kedarnath, Uttarakhand', '2024-08-10', '2024-08-17', 25, 'Combine adventure with spirituality on this unique journey to Kedarnath.', 'https://images.pexels.com/photos/11305767/pexels-photo-11305767.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1');