from __init__ import VERSION, API_NAME

if __name__ == "__main__":
    import uvicorn
    from loguru import logger

    logger.info(f"Version: {VERSION}")
    logger.info(f"Starting {API_NAME}...")
    uvicorn.run(
        "api.v1.main:app",
        port=3560,
        workers=9,
        access_log="uvicorn_access.log",
    )
