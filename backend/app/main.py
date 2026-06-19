from fastapi import FastAPI

app = FastAPI(
    title="E-Commerce API",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "E-Commerce API is running"}