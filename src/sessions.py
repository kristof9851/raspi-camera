sessions = {}
SESSION_COOKIE_NAME = "session_token"

from fastapi import Request, HTTPException, status

def authenticate_user(request: Request):
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    print(f"Session token from cookie: {session_token}")
    print(f"Sessions: {sessions}")
    if not session_token or session_token not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return sessions[session_token]
