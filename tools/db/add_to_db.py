import psycopg
import dotenv
import os
from typing import Annotated
from langchain_core.tools import tool, InjectedToolArg
dotenv.load_dotenv()

@tool
def add_to_db(user_id: Annotated[str, InjectedToolArg] | None = 'user-id-123', gender: str | None = None, school: str | None = None):
    '''Adds a new user to the database or updates an existing user'''
    try:
        with psycopg.connect(f"host={os.getenv('DB_HOST')} port={os.getenv('DB_PORT')} dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USER')} password={os.getenv('DB_PASSWORD')}") as conn:
            with conn.cursor() as cur:
                # Build the SET clause dynamically based on non-None values
                set_clauses = []
                if gender is not None:
                    set_clauses.append("gender = EXCLUDED.gender")
                if school is not None:
                    set_clauses.append("school = EXCLUDED.school")
                
                # If no fields to update, just do an insert
                if not set_clauses:
                    cur.execute("""
                        INSERT INTO preference (user_id, gender, school)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id) DO NOTHING
                    """, (user_id, gender, school))
                else:
                    cur.execute(f"""
                        INSERT INTO preference (user_id, gender, school)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id) 
                        DO UPDATE SET {', '.join(set_clauses)}
                    """, (user_id, gender, school))
                
                conn.commit()
                return "User added to database"
                
    except psycopg.OperationalError as e:
        return f"Database connection error: {str(e)}"
    except psycopg.Error as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
            


