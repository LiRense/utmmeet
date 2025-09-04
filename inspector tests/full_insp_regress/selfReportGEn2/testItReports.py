import json
import uuid
from datetime import datetime
import os
import sys
import traceback
from typing import Dict, List, Optional, Callable, Any


class TestReport:
    def __init__(self):
        self._configuration_id = str(uuid.uuid4())
        self._auto_test_external_id = "default_test_id"
        self._parameters: Dict[str, str] = {}
        self._properties: Dict[str, str] = {}
        self._step_results: List[Dict] = []
        self._setup_results: List[Dict] = []
        self._teardown_results: List[Dict] = []
        self._global_start_time: Optional[datetime] = None
        self._global_end_time: Optional[datetime] = None
        self._global_outcome = "Passed"
        self._global_message = "Все тесты прошли успешно"
        self._global_traces = "Нет ошибок"
        self._report_filename = "test_report.json"
        self._debug = True

        # Initialize subclasses
        self.stepResults = self.StepResults(self)
        self.setupResults = self.SetupResults(self)
        self.teardownResults = self.TeardownResults(self)

    def configure(self,
                  configuration_id: Optional[str] = None,
                  auto_test_external_id: Optional[str] = None,
                  report_filename: Optional[str] = None,
                  debug: bool = True):
        if configuration_id:
            self._configuration_id = configuration_id
        if auto_test_external_id:
            self._auto_test_external_id = auto_test_external_id
        if report_filename:
            self._report_filename = report_filename
        self._debug = debug

    def parameter(self, key: str, value: str):
        self._parameters[key] = value

    def add_property(self, key: str, value: str):
        self._properties[key] = value

    def start_test_run(self):
        self._log("Начало выполнения тестов")
        self._global_start_time = datetime.utcnow()
        self._global_outcome = "Passed"
        self._global_message = "Все тесты прошли успешно"
        self._global_traces = "Нет ошибок"
        self._step_results = []
        self._setup_results = []
        self._teardown_results = []

    def end_test_run(self):
        self._global_end_time = datetime.utcnow()
        self._log("Завершение выполнения тестов")
        self._determine_global_outcome()
        report = self._generate_report()
        self._save_report(report)
        return report

    def _determine_global_outcome(self):
        outcomes = [test["outcome"] for test in self._step_results]

        if "Failed" in outcomes:
            self._global_outcome = "Failed"
            failed_tests = [t["title"] for t in self._step_results if t["outcome"] == "Failed"]
            self._global_message = f"Ошибки в тестах: {', '.join(failed_tests)}"

            traces = []
            for t in self._step_results:
                if t["outcome"] == "Failed":
                    traces.append(f"\n                                                  \n")
                    traces.append(f"{t['title']}:\n{t['traces']}")
                    traces.append(f"\n                                                  \n\n")

            self._global_traces = "\n".join(traces)

        elif all(outcome == "Skipped" for outcome in outcomes):
            self._global_outcome = "Skipped"
            self._global_message = "Все тесты пропущены"
            self._global_traces = "Причины пропуска:\n" + "\n".join(
                f"{t['title']}: {t['message']}"
                for t in self._step_results
            )
        elif not outcomes:
            self._global_outcome = "Skipped"
            self._global_message = "Нет выполненных тестов"
            self._global_traces = "Не было запущено ни одного теста"

    def _generate_report(self) -> Dict:
        if not self._global_start_time or not self._global_end_time:
            raise RuntimeError("Test run not properly started/ended")

        duration = int((self._global_end_time - self._global_start_time).total_seconds() * 1000)

        return [{
            "configurationId": self._configuration_id,
            "links": [],
            "failureReasonNames": [],
            "autoTestExternalId": self._auto_test_external_id,
            "outcome": self._global_outcome,
            "message": self._global_message,
            "traces": self._global_traces,
            "startedOn": self._global_start_time.isoformat() + "Z",
            "completedOn": self._global_end_time.isoformat() + "Z",
            "duration": duration,
            "attachments": [],
            "parameters": self._parameters,
            "properties": self._properties,
            "stepResults": self._step_results,
            "setupResults": self._setup_results,
            "teardownResults": self._teardown_results
        }]

    def _save_report(self, report: Dict):
        try:
            with open(self._report_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self._log(f"Отчет сохранен в {os.path.abspath(self._report_filename)}")
            print(json.dumps(report, indent=2, ensure_ascii=False))
        except Exception as e:
            self._log(f"ОШИБКА при сохранении отчета: {str(e)}")
            raise

    def _log(self, message: str):
        if self._debug:
            print(f"[TestReport] {message}", file=sys.stderr)

    def run_tests(self, test_functions: List[Callable], setup_teardown_func: Optional[Callable] = None):
        """Запускает все тесты и формирует отчет"""
        self.start_test_run()

        # Инициализация фикстуры
        if setup_teardown_func:
            fixture = setup_teardown_func()
            next(fixture)  # Выполняем setup

        try:
            # Выполняем все тесты
            for test in test_functions:
                try:
                    test()
                except Exception:
                    continue  # Ошибки уже обработаны декоратором

        finally:
            # Завершение фикстуры
            if setup_teardown_func:
                try:
                    next(fixture)  # Выполняем teardown
                except StopIteration:
                    pass

            # Завершение тестового прогона
            report = self.end_test_run()
            print("\nТестирование завершено. Отчет сформирован.")

    class StepResults:
        def __init__(self, report):
            self._report = report
            self._current_test = None
            self._step_stack = []  # Стек для вложенных шагов
            self._skip_remaining = False  # Флаг для пропуска оставшихся шагов

        def _get_current_step(self):
            """Возвращает текущий активный шаг (последний в стеке) или текущий тест"""
            return self._step_stack[-1] if self._step_stack else self._current_test

        def title(self, title: str):
            def decorator(test_func: Callable) -> Callable:
                def wrapper(*args, **kwargs) -> Any:
                    # Создаем новый тест
                    new_test = {
                        "title": title,
                        "description": "",
                        "info": "",
                        "startedOn": datetime.utcnow().isoformat() + "Z",
                        "outcome": "Passed",
                        "stepResults": [],
                        "attachments": [],
                        "parameters": {},
                        "message": "",
                        "traces": ""
                    }

                    # Сохраняем предыдущий текущий тест
                    prev_test = self._current_test
                    prev_skip = self._skip_remaining
                    self._current_test = new_test
                    self._skip_remaining = False
                    self._step_stack.append(new_test)

                    try:
                        result = test_func(*args, **kwargs)
                    except AssertionError as e:
                        error_msg = str(e) or "Утверждение не выполнено"
                        self._handle_error(error_msg)
                        raise
                    except Exception as e:
                        error_msg = f"Неожиданная ошибка: {str(e)}"
                        self._handle_error(error_msg)
                        raise
                    finally:
                        completed_test = self._step_stack.pop()
                        completed_test["completedOn"] = datetime.utcnow().isoformat() + "Z"
                        duration = (datetime.fromisoformat(completed_test["completedOn"][:-1]) -
                                    datetime.fromisoformat(completed_test["startedOn"][:-1]))
                        completed_test["duration"] = int(duration.total_seconds() * 1000)

                        # Определяем outcome родительского шага на основе подшагов
                        if completed_test["stepResults"]:
                            child_outcomes = [s["outcome"] for s in completed_test["stepResults"]]
                            if "Failed" in child_outcomes:
                                completed_test["outcome"] = "Failed"
                                failed_steps = [s["title"] for s in completed_test["stepResults"] if
                                                s["outcome"] == "Failed"]
                                completed_test["message"] = f"Ошибки в шагах: {', '.join(failed_steps)}"
                            elif all(outcome == "Skipped" for outcome in child_outcomes):
                                completed_test["outcome"] = "Skipped"
                                completed_test["message"] = "Все шаги пропущены"

                        if self._step_stack:
                            self._step_stack[-1]["stepResults"].append(completed_test)
                        else:
                            self._report._step_results.append(completed_test)

                        # Восстанавливаем предыдущий текущий тест и флаг пропуска
                        self._current_test = prev_test
                        self._skip_remaining = prev_skip

                    return result

                return wrapper

            return decorator

        def step(self, title: str):
            """Декоратор для вложенных шагов"""

            def decorator(step_func: Callable) -> Callable:
                def wrapper(*args, **kwargs) -> Any:
                    if not self._current_test:
                        raise RuntimeError("Вложенные шаги можно создавать только внутри теста")

                    # Сохраняем предыдущее состояние флага пропуска
                    prev_skip = self._skip_remaining

                    # Если текущий шаг должен быть пропущен
                    if self._skip_remaining:
                        skipped_step = {
                            "title": title,
                            "description": "",
                            "info": "",
                            "startedOn": datetime.utcnow().isoformat() + "Z",
                            "completedOn": datetime.utcnow().isoformat() + "Z",
                            "outcome": "Skipped",
                            "stepResults": [],
                            "attachments": [],
                            "parameters": {},
                            "message": "Пропущен из-за ошибки в предыдущем шаге",
                            "traces": "",
                            "duration": 0
                        }
                        if self._step_stack:
                            self._step_stack[-1]["stepResults"].append(skipped_step)
                        else:
                            self._current_test["stepResults"].append(skipped_step)
                        return None

                    new_step = {
                        "title": title,
                        "description": "",
                        "info": "",
                        "startedOn": datetime.utcnow().isoformat() + "Z",
                        "outcome": "Passed",
                        "stepResults": [],
                        "attachments": [],
                        "parameters": {},
                        "message": "",
                        "traces": ""
                    }

                    self._step_stack.append(new_step)
                    self._skip_remaining = False  # Сбрасываем флаг для нового шага

                    try:
                        result = step_func(*args, **kwargs)
                    except AssertionError as e:
                        error_msg = str(e) or "Утверждение не выполнено"
                        self._handle_error(error_msg)
                        raise
                    except Exception as e:
                        error_msg = f"Неожиданная ошибка: {str(e)}"
                        self._handle_error(error_msg)
                        raise
                    finally:
                        completed_step = self._step_stack.pop()
                        completed_step["completedOn"] = datetime.utcnow().isoformat() + "Z"
                        duration = (datetime.fromisoformat(completed_step["completedOn"][:-1]) -
                                    datetime.fromisoformat(completed_step["startedOn"][:-1]))
                        completed_step["duration"] = int(duration.total_seconds() * 1000)

                        # Определяем outcome родительского шага на основе подшагов
                        if completed_step["stepResults"]:
                            child_outcomes = [s["outcome"] for s in completed_step["stepResults"]]
                            if "Failed" in child_outcomes:
                                completed_step["outcome"] = "Failed"
                                failed_steps = [s["title"] for s in completed_step["stepResults"] if
                                                s["outcome"] == "Failed"]
                                completed_step["message"] = f"Ошибки в шагах: {', '.join(failed_steps)}"
                            elif all(outcome == "Skipped" for outcome in child_outcomes):
                                completed_step["outcome"] = "Skipped"
                                completed_step["message"] = "Все шаги пропущены"

                        if self._step_stack:
                            self._step_stack[-1]["stepResults"].append(completed_step)
                        else:
                            self._current_test["stepResults"].append(completed_step)

                        # Восстанавливаем предыдущее состояние флага пропуска
                        self._skip_remaining = prev_skip

                    return result

                return wrapper

            return decorator

        def _handle_error(self, error_msg: str):
            current_step = self._get_current_step()
            if current_step:
                current_step.update({
                    "outcome": "Failed",
                    "message": error_msg,
                    "traces": traceback.format_exc()
                })

        def skip(self, reason: str = ""):
            """Пропустить текущий тест или шаг"""
            current_step = self._get_current_step()
            if current_step:
                current_step.update({
                    "outcome": "Skipped",
                    "message": reason or "Шаг пропущен",
                    "completedOn": datetime.utcnow().isoformat() + "Z",
                    "traces": ""
                })
                duration = (datetime.fromisoformat(current_step["completedOn"][:-1]) -
                            datetime.fromisoformat(current_step["startedOn"][:-1]))
                current_step["duration"] = int(duration.total_seconds() * 1000)
                self._skip_remaining = True

        def description(self, description: str):
            current_step = self._get_current_step()
            if current_step:
                current_step["description"] = description

        def info(self, info: str):
            current_step = self._get_current_step()
            if current_step:
                current_step["info"] = info

        def parameter(self, key: str, value: str):
            current_step = self._get_current_step()
            if current_step:
                current_step["parameters"][key] = value

    class SetupResults:
        def __init__(self, report):
            self._report = report

        def add(self, title: str, description: str = "", info: str = ""):
            setup_data = {
                "title": title,
                "description": description,
                "info": info,
                "startedOn": datetime.utcnow().isoformat() + "Z",
                "completedOn": datetime.utcnow().isoformat() + "Z",
                "outcome": "Passed",
                "stepResults": [],
                "attachments": [],
                "parameters": {}
            }
            duration = (datetime.fromisoformat(setup_data["completedOn"][:-1]) -
                        datetime.fromisoformat(setup_data["startedOn"][:-1]))
            setup_data["duration"] = int(duration.total_seconds() * 1000)
            self._report._setup_results.append(setup_data)
            return setup_data

        def parameter(self, key: str, value: str):
            if self._report._setup_results:
                self._report._setup_results[-1]["parameters"][key] = value

    class TeardownResults:
        def __init__(self, report):
            self._report = report

        def add(self, title: str, description: str = "", info: str = ""):
            teardown_data = {
                "title": title,
                "description": description,
                "info": info,
                "startedOn": datetime.utcnow().isoformat() + "Z",
                "completedOn": datetime.utcnow().isoformat() + "Z",
                "outcome": "Passed",
                "stepResults": [],
                "attachments": [],
                "parameters": {}
            }
            duration = (datetime.fromisoformat(teardown_data["completedOn"][:-1]) -
                        datetime.fromisoformat(teardown_data["startedOn"][:-1]))
            teardown_data["duration"] = int(duration.total_seconds() * 1000)
            self._report._teardown_results.append(teardown_data)
            return teardown_data

        def parameter(self, key: str, value: str):
            if self._report._teardown_results:
                self._report._teardown_results[-1]["parameters"][key] = value


# Глобальный экземпляр для использования
testReport = TestReport()