import psycopg
import dotenv
import os
from typing import Annotated
from langchain_core.tools import tool, InjectedToolArg
dotenv.load_dotenv()

@tool
def retrieve_from_db(user_id: Annotated[str, InjectedToolArg] | None = 'user-id-123'):
    '''Get the user information by user_id'''
    try:
        with psycopg.connect(f"host={os.getenv('DB_HOST')} port={os.getenv('DB_PORT')} dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USER')} password={os.getenv('DB_PASSWORD')}") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM preference WHERE user_id = %s", (user_id,))
                result = cur.fetchone()
                
                if result is None:
                    return f"No user found with id: {user_id}"
                
                columns = [desc[0] for desc in cur.description]
                user_data = dict(zip(columns, result))
                return user_data
                
    except psycopg.OperationalError as e:
        return f"Database connection error: {str(e)}"
    except psycopg.Error as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
            

