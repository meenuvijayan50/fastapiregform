from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from psycopg2 import connect, sql
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database connection parameters
db_params = {
    "dbname": "base1",
    "user": "dem1",
    "password": "meenu",
    "host": "localhost",
    "port": "5432",
}

# OAuth2PasswordBearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database connection function
def get_db():
    conn = connect(**db_params)
    try:
        yield conn
    finally:
        conn.close()


# ...

# POST method for user registration
@app.post("/register/")
def register_user(
    full_name: str, email: str, password: str, phone: str, profile_picture: str,
    db: connect = Depends(get_db)
):
    cursor = db.cursor()

    # Check if email or phone already exist
    cursor.execute(sql.SQL('SELECT * FROM users WHERE email = %s;'), (email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")

    cursor.execute(sql.SQL('SELECT * FROM users WHERE phone = %s;'), (phone,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Phone already registered")

    # Insert user into the "user1" table
    cursor.execute(
        sql.SQL('INSERT INTO users (full_name, email, password, phone) VALUES (%s, %s, %s, %s) RETURNING id;'),
        (full_name, email, password, phone),
    )
    user_id = cursor.fetchone()[0]

    # Insert profile into the "profile" table
    cursor.execute(
        sql.SQL('INSERT INTO profiles (profile_picture, user_id) VALUES (%s, %s);'),
        (profile_picture, user_id),
    )

    db.commit()
    cursor.close()

    return {"message": "User registered successfully"}

# GET method to get registered user details
@app.get("/user/{user_id}")
def get_user(user_id: int, db: connect = Depends(get_db)):
    cursor = db.cursor()

    # Retrieve user details from the "user1" table
    cursor.execute(sql.SQL('SELECT * FROM users WHERE id = %s;'), (user_id,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Retrieve profile details from the "profile" table
    cursor.execute(sql.SQL('SELECT * FROM profiles WHERE user_id = %s;'), (user_id,))
    profile = cursor.fetchone()

    cursor.close()

    return {
        "user_id": user[0],
        "full_name": user[1],
        "email": user[2],
        "phone": user[3],
        "profile_picture": profile[1] if profile else None,
    }
