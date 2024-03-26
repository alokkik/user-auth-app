import os
import jwt
import psycopg2
from uuid import uuid4
from app.query import FIND_USER_QUERY, CREATE_USER_QUERY
from contextlib import asynccontextmanager
from app.schemas import UserOut, UserAuth
from fastapi.responses import JSONResponse
from psycopg2.extensions import connection as pg_connection
from fastapi import FastAPI, status, HTTPException, Header, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import UserOut, UserAuth, TokenSchema
from app.db import get_connection, create_users_table
from app.utils import (
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_password,
    validate_token
)


blacklist = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    conn =  get_connection()
    create_users_table(conn)
    yield
    # Clean up the ML models and release the resources
    conn.close()

# initialize the FastAPI app
app = FastAPI(lifespan=lifespan)


def check_user(email, conn):
    with conn.cursor() as cursor:
        cursor.execute(FIND_USER_QUERY, (email,))
        user = cursor.fetchone()
    return user

@app.post('/signup', summary="Create new user", response_model=UserOut)
async def create_user(data: UserAuth, conn: pg_connection = Depends(get_connection)):
    
    if check_user(data.email, conn):
        raise HTTPException(status_code=404, detail="User already exists")

    try:
        with conn.cursor() as cursor:
            # Execute the query with parameters
            cursor.execute(CREATE_USER_QUERY, (data.email, get_password_hash(data.password), str(uuid4())))
            conn.commit()  # Commit the changes to the database
    except psycopg2.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    return JSONResponse({'message': 'User created successfully!'})


@app.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), conn: pg_connection = Depends(get_connection)):
    user = check_user(form_data.username, conn)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user = { "email": user[1], "id": user[0], "password": user[2]}

    hashed_pass = user['password']
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    return JSONResponse({
        "access_token": create_access_token(user['email']),
        "refresh_token": create_refresh_token(user['email']),
    })

@app.get("/check/auth", summary="Check access to protected endpoint")
async def protected_endpoint(token: str = Header(...)):
    if not validate_token(token, blacklist):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"message": "Access granted to protected endpoint"}


# Revoke token
@app.post('/revoke')
def revoke(token: str = Header(...)):
    if not validate_token(token, blacklist):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    blacklist.add(token)
    return {"message": "Token successfully revoked!"}


# Endpoint for token refresh
@app.post("/refresh")
async def refresh_token(refresh_token: str = Header(...)):
    try:
        payload = jwt.decode(refresh_token, os.environ['JWT_REFRESH_SECRET_KEY'], algorithms=["HS256"])
        username = payload["sub"]
        access_token = create_access_token(username)
        return {"access_token": access_token}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")