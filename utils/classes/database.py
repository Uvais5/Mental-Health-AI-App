
from kivy.app import App
import os
import sqlite3
import shutil
from kivy.utils import platform

from datetime import datetime
import os
from kivy.utils import platform
from kivy.app import App

def get_database_path():
    "names of path : base_dir,photo_path,"
    """Return paths for app database, main folder, and photo folder."""
    if platform == "android":
        # Android: Internal app storage
        base_dir = App.get_running_app().user_data_dir
    else:
        # PC: Local data folder
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))

    # Define main folder and subfolder paths
    print(base_dir)
    photo_path = os.path.join(base_dir, "photo")
    db_path = os.path.join(base_dir, "app.db")

    # Create folders if they don't exist
    os.makedirs(photo_path, exist_ok=True)

    return db_path, photo_path.replace("\\","\\"),base_dir.replace("\\","\\")



def init_db():
    """Initialize and copy the database to the correct path if it doesn't exist."""
    
    # Get database path
    db_path = get_database_path()
    print("here is database :",db_path[0])
    
    conn = sqlite3.connect(db_path[0])
    cursor = conn.cursor()
    print(f"✅ Database connected at: {db_path}")

    # Create tables if not exist
    create_tables(cursor, conn)

    return conn, cursor


def create_tables(cursor, conn):
    """Create necessary tables."""
    
    # Create journal table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal (
            date TEXT PRIMARY KEY,
            pre_journal TEXT,
            after_journal TEXT
        )
    """)

    # Create photos table (multiple photos per date)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            photo_path TEXT,
            FOREIGN KEY (date) REFERENCES journal (date)
        )
    """)

    # Create mood table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood (
            date TEXT UNIQUE,
            pre_mood TEXT,
            after_mood TEXT
        )
    """)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_affirmation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voice_affirmation_data TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loa_form_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,  -- Make date unique to prevent duplicates
            formdata TEXT
        )
    ''')
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS textfeild (
                id INTEGER PRIMARY KEY,
                acceptance TEXT,
                learned TEXT,
                priority TEXT,
                gen_image TEXT
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS anxiety_textfeild (
                id INTEGER PRIMARY KEY,
                release_audit TEXT,
                after_dare TEXT,
                gen_image TEXT
            )
        """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS testresult (
            testtype TEXT PRIMARY KEY,
            descriptions TEXT
        )
    """)
    
    #cursor.execute("INSERT OR IGNORE INTO textfeild (id, acceptance, learned, priority) VALUES (1, '', '','')")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS thought_reframing_user_form (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            situation TEXT NOT NULL,
            thoughts TEXT NOT NULL,
            feelings TEXT NOT NULL,
            worst_case TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS imgery_cbt_user_form (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            situation TEXT NOT NULL,
            mental_img TEXT NOT NULL,
            exploration TEXT NOT NULL,
            emotional TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    # Commit changes
    conn.commit()
    print("Database tables created successfully!")
def save_loa_form_data(data):
        """Save or update LoA form data in journal.db with auto-generated date."""
        
        # Connect to database (or create if not exists)
        db_path = get_database_path()[0]
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(data)
        
        # Generate today's date in YYYY-MM-DD format
        date = datetime.today().strftime("%Y-%m-%d")
        
        # Check if data already exists for today's date
        cursor.execute('SELECT id FROM loa_form_data WHERE date = ?', (date,))
        
        existing_entry = cursor.fetchone()
        if existing_entry:
            # Update existing record
            cursor.execute('''
                UPDATE loa_form_data
                SET formdata = ?
                WHERE date = ?
            ''', (data, date))
            print(f"Data for {date} updated successfully!")
        else:
            # Insert new record if not exists
            cursor.execute('''
                INSERT INTO loa_form_data (date, formdata)
                VALUES (?, ?)
            ''', (date, data))
            print(f"Data for {date} inserted successfully!")
        
        # Commit and close the connection
        conn.commit()
        conn.close()
def show_loa_form_data():

    db_path = get_database_path()
    # Connect to database
    conn = sqlite3.connect(db_path[0])
    cursor = conn.cursor()
    
    # Fetch all records from loa_form_data table
    cursor.execute('SELECT date, formdata FROM loa_form_data ORDER BY date DESC')
    rows = cursor.fetchall()
    
    # Close the connection
    conn.close()
    
    # Check if data exists
    if rows:
        print("LoA Form Data:")
        for row in rows:
            date, formdata = row
        
    else:
        print("No data found in loa_form_data.")
        formdata = "no_data"
    return formdata
def add_or_update_voice_affirmation_data( voice_data):
        """Check if voice_affirmation table exists and insert or update data."""
        db_path = get_database_path()
        # Connect to the database
        conn = sqlite3.connect(db_path[0])
        cursor = conn.cursor()
        
        # Check if the voice_affirmation table exists
        cursor.execute('''
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='voice_affirmation'
        ''')
        
        table_exists = cursor.fetchone()
        
        # Create the table if it does not exist
        if not table_exists:
            print("Table does not exist. Creating voice_affirmation table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS voice_affirmation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    voice_affirmation_data TEXT
                )
            ''')
            print("voice_affirmation table created successfully.")
            
            # Insert data after creating the table
            cursor.execute('''
                INSERT INTO voice_affirmation (voice_affirmation_data)
                VALUES (?)
            ''', (voice_data,))
            print(f"Inserted initial voice affirmation: {voice_data}")
        
        else:
            # Check if any record exists
            cursor.execute('SELECT id FROM voice_affirmation ORDER BY id DESC LIMIT 1')
            existing_entry = cursor.fetchone()
            
            if existing_entry:
                # Update the latest record with new data
                cursor.execute('''
                    UPDATE voice_affirmation
                    SET voice_affirmation_data = ?
                    WHERE id = ?
                ''', (voice_data, existing_entry[0]))
                print(f"Voice affirmation data updated successfully: {voice_data}")
            else:
                # Insert if no record is found
                cursor.execute('''
                    INSERT INTO voice_affirmation (voice_affirmation_data)
                    VALUES (?)
                ''', (voice_data,))
                print(f"Inserted new voice affirmation: {voice_data}")
        
        # Commit and close the connection
        conn.commit()
        conn.close()
def show_voice_affirmation_data():
        """Fetch and display the latest voice affirmation data."""
        db_path = get_database_path()
        # Connect to the database
        
        conn = sqlite3.connect(db_path[0])
        cursor = conn.cursor()
    
        # Fetch the latest voice affirmation data
        cursor.execute("SELECT voice_affirmation_data FROM voice_affirmation ORDER BY id DESC LIMIT 1")
        voice_data = cursor.fetchone()
        
        conn.close()
        
        if not voice_data:
            return "No voice affirmation data found."
        
        return str(voice_data[0])
def cbt_form_save_to_database(input1, input2, input3,input4,mode):
    """Save form data to thought_reframing_user_form table."""
    db_path = get_database_path()
    conn = sqlite3.connect(db_path[0])
    cursor1 = conn.cursor()
    if mode == "thought":
        cursor1.execute("""
            INSERT INTO thought_reframing_user_form (situation, thoughts, feelings, worst_case)
            VALUES (?, ?, ?, ?)
        """, (input1, input2, input3, input4))
    elif mode == "imgery":
        cursor1.execute("""
            INSERT INTO imgery_cbt_user_form (situation, mental_img, exploration, emotional)
            VALUES (?, ?, ?, ?)
        """, (input1, input2, input3, input4))
    conn.commit()
    conn.close()

    # self.show_dialog("Success", "Your responses have been successfully saved!")



def show_cbt_form_data(mode):
    """Fetch the latest entry from the thought_reframing_user_form table."""
    db_path = get_database_path()
    conn = sqlite3.connect(db_path[0])
    cursor = conn.cursor()
    if mode == "thought":
        print("using thought data")
        cursor.execute("""
            SELECT situation, thoughts, feelings, worst_case
            FROM thought_reframing_user_form
            ORDER BY ROWID DESC
            LIMIT 1
        """)

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "situation": row[0],
                "thoughts": row[1],
                "feelings": row[2],
                "worst_case": row[3]
            }
        else:
            return None
    elif mode == "imgery":
        cursor.execute("""
            SELECT situation, mental_img, exploration, emotional
            FROM imgery_cbt_user_form
            ORDER BY ROWID DESC
            LIMIT 1
        """)

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "situation": row[0],
                "mental_img": row[1],
                "exploration": row[2],
                "emotional": row[3]
            }
        else:
            return None


