from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from src.database.db import engine, Base
from src.routes import auth as auth_routes
from src.routes import contacts as contacts_routes
from src.routes import users as users_routes
from src.services.limiter import limiter

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contacts API")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Rate limiting (slowapi) ---
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Забагато запитів. Спробуйте пізніше."},
    )


app.include_router(auth_routes.router)
app.include_router(contacts_routes.router)
app.include_router(users_routes.router)


@app.get("/")
def read_root():
    return {"message": "Contacts API is running"}
