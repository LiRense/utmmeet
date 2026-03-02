import os
import time
import sys
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

from jobs.mark_gen import GeneratorBcode

# Настройка loguru
logger.remove()  # Удаляем стандартный обработчик

logger.add(
    sink="logs/mark_gen_{time:YYYY-MM-DD}.log",
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}",
    rotation="1 day",
    retention="30 days"
)

class CronService:
    def __init__(self):
        self.running = True

    def run_job(self):
        try:
            logger.info("Starting mark generation job")

            generator = GeneratorBcode()
            generator.insert_mark_list_records(10)

            logger.info("Mark generation job completed successfully")
        except Exception as e:
            logger.error(f"Job failed: {e}")

    def run(self):
        logger.info("Starting Cron Service")

        if os.getenv('RUN_ON_STARTUP', 'true').lower() == 'true':
            logger.info("Running job on startup")
            self.run_job()

        while self.running:
            try:
                now = datetime.now()

                if now.hour == 0 and now.minute == 0:
                    logger.info("Midnight - running job")
                    self.run_job()
                    time.sleep(120)

                time.sleep(60)

            except Exception as e:
                logger.error(f"Error: {e}")
                time.sleep(60)


if __name__ == "__main__":
    CronService().run()