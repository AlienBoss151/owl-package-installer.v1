# OWL Backend Server

This backend is required for registration, user counting, and remote enable/disable for your OPI tool.

## How to Run

1. Install dependencies:
    ```
    pip install flask
    ```
2. Start the server:
    ```
    python app.py
    ```
3. The server will listen on port 5000.

## Endpoints

- `POST /api/register_user`  
  Register a new user (called by opi CLI).
- `GET /api/app_status`  
  Returns `{ "enabled": true }` or `{ "enabled": false }`.
- `GET /api/user_count`  
  Returns `{ "user_count": N }`.

## Controlling OPI Globally

- Change the `APP_ENABLED` variable in `app.py` to `False` to globally disable all OPI clients.

## View Registered Users

- Data is stored in `users.json`.