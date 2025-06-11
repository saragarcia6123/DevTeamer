# DevTeamer - Find devs to collab with

[![wakatime](https://wakatime.com/badge/user/961b9b73-7fbd-42ec-8eac-034f364eaeaf/project/c7cdfabd-0d57-4067-a8b9-9393319a59b3.svg)](https://wakatime.com/badge/user/961b9b73-7fbd-42ec-8eac-034f364eaeaf/project/c7cdfabd-0d57-4067-a8b9-9393319a59b3)

This project uses [FastAPI](https://fastapi.tiangolo.com/) for the backend and [React](https://react.dev/) for the frontend

## Running Locally

### Pre-requisites

- [Docker](https://www.docker.com/)

### Setup

```sh
cp ./frontend/.env.example ./frontend/.env
cp ./backend/.env.example ./backend/.env
cp ./db/.env.example ./db/.env
```

*As of right now, the example `.env` configuration should work as-is*

### Command

```sh
docker compose up
```

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

- #### /auth/verify-login — Confirm login via 2FA
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