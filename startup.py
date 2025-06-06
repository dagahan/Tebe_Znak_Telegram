import sys, inspect, logging, colorama
sys.path.insert(0, './src')
from services.scheduler import SchedulerService
from loguru import logger



class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and depth < 10:
            if frame.f_code.co_filename == logging.__file__:
                depth += 1
            frame = frame.f_back

        logger.opt(depth=depth, exception=record.exc_info, record=True).log(
            level, record.getMessage()
        )



class LogSetup:
    @staticmethod
    def configure():
        logger.remove()
        logger.add(
            "debug/debug.json",
            format="{time} {level} {message}",
            serialize=True,
            rotation="04:00",
            retention="14 days",
            compression="zip",
            level="DEBUG",
            catch=True,
        )

        logger.add(
            sys.stdout,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - {message}",
            level="DEBUG",
            catch=True,
        )



if __name__ == "__main__":
    try:
        logsetup = LogSetup()
        logsetup.configure()
        service = SchedulerService()
        service.run_service()
    except KeyboardInterrupt:
        logger.info(f"{colorama.Fore.CYAN}Service stopped by user")
    except Exception as error:
        logger.critical(f"{colorama.Fore.RED}Service crashed: {error}")
        sys.exit(1)
