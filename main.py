import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "SHZgptServer.asgi:application",
        host="0.0.0.0",
        port=8000,
        workers=2,
        reload=True,
    )
