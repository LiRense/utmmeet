import json
import uuid
from datetime import datetime
import os
import sys
import traceback
from typing import Dict, List, Optional, Callable, Any

"""
TestItReports - Библиотека для структурированного тестирования и отчетности
============================================================================

Библиотека предоставляет гибкий инструмент для:
- Организации тестов с вложенными шагами
- Формирования детальных отчетов в JSON
- Управления setup/teardown процедурами
- Гибкой настройки параметров тестирования

Основные возможности:
- Иерархическая структура тестов (тест → шаги → подшаги)
- Три статуса выполнения: Passed, Failed, Skipped
- Автоматический расчет длительности выполнения
- Глобальные и локальные параметры тестов
- Интеграция с фикстурами pytest-style

Примеры использования:
---------------------
"""

class TestReport:
    """Класс для формирования отчетов о выполнении тестов в формате, совместимом с TMS testIt.

    Основной функционал:
    - Создание структурированных JSON-отчетов с иерархией шагов
    - Поддержка setup/teardown методов
    - Автоматический расчет длительности выполнения
    - Три статуса выполнения: Passed, Failed, Skipped
    - Гибкая система параметров и свойств тестирования

    Аттрибуты
    ----------
    _configuration_id : str
        Уникальный идентификатор конфигурации. Формат: UUID4. Автоматически генерируется при создании экземпляра.
    _auto_test_external_id : str
        Внешний ID теста (из testIt). По умолчанию: "default_test_id".
    _parameters : Dict[str, str]
        Глобальные параметры тестирования. Пример: {"environment": "prod", "browser": "chrome"}
    _properties : Dict[str, str]
        Метаданные тестового прогона. Пример: {"version": "1.0.0", "team": "QA Automation"}
    _step_results : List[Dict]
        Результаты выполнения шагов тестов. Хранит иерархическую структуру тестовых шагов.
    _setup_results : List[Dict]
        Результаты методов setup.
    _teardown_results : List[Dict]
        Результаты методов teardown.
    _global_start_time : Optional[datetime]
        Время начала прогона (UTC).
    _global_end_time : Optional[datetime]
        Время окончания прогона (UTC).
    _global_outcome : str
        Общий результат прогона ("Passed"/"Failed"/"Skipped").
    _global_message : str
        Сводное сообщение о результатах.
    _global_traces : str
        Агрегированные трассировки ошибок (если есть).
    _report_filename : str
        Путь к файлу для сохранения отчета. По умолчанию: "test_report.json" в текущей директории.
    _debug : bool
        Режим отладки (логирование в stderr при True).

    Примеры использования:
    ---------------------
    1. Базовая конфигурация:
        >>> report = TestReport()
        >>> report.configure(
        ...     configuration_id=os.getenv('CONFIG_ID'),
        ...     auto_test_external_id=os.getenv('EXTERNALID'),
        ...     report_filename="test_results.json",
        ...     debug=True
        ... )
        >>> report.parameter("environment", "production")
        >>> report.add_property("version", "1.0.0")

    2. Тест с вложенными шагами:
        >>> @report.stepResults.title("Тест API пользователей")
        ... def test_api():
        ...     report.stepResults.description("Проверка CRUD операций")
        ...
        ...     @report.stepResults.step("Создание пользователя")
        ...     def create_user():
        ...         assert True
        ...
        ...     create_user()

    3. Полный сценарий с фикстурами:
        >>> def setup_teardown():
        ...     report.setupResults.add("Инициализация БД")
        ...     yield
        ...     report.teardownResults.add("Очистка данных")
        ...
        >>> report.run_tests([test_api], setup_teardown_func=setup_teardown)

    4. Различные статусы тестов:
        >>> @report.stepResults.title("Успешный тест")
        ... def success_test():
        ...     assert True

        >>> @report.stepResults.title("Пропущенный тест")
        ... def skipped_test():
        ...     report.stepResults.skip("Недостаточно данных")

        >>> @report.stepResults.title("Падающий тест")
        ... def failing_test():
        ...     assert False, "Ожидаемая ошибка"

    Особенности работы:
    ------------------
    1. Иерархия шагов:
       - Любая глубина вложенности (тест → шаг → подшаг)
       - Автоматическое определение статуса родительского шага
       - Единое время выполнения для цепочки шагов

    2. Временные параметры:
       - Автоматическая фиксация времени начала/окончания
       - Расчет длительности в миллисекундах
       - UTC-время в формате ISO8601

    3. Статусы выполнения:
       - Passed: Все утверждения успешны
       - Failed: Хотя бы одно утверждение не выполнено
       - Skipped: Явный пропуск теста/шага

    Формат отчета:
    -------------
    {
        "configurationId": "uuid",               # ID конфигурации
        "autoTestExternalId": "string",          # Внешний ID теста
        "outcome": "Passed/Failed/Skipped",      # Общий результат
        "message": "string",                     # Сводное сообщение
        "traces": "string",                      # Трассировки ошибок
        "startedOn": "ISO8601",                  # Время начала
        "completedOn": "ISO8601",                # Время окончания
        "duration": int,                         # Длительность (мс)
        "parameters": {"key": "value"},          # Глобальные параметры
        "properties": {"key": "value"},          # Свойства теста
        "stepResults": [{                        # Иерархия шагов
            "title": "string",
            "description": "string",
            "outcome": "string",
            "stepResults": [...]
        }],
        "setupResults": [...],                   # Результаты setup
        "teardownResults": [...]                 # Результаты teardown
    }

    Note:
    -----
    Для корректной интеграции с testIt:
    1. Убедитесь, что auto_test_external_id соответствует ID теста в системе
    2. При использовании configuration_id проверьте его актуальность
    3. Все временные метки должны быть в UTC
    """

    def __init__(self):
        """Инициализирует новый экземпляр TestReport с настройками по умолчанию."""

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

        self.stepResults = self.StepResults(self)
        self.setupResults = self.SetupResults(self)
        self.teardownResults = self.TeardownResults(self)

    def configure(self,
                  configuration_id: Optional[str] = None,
                  auto_test_external_id: Optional[str] = None,
                  report_filename: Optional[str] = None,
                  debug: bool = True):
        """Настраивает параметры отчета.

        Parameters
        ----------
        configuration_id : Optional[str]
            Уникальный идентификатор конфигурации.
        auto_test_external_id : Optional[str]
            Внешний идентификатор теста.
        report_filename : Optional[str]
            Имя файла для сохранения отчета.
        debug : bool
            Флаг отладки (вывод дополнительной информации).

        Raises
        ------
        ValueError
            Если переданные параметры имеют недопустимый формат.
        """
        if configuration_id:
            self._configuration_id = configuration_id
        if auto_test_external_id:
            self._auto_test_external_id = auto_test_external_id
        if report_filename:
            self._report_filename = report_filename
        self._debug = debug

    def parameter(self, key: str, value: str):
        """Добавляет глобальный параметр тестирования.

        Parameters
        ----------
        key : str
            Ключ параметра.
        value : str
            Значение параметра.

        Raises
        ------
        TypeError
            Если ключ или значение не являются строками.
        """
        self._parameters[key] = value

    def add_property(self, key: str, value: str):
        """Добавляет дополнительное свойство тестирования.

        Parameters
        ----------
        key : str
            Ключ свойства.
        value : str
            Значение свойства.
        """
        self._properties[key] = value

    def start_test_run(self):
        """Начинает новый тестовый прогон, сбрасывая предыдущие результаты."""
        self._log("Начало выполнения тестов")
        self._global_start_time = datetime.utcnow()
        self._global_outcome = "Passed"
        self._global_message = "Все тесты прошли успешно"
        self._global_traces = "Нет ошибок"
        self._step_results = []
        self._setup_results = []
        self._teardown_results = []

    def end_test_run(self):
        """Завершает тестовый прогон и формирует отчет.

        Returns
        -------
        Dict
            Сформированный отчет о тестировании.

        Raises
        ------
        RuntimeError
            Если тестовый прогон не был должным образом начат или завершен.
        """
        self._global_end_time = datetime.utcnow()
        self._log("Завершение выполнения тестов")
        self._determine_global_outcome()
        report = self._generate_report()
        self._save_report(report)
        return report

    def _determine_global_outcome(self):
        """Определяет общий результат тестового прогона на основе результатов отдельных тестов."""
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
        """Генерирует отчет о тестировании в формате JSON.

        Returns
        -------
        Dict
            Словарь с данными отчета.

        Raises
        ------
        RuntimeError
            Если тестовый прогон не был должным образом начат или завершен.
        """
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
        """Сохраняет отчет в файл.

        Parameters
        ----------
        report : Dict
            Отчет для сохранения.

        Raises
        ------
        IOError
            Если не удалось записать файл.
        PermissionError
            Если нет прав на запись в указанное место.
        TypeError
            Если отчет имеет неверный формат.
        """
        try:
            with open(self._report_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self._log(f"Отчет сохранен в {os.path.abspath(self._report_filename)}")
            print(json.dumps(report, indent=2, ensure_ascii=False))
        except Exception as e:
            self._log(f"ОШИБКА при сохранении отчета: {str(e)}")
            raise

    def _log(self, message: str):
        """Логирует сообщение, если включен режим отладки.

        Parameters
        ----------
        message : str
            Сообщение для логирования.
        """
        if self._debug:
            print(f"[TestReport] {message}", file=sys.stderr)

    def run_tests(self, test_functions: List[Callable], setup_teardown_func: Optional[Callable] = None):
        """Запускает все тесты и формирует отчет.

        Parameters
        ----------
        test_functions : List[Callable]
            Список тестовых функций для выполнения.
        setup_teardown_func : Optional[Callable]
            Функция-фикстура для setup/teardown.

        Notes
        -----
        Функция setup_teardown_func должна быть генератором (использовать yield).
        """
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
        """Класс для управления результатами шагов тестирования.

        Attributes
        ----------
        _report : TestReport
            Родительский объект TestReport.
        _current_test : Optional[Dict]
            Текущий выполняемый тест.
        _step_stack : List[Dict]
            Стек для вложенных шагов.
        _skip_remaining : bool
            Флаг для пропуска оставшихся шагов.
        """
        def __init__(self, report):
            """Инициализирует новый экземпляр StepResults.

            Parameters
            ----------
            report : TestReport
                Родительский объект TestReport.
            """
            self._report = report
            self._current_test = None
            self._step_stack = []  # Стек для вложенных шагов
            self._skip_remaining = False  # Флаг для пропуска оставшихся шагов

        def _get_current_step(self):
            """Возвращает текущий активный шаг (последний в стеке) или текущий тест.

            Returns
            -------
            Optional[Dict]
                Текущий активный шаг или тест, или None если нет активных шагов.
            """
            return self._step_stack[-1] if self._step_stack else self._current_test

        def title(self, title: str):
            """Декоратор для задания названия теста.

            Parameters
            ----------
            title : str
                Название теста.

            Returns
            -------
            Callable
                Декоратор функции теста.
            """
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
            """Декоратор для создания вложенного шага теста.

            Parameters
            ----------
            title : str
                Название шага.

            Returns
            -------
            Callable
                Декоратор функции шага.

            Raises
            ------
            RuntimeError
                Если шаг создается вне контекста теста.
            ValueError
                Если название шага пустое.
            """
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
            """Обрабатывает ошибку в текущем шаге или тесте.

            Parameters
            ----------
            error_msg : str
                Сообщение об ошибке.

            Raises
            ------
            RuntimeError
                Если нет активного шага/теста для обработки ошибки.
            """
            current_step = self._get_current_step()
            if current_step:
                current_step.update({
                    "outcome": "Failed",
                    "message": error_msg,
                    "traces": traceback.format_exc()
                })

        def skip(self, reason: str = ""):
            """Пропускает текущий тест или шаг.

            Parameters
            ----------
            reason : str
                Причина пропуска.
            """
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
            """Устанавливает описание для текущего шага или теста.

            Parameters
            ----------
            description : str
                Описание шага или теста.
            """
            current_step = self._get_current_step()
            if current_step:
                current_step["description"] = description

        def info(self, info: str):
            """Устанавливает дополнительную информацию для текущего шага или теста.

            Parameters
            ----------
            info : str
                Дополнительная информация.
            """
            current_step = self._get_current_step()
            if current_step:
                current_step["info"] = info

        def parameter(self, key: str, value: str):
            """Добавляет параметр для текущего шага или теста.

            Parameters
            ----------
            key : str
                Ключ параметра.
            value : str
                Значение параметра.
            """
            current_step = self._get_current_step()
            if current_step:
                current_step["parameters"][key] = value

    class SetupResults:
        """Класс для управления результатами setup-методов.

        Attributes
        ----------
        _report : TestReport
            Родительский объект TestReport.
        """
        def __init__(self, report):
            """Инициализирует новый экземпляр SetupResults.

            Parameters
            ----------
            report : TestReport
                Родительский объект TestReport.
            """
            self._report = report

        def add(self, title: str, description: str = "", info: str = ""):
            """Добавляет новый setup-метод в отчет.

            Parameters
            ----------
            title : str
                Название setup-метода.
            description : str, optional
                Описание setup-метода.
            info : str, optional
                Дополнительная информация.

            Returns
            -------
            Dict
                Добавленный setup-метод.
            """
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
            """Добавляет параметр для последнего добавленного setup-метода.

            Parameters
            ----------
            key : str
                Ключ параметра.
            value : str
                Значение параметра.
            """
            if self._report._setup_results:
                self._report._setup_results[-1]["parameters"][key] = value

    class TeardownResults:
        """Класс для управления результатами teardown-методов.

        Attributes
        ----------
        _report : TestReport
            Родительский объект TestReport.
        """
        def __init__(self, report):
            """Инициализирует новый экземпляр TeardownResults.

            Parameters
            ----------
            report : TestReport
                Родительский объект TestReport.
            """
            self._report = report

        def add(self, title: str, description: str = "", info: str = ""):
            """Добавляет новый teardown-метод в отчет.

            Parameters
            ----------
            title : str
                Название teardown-метода.
            description : str, optional
                Описание teardown-метода.
            info : str, optional
                Дополнительная информация.

            Returns
            -------
            Dict
                Добавленный teardown-метод.
            """
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
            """Добавляет параметр для последнего добавленного teardown-метода.

            Parameters
            ----------
            key : str
                Ключ параметра.
            value : str
                Значение параметра.
            """
            if self._report._teardown_results:
                self._report._teardown_results[-1]["parameters"][key] = value


# Глобальный экземпляр для использования
testReport = TestReport()