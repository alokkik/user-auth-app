# user-auth-app
This application contains JWT based user authentication, sign-in, sign-up, token revocation and refreshment.


## How to run the application on your local:
#### Note: This application uses PostgreSQL as database.
```
For Mac: brew install postgresql@14
for Ubuntu: sudo apt install postgresql
For Windows: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
```

1. Go to ```user-auth-app```
2. To create a ```.venv```, run ```python3 -m venv .venv```
3. Run ```source .venv/bin/activate``` to activate virtual environment.
4. Run below commands
   ```
    export JWT_SECRET_KEY=36b0261d4d233cd794837747cba2c74b4f09293ceed11cfdf8fb1ea09dffaca9
    export JWT_REFRESH_SECRET_KEY=ea363cb466c23eb5d057b6e1853ff7e9b5c03bcb35805e36af86b22d451bf228
   ```
7. Now, install dependencies ```pip3 install -r requirements.txt```.
8. Finally, run ```uvicorn app.app:app```
9. go to http://localhost:8000/docs

### Curl :-

#### 1) Create A User
```
curl -X 'POST' \
  'http://127.0.0.1:8000/signup' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "user@example.com",
  "password": "string"
}'
```

#### 2) User Login
```
curl -X 'POST' \
  'http://127.0.0.1:8000/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=&username=user%40example.com&password=string'
```

#### 3) Check Token Authentication
returns "Access granted to protected endpoint" on success.
```
curl -X 'GET' \
  'http://127.0.0.1:8000/check/auth' \
  -H 'accept: application/json' \
  -H 'token: paste_your_access_token_here'
```

#### 4) Revoke Token

```
curl -X 'POST' \
  'http://127.0.0.1:8000/revoke' \
  -H 'accept: application/json' \
  -H 'token: paste_your_access_token_here'
```

#### 5) Refresh Token

```
curl -X 'POST' \
  'http://127.0.0.1:8000/refresh' \
  -H 'accept: application/json' \
  -H 'refresh-token: paste_your_refresh_token_here'
```
