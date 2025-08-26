
import sqlite3
import bcrypt
import os

from platformdirs import user_data_dir
from transformers import T5ForConditionalGeneration, T5Tokenizer

##############################################################################################
### Import a pre-trained model from Huggungface to translate natural language to sql query ###
##############################################################################################


model_dir = "./t5_sql_finetuned"
tokenizer = T5Tokenizer.from_pretrained(model_dir)
model = T5ForConditionalGeneration.from_pretrained(model_dir)


def query_from_nl_to_sql(text):
    '''
    exploits the fine tuned model to generate an sql query starting from
    a natural language prompt
    '''
    input_text = f"Translate from English to SQL: {text}"
    inputs = tokenizer(input_text, return_tensors='pt')
    outputs = model.generate(**inputs)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result



###########################################
### database managment system for login ###
###########################################

APP_NAME = "MonkeyDB"
APP_AUTHOR = "Marco"

USER_DB_DIR = user_data_dir(appname=APP_NAME, appauthor=APP_AUTHOR, ensure_exists=True)
USER_DB_PATH = os.path.join(USER_DB_DIR, "Users.db")


def create_users_database():
    database = sqlite3.connect(USER_DB_PATH)
    cursor = database.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            username TEXT PRIMARY KEY,
            password BLOB NOT NULL
        )
        """
        )
    database.commit()    # save eventual updates
    database.close()     # close connection with database


def insert_user(name, surname, username, password):
    '''
    hashes the password and inserts the data in the users.db dataabase
    '''
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    database = sqlite3.connect(USER_DB_PATH)
    cursor = database.cursor()
    
    try:
        cursor.execute(
            "INSERT into users(name, surname, username, password) values(?, ?, ?, ?)", (name, surname, username, hashed_password)
            )
        database.commit()
        database.close()
        return True
        
    except sqlite3.IntegrityError:
        database.close()
        return False



def print_table(database):
    database = sqlite3.connect(database)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    print("Users:")

    for row in rows:
        print(row)

    database.close()


def delete_table(table, db):
    database = sqlite3.connect(db)
    cursor = database.cursor()

    cursor.execute(f"DROP TABLE IF EXISTS {table}")
    database.commit()
    database.close()

def get_user(user):
    database = sqlite3.connect(USER_DB_PATH)
    cursor = database.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username = ?", (user,))
    data = cursor.fetchone()
    database.close()
    
    return data

def execute_query(database_name, query):
    database = sqlite3.connect(database_name)
    cursor = database.cursor()

    try:
        cursor.execute(query)
        if query.strip().lower().startswith("select"):
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return results, columns

        else:
            database.commit()
            return
    
    except Exception as e:
        raise e
    
    finally:
        database.close()
    
    

def create_database(name):
    database = sqlite3.connect(f"{name}.db")
    database.commit()    # save eventual updates
    database.close()     # close connection with database


def delete_database(db_name):
    if os.path.exists(db_name):
        try:
            os.remove(db_name)
            return True
        
        except OSError as e:
            raise OSError(f"The database {db_name} could not be deleted, error: {e}")
        
    else:
        raise FileNotFoundError(f"Database {db_name} not found")


def get_databases_in_folder(folder_path):
    '''
    returns all the .db files in the selected folder
    '''
    db_files = []
    if os.path.isdir(folder_path):
        for f in os.listdir(folder_path):
            if f.endswith(".db"):
                db_files.append(os.path.join(folder_path, f))
    return db_files