import threading
import time
from datetime import datetime
from croniter import croniter
from loguru import logger


class Scheduler:
    def __init__(self, cron_schedule, job_function, job_params=None, run_on_startup=True):
        self.cron_schedule = cron_schedule
        self.job_function = job_function
        self.job_params = job_params or {}
        self.run_on_startup = run_on_startup
        self.thread = None
        self.running = False
        self.startup_executed = False

        # Разбор крона
        try:
            base_time = datetime.now()
            croniter(cron_schedule, base_time)
            logger.info(f"Scheduler initialized with cron schedule: '{cron_schedule}'")
        except Exception as e:
            logger.error(f"Invalid cron expression '{cron_schedule}': {e}")
            raise

    def _calculate_next_run(self, base_time=None):
        if base_time is None:
            base_time = datetime.now()
        cron = croniter(self.cron_schedule, base_time)
        return cron.get_next(datetime)

    def _run_job(self, job_type="scheduled"):
        try:
            logger.info(f"Starting {job_type} job...")
            start_time = time.time()

            if self.job_params:
                result = self.job_function(**self.job_params)
            else:
                result = self.job_function()

            execution_time = time.time() - start_time
            logger.success(f"{job_type.capitalize()} job completed successfully in {execution_time:.2f}s")
            return True

        except Exception as e:
            logger.error(f"{job_type.capitalize()} job failed: {e}")
            return False

    def _should_run_startup_job(self):
        if not self.run_on_startup or self.startup_executed:
            return False
        return True

    def _scheduler_loop(self):
        logger.info("Scheduler loop started")

        while self.running:
            try:
                current_time = datetime.now()

                if self._should_run_startup_job():
                    logger.info("Executing initial job run...")
                    self._run_job("initial")
                    self.startup_executed = True

                next_run = self._calculate_next_run(current_time)
                wait_seconds = (next_run - current_time).total_seconds()

                if wait_seconds > 0:
                    logger.info(f"Next run at {next_run.strftime('%Y-%m-%d %H:%M:%S')} (in {wait_seconds:.0f} seconds)")

                    # Делим ожидание на небольшие интервалы для возможности остановки
                    sleep_intervals = max(1, min(10, int(wait_seconds)))
                    for i in range(sleep_intervals):
                        if not self.running:
                            logger.info("Scheduler stopped during sleep")
                            return
                        time.sleep(wait_seconds / sleep_intervals)

                if self.running:
                    self._run_job("scheduled")
                    self.startup_executed = True

            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)  # Пауза при ошибке

    def start(self):
        if self.running:
            logger.warning("Scheduler is already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.thread.name = "SchedulerThread"
        self.thread.start()
        logger.info("Scheduler started")

    def stop(self):
        if not self.running:
            logger.warning("Scheduler is not running")
            return

        logger.info("Stopping scheduler...")
        self.running = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=10)
            if self.thread.is_alive():
                logger.warning("Scheduler thread did not stop gracefully")
            else:
                logger.info("Scheduler stopped gracefully")
        else:
            logger.info("Scheduler stopped")

    def trigger_manual_run(self):
        """Запуск задания вручную"""
        if not self.job_function:
            logger.error("No job function defined")
            return False

        logger.info("Manual job execution triggered")
        return self._run_job("manual")

    def get_status(self):
        """Получить статус планировщика"""
        status = {
            "running": self.running,
            "cron_schedule": self.cron_schedule,
            "run_on_startup": self.run_on_startup,
            "startup_executed": self.startup_executed,
            "thread_alive": self.thread.is_alive() if self.thread else False
        }

        if self.running:
            try:
                next_run = self._calculate_next_run()
                status["next_run"] = next_run.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                logger.warning(f"Could not calculate next run time: {e}")

        logger.debug(f"Scheduler status: {status}")
        return status