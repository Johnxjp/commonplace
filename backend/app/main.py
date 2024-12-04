from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ImportRouter, LibraryRouter
from app.logging import setup_logging

setup_logging()


app = FastAPI(debug=True)

# origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

# TODO: Settings probably need to be more robust
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(ImportRouter)
app.include_router(LibraryRouter)
