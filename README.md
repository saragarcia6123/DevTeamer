# DevTeamer - Find devs to collab with

This project uses [FastAPI](https://fastapi.tiangolo.com/) for the backend and [React](https://react.dev/) for the frontend

## Endpoints

*2FA = 2-Factor Authentication*

*✱ = required*

---

- #### /auth/register — User registration
    ↪ Response (dev) — **Verify link** or **HTTPError**

    ↪ Response (prod) — **Message** or **HTTPError**
    
    - **User Data ✱** — [**email**, **password**, **username**, first name, last name]
    - **Redirect URI** — Where to go after verification link

---

- #### /auth/verify — Profile verification
    ↪ Response or Redirect — [**message**, **status**]

    - **Token ✱** — Short-lived JWT Token generated during registration
    - **Redirect URI** — Handed over from registration

---

- #### /auth/login — Logging in with email or username
    ↪ Response (dev) — **2FA link** or **HTTPError**

    ↪ Response (prod) — **Message** or **HTTPError**

    - **User Data ✱** — [**email**, **password**]
    - **Redirect URI** — Where to go after 2FA link

---

- #### /auth/verify-login — Confirming login via 2FA
    ↪ Response or Redirect — [**message**, **status**, **HTTP-only JWT Cookie**]

    - **Token** — Short-lived JWT Token generated during login
    - **Redirect URI** — Handed over from login

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
5. JWT token is generated and sent to email via a link to confirm login with 2FA
6. User clicks the link and request is made to /auth/confirm-login
7. JWT is validated.
8. A long-lived HTTP-only JWT token is generated
9. The token is injected into the response cookie
10. The client receives the repsonse with the cookie and is now authorised