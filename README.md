# ShareGram 📸

A minimal Instagram-style media sharing app with a **FastAPI** backend and a **Streamlit** frontend. Users can register, log in, upload photos/videos with a caption, browse a shared feed, and delete their own posts.

## Features

- 🔐 JWT authentication (register, login, password reset, email verification) via `fastapi-users`
- 📤 Image/video upload with captions, stored on **ImageKit**
- 🗂️ SQLite database (via `aiosqlite` + SQLAlchemy async ORM) for users and posts
- 🖼️ Shared feed showing all uploads, newest first
- 🗑️ Post owners (or superusers) can delete posts
- 🌐 Simple Streamlit UI that talks to the FastAPI backend over HTTP

## Tech Stack

| Layer      | Technology |
|------------|------------|
| Backend    | FastAPI, Uvicorn |
| Auth       | fastapi-users, JWT |
| Database   | SQLAlchemy (async), SQLite (aiosqlite) |
| Storage    | ImageKit.io |
| Frontend   | Streamlit |

## Project Structure

```
ShareGram/
├── main.py                 # Entry point — runs the FastAPI app with Uvicorn
├── requirements.txt
├── app/
│   ├── app.py               # FastAPI app, routes (upload, feed, delete, auth)
│   ├── db.py                 # SQLAlchemy models (User, Post) and session setup
│   ├── users.py               # fastapi-users auth backend & user manager
│   ├── schemas.py               # Pydantic schemas
│   ├── images.py                 # ImageKit client setup
│   └── streamlit_app.py           # Streamlit frontend
└── LICENSE
```

## Getting Started

### Prerequisites

- Python 3.10+
- An [ImageKit.io](https://imagekit.io/) account (for media storage)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/iamarshalrejith/ShareGram.git
   cd ShareGram
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables:
   ```env
   SECRET=<a-long-random-string>
   IMAGEKIT_PRIVATE_KEY=<your-imagekit-private-key>
   IMAGEKIT_URL=<your-imagekit-url-endpoint>
   ```

### Running the app

**Start the backend (FastAPI):**
```bash
python main.py
```
The API will be available at `http://localhost:8000`. Interactive API docs are auto-generated at `http://localhost:8000/docs`.

**Start the frontend (Streamlit), in a separate terminal:**
```bash
streamlit run app/streamlit_app.py
```
By default the frontend expects the API at `http://localhost:8000`. To point it elsewhere, set the `API_URL` environment variable or a Streamlit secret named `API_URL`.

## API Overview

| Method | Endpoint             | Description                          | Auth required |
|--------|-----------------------|---------------------------------------|----------------|
| POST   | `/auth/register`      | Register a new user                   | No |
| POST   | `/auth/jwt/login`      | Log in and receive a JWT              | No |
| POST   | `/auth/forgot-password` | Request a password reset             | No |
| POST   | `/auth/verify`         | Verify a user's email                 | No |
| GET    | `/users/me`            | Get current user profile              | Yes |
| POST   | `/upload`              | Upload an image/video with a caption  | Yes |
| GET    | `/feed`                | Get all posts, newest first           | Yes |
| DELETE | `/posts/{post_id}`     | Delete a post (owner or superuser)    | Yes |

## Notes

- The included SQLite setup (`test.db`) is intended for local development. Swap `DATABASE_URL` in `app/db.py` for a production-grade database (e.g. PostgreSQL) before deploying.
- CORS is currently open to all origins (`allow_origins=["*"]`) for ease of local development — restrict this to your actual frontend origin in production.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
