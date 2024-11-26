from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ImportRouter, LibraryRouter
from app.config import setup_logging

setup_logging()


app = FastAPI()

# origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ImportRouter)
app.include_router(LibraryRouter)
