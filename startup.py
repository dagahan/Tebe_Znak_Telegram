import sys
from loguru import logger

sys.path.insert(0, './src')
from znak_publisher import ZnakPublisherService



if __name__ == "__main__":
    try:
        ZnakPublisherService().Run_Service()
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as error:
        logger.critical(f"Service crashed: {error}")
        sys.exit(1)