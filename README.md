# DevPortal

[![wakatime](https://wakatime.com/badge/user/961b9b73-7fbd-42ec-8eac-034f364eaeaf/project/4aecf67f-d5c4-46f7-9196-7e2542fcfa0f.svg)](https://wakatime.com/badge/user/961b9b73-7fbd-42ec-8eac-034f364eaeaf/project/4aecf67f-d5c4-46f7-9196-7e2542fcfa0f)

## A sophisticated login portal made with [FastAPI](https://fastapi.tiangolo.com/) and [React](https://react.dev/)

## Running Locally

### Pre-requisites

- [Docker](https://www.docker.com/products/docker-desktop/)

### Setup

#### Copy .env files

```sh
cp ./frontend/.env.example ./frontend/.env
cp ./backend/.env.example ./backend/.env
cp ./db/.env.example ./db/.env
```

*As of right now, the example `.env` configuration should work as-is*

#### Install node modules

```sh
cd frontend
npm install
cd ..
```

#### Run Command

```sh
docker compose up --build
```

Wait for the message 'VITE v6.x.x  ready in xxx ms' to appear (this should take around 20-30 seconds)

*Frontend URL - <http://localhost:3000>*

*Backend docs URL — <http://localhost:8000/docs>*


## Direct connection to the databases via CLI

### [PostgreSQL](https://www.postgresql.org/download/)

```sh
psql -h 127.0.0.1 -U postgres -W
\c db
```

### [Redis](https://redis.io/downloads/)

```sh
redis-cli -h 127.0.0.1
```

## Response Model

*✱ = required*

- **Detail ✱** — string
- **Status Code ✱** — int
- **Data** — int
- **Metadata ✱** — dict

## Endpoints

*2FA = 2-Factor Authentication*

*✱ = required*

---

- #### /auth/register — User registration
    ↪ Response (dev) — **Verify link**

    ↪ Response (prod) — **Message**
    
    - **User Data ✱** — [**email**, **password**, **username**, first name, last name]
    - **Redirect URI** — Page to redirect to after verification

---

- #### /auth/verify — Profile verification
    ↪ Response or Redirect — [**message**, **status**]

    - **Token ✱** — Short-lived JWT Token generated during registration
    - **Redirect URI** — Handed over from registration

---

- #### /auth/login — Logging in with email or username
    ↪ Response (dev) — **2FA link**

    ↪ Response (prod) — **Message**

    - **User Data ✱** — [**email**, **password**]
    - **Redirect URI** — Page to redirect to after 2FA login

---

- #### /auth/confirm-login — Confirm login via 2FA
    ↪ Response or Redirect — [**message**, **status**, **HTTP-only JWT Cookie**]

    - **Token ✱** — Short-lived JWT Token generated during login
    - **Redirect URI** — Page to redirect to handed over from login

---

- #### /auth/resend-verification — Confirm login via 2FA
    ↪ Response or Redirect — [**message**]

    - **Redirect URI** — Page to redirect to after verification

---

- #### /users/get-current — Retrieve details of current user
    ↪ **User Data** — [**id**, **email**, **username**, first name, last name, **verified**]

---

- #### /users/{username} — Retrieve details of a user by email or username
    ↪ **User Data** — [**id**, **email**, **username**, first name, last name, **verified**]

---

- #### /users/check-exists — Check if a user exists
    ↪ **Exists** — true/false

---

- #### /users/check-verified — Check if a user is verified
    ↪ **Verified** — true/false

---

### User model

*✱ = non-null*

- **ID ✱** — int, primary key
- **Email ✱** — string
- **Username ✱** — string
- **Hashed Password ✱** — string
- **First Name** — string
- **Last Name** — string
- **Verified ✱** — boolean

---

### Registration

1. Client makes request to /auth/register with User Form Data
2. Server validates user data.
3. Password is hashed using bcrypt
4. User is inserted into SQL database
5. JWT token is generated and sent to email via a link to verify
6. User clicks the link and request is made to /auth/verify
7. JWT is validated and user is marked as verified


### Login

1. Client makes request to /auth/login with email/username and password
2. Server checks existence of user in SQL database
3. Password is validated using bcrypt
4. JWT token is generated and sent to email via a link to confirm login with 2FA
5. User clicks the link and request is made to /auth/confirm-login
6. JWT is validated.
7. A long-lived HTTP-only JWT token is generated
8. The token is injected into the response cookie
9. The client receives the repsonse with the cookie and is now authorised
10. Subsequent requests made to the API must have credentials included and will be auto authenticated

## Extra Features

- Custom HTTP Middleware that intercepts and standardizes all requests
- Cache last response and return on immediately subsequent requests to prevent idempotency
- Robust field validation using Pydantic and other validation libraries

*...plus loads more that you can check out for yourself!*
