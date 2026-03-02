import json
from testitReports import testReport
import time
from regress import *
import os
import ast
import traceback

# Настройка отчета
testReport.configure(
    configuration_id=os.getenv('CONFIG_ID'),
    auto_test_external_id=os.getenv('EXTERNALID'),
    report_filename="test_results.json",
    debug=True
)

# Глобальные параметры и свойства
testReport.parameter("environment", "api-moderation")
test_env = {'bearer': None}


# Вспомогательная функция для декодирования байтовых ответов
def decode_response_content(content):
    """Декодирует байтовый ответ сервера в читаемый текст"""
    if isinstance(content, bytes):
        try:
            # Пробуем декодировать как UTF-8
            decoded = content.decode('utf-8')
            # Если это JSON, пытаемся красиво отформатировать
            try:
                json_obj = json.loads(decoded)
                return json.dumps(json_obj, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                return decoded
        except UnicodeDecodeError:
            # Если не UTF-8, пробуем другие кодировки
            try:
                return content.decode('cp1251')
            except UnicodeDecodeError:
                return str(content)
    return str(content)


# Фикстура setup/teardown
def setup_teardown():
    global test_env
    # Setup
    logger.debug("=" * 50)
    logger.debug("НАЧАЛО НАСТРОЙКИ ТЕСТОВОГО ОКРУЖЕНИЯ")
    logger.debug("=" * 50)

    setup_step = testReport.setupResults.add(
        "Инициализация тестового окружения",
        "Подготовка тестового окружения для выполнения API тестов"
    )

    testReport.setupResults.parameter("environment", "api-moderation")
    testReport.setupResults.parameter("test_start_time", time.strftime("%Y-%m-%d %H:%M:%S"))

    logger.info("Тестовое окружение успешно инициализировано")

    yield  # Здесь выполняются тесты

    # Teardown
    logger.debug("=" * 50)
    logger.debug("ОЧИСТКА ТЕСТОВОГО ОКРУЖЕНИЯ")
    logger.debug("=" * 50)

    teardown_step = testReport.teardownResults.add(
        "Очистка тестовых данных",
        "Завершение тестов и очистка временных данных"
    )

    test_env['bearer'] = None
    logger.info("Тестовое окружение успешно очищено")


def swagger_full_test():
    logger.info("=" * 50)
    logger.info("ЗАПУСК ПОЛНОГО ТЕСТИРОВАНИЯ SWAGGER API")
    logger.info("=" * 50)

    @testReport.stepResults.title("Получение bearer токена")
    def get_bearer():
        global test_env
        logger.debug("-" * 30)
        logger.debug("ШАГ: Получение bearer токена")
        logger.debug("-" * 30)

        try:
            logger.debug("Инициализация CSV_getter и запрос токена")
            response = CSV_getter().get_bearer()

            if response is None:
                error_msg = "❌ Не удалось получить bearer токен: ответ от сервера отсутствует"
                logger.error(error_msg)
                testReport.stepResults.description(error_msg)
                assert False, error_msg

            elif response[0] != 200:
                error_content = decode_response_content(response[1]) if len(
                    response) > 1 else "Нет дополнительной информации"
                error_msg = (f"❌ Эндпоинт авторизации вернул код {response[0]}, ожидался 200\n"
                             f"Детали ошибки: {error_content}")
                logger.error(error_msg)
                testReport.stepResults.description(error_msg)
                assert False, error_msg

            else:
                token_preview = response[1][:20] + "..." if len(response[1]) > 20 else response[1]
                success_msg = (f"✅ Bearer токен успешно получен\n"
                               f"  Статус код: {response[0]}\n")
                logger.info(success_msg)
                test_env['bearer'] = response[1]
                testReport.stepResults.description(success_msg)
                assert True, "Bearer токен успешно сгенерирован"

        except Exception as e:
            error_msg = f"❌ Критическая ошибка при получении bearer токена: {str(e)}"
            logger.error(error_msg)
            logger.debug(f"Traceback: {traceback.format_exc()}")
            testReport.stepResults.description(error_msg)
            assert False, error_msg

    @testReport.stepResults.title("Выполнение тестовых сценариев")
    def curl_test_module():
        logger.debug("-" * 30)
        logger.debug("ШАГ: Генерация и выполнение тестовых сценариев")
        logger.debug("-" * 30)

        try:
            csv_getter = CSV_getter()
            logger.debug("Чтение тестовых данных из CSV")
            tests_df = csv_getter.get_rows()

            if tests_df.empty:
                warning_msg = "⚠️ CSV файл не содержит тестовых данных"
                logger.warning(warning_msg)
                testReport.stepResults.description(warning_msg)
                return

            grouped = tests_df.groupby('endpoint')

            if len(grouped) == 0:
                warning_msg = "⚠️ Нет данных для группировки по endpoint"
                logger.warning(warning_msg)
                testReport.stepResults.description(warning_msg)
                return

            for endpoint_name, group in grouped:
                logger.debug("-" * 20)
                logger.debug(f"Обработка эндпоинта: {endpoint_name}")
                logger.debug(f"Найдено {len(group)} записей для этого эндпоинта")

                tests_for_endpoint = []

                for id, row in group.iterrows():
                    logger.debug(f"Обработка тестового плана #{id}: {row['method']} {row['endpoint']}")
                    logger.debug(f"Content-Type: {row['content-type']}")
                    logger.debug(f"Ожидаемый код: {row['expCode']}, код ошибки авторизации: {row['auth_code_err']}")

                    tests_list = list(csv_getter.make_tests(id, row))
                    logger.debug(f"Сгенерировано {len(tests_list)} тестовых кейсов для плана #{id}")

                    for test in tests_list:
                        test['method'] = row['method']
                        test['content-type'] = row['content-type']
                        test['expCode'] = row['expCode']
                        test['auth_code_err'] = row['auth_code_err']

                    tests_for_endpoint.extend(tests_list)

                logger.debug(f"Всего сгенерировано {len(tests_for_endpoint)} тестов для эндпоинта {endpoint_name}")

                @testReport.stepResults.title(f"Тесты для эндпоинта {endpoint_name}")
                def endpoint_tests():
                    for i, test in enumerate(tests_for_endpoint):
                        logger.debug(
                            f"Выполнение тестового кейса #{i + 1} из {len(tests_for_endpoint)} для {endpoint_name}")

                        test_row = {
                            'method': test.get('method'),
                            'endpoint': endpoint_name,
                            'content-type': test.get('content-type'),
                            'expCode': test.get('expCode'),
                            'auth_code_err': test.get('auth_code_err')
                        }

                        # Выполняем тест
                        run_test_case(test_row, test)

                endpoint_tests()

        except Exception as e:
            error_msg = f"❌ Ошибка при генерации тестов: {str(e)}"
            logger.error(error_msg)
            testReport.stepResults.description(error_msg)
            assert False, error_msg

    def run_test_case(row, test):
        logger.debug("." * 15)
        logger.debug(f"Формирование описания тестового кейса")

        logger.debug(f"Параметры теста:")
        logger.debug(f"  - Описание: {test.get('description', 'Нет описания')}")
        logger.debug(f"  - Минимальные параметры: {test.get('min_params', 'Нет')}")
        logger.debug(f"  - Максимальные параметры: {test.get('parameters', 'Нет')}")
        logger.debug(f"  - Минимальное body: {test.get('min_req_body', 'Нет')}")
        logger.debug(f"  - Максимальное body: {test.get('request_body', 'Нет')}")
        logger.debug(f"  - Требуется авторизация: {test.get('auth', False)}")

        title_desc = 'Кейс:'
        test['final_params'] = ''
        test['final_body'] = ''
        test['final_files'] = ''

        found_test_type = False

        if pd.notna(test.get('min_params')) and test['min_params']:
            title_desc += ' минимально заполненные параметры'
            test['final_params'] = test['min_params']
            logger.debug("Тип: тест с минимальными параметрами")
            found_test_type = True

        elif pd.notna(test.get('parameters')) and test['parameters']:
            title_desc += ' максимально заполненные параметры'
            test['final_params'] = test['parameters']
            logger.debug("Тип: тест с максимальными параметрами")
            found_test_type = True

        if pd.notna(test.get('min_req_body')) and test['min_req_body']:
            title_desc += ' минимально заполненное body'
            test['final_body'] = test['min_req_body']
            logger.debug("Тип: тест с минимальным body")
            found_test_type = True

        elif pd.notna(test.get('request_body')) and test['request_body']:
            title_desc += ' максимально заполненное body'
            test['final_body'] = test['request_body']
            logger.debug("Тип: тест с максимальным body")
            found_test_type = True

        if pd.notna(test.get('files_min')) and test['files_min']:
            title_desc += ' с минимальным набором файлов'
            test['final_files'] = test['files_min']
            logger.debug(f"Тип: тест с минимальными файлами - {test['files_min']}")
            found_test_type = True
        elif pd.notna(test.get('files_max')) and test['files_max']:
            title_desc += ' с максимальным набором файлов'
            test['final_files'] = test['files_max']
            logger.debug(f"Тип: тест с максимальными файлами - {test['files_max']}")
            found_test_type = True

        # Проверяем description - он может перезаписать title_desc, но не отменяет найденный тип теста
        if pd.notna(test.get('description')) and test['description']:
            title_desc = f"Кейс: {test['description']}"
            logger.debug(f"Тип: пользовательское описание - {test['description']}")
            found_test_type = True

        # Если ни один из блоков не сработал
        if not found_test_type:
            title_desc = 'Кейс без параметров и тела'
            logger.debug("Тип: тест без параметров и тела")

        @testReport.stepResults.title(f"{title_desc}")
        def test_case():
            logger.debug(f"Запуск тестового кейса: {title_desc}")

            if test.get('auth', False):
                logger.debug("Сценарий с авторизацией (будет проверен оба варианта: с токеном и без)")
                run_auth_scenarios(test)
            else:
                logger.debug("Сценарий без авторизации (будет проверен только вариант без токена)")
                run_auth_scenarios(test, [('without_bearer', 'without bearer')])

        test_case()

    def run_auth_scenarios(test_row, scenarios=None):
        try:
            if scenarios is None:
                scenarios = [
                    ('with_bearer', 'with bearer'),
                    ('without_bearer', 'without bearer')
                ]
                logger.debug(f"Будут выполнены оба сценария авторизации")
            else:
                logger.debug(f"Будет выполнен сценарий: {scenarios[0][1]}")

            logger.debug(f"Параметры запроса:")
            logger.debug(f"  - Endpoint: {test_row['endpoint']}")
            logger.debug(f"  - Method: {test_row['method']}")
            logger.debug(f"  - Content-Type: {test_row['content-type']}")

            for scenario_name, title in scenarios:
                logger.debug(f">>> Выполнение сценария: {title}")

                @testReport.stepResults.title(title)
                def scenario():
                    try:
                        sw_path = CSV_getter().config_pars()
                        logger.debug(f"Загружена конфигурация: base_url={sw_path['swagger_url']}")

                        if scenario_name == 'with_bearer':
                            bearer = test_env.get('bearer')
                            if not bearer:
                                error_msg = "❌ Bearer токен отсутствует в тестовом окружении"
                                logger.error(error_msg)
                                testReport.stepResults.description(error_msg)
                                assert False, error_msg
                            logger.debug("Используется авторизация с токеном")
                        else:
                            bearer = None
                            logger.debug("Запрос выполняется без авторизации")

                            # logger.debug(f"test_params: {test_row['parameters']}")
                            # logger.debug(f"final_params: {test_row['final_params']}")

                        try:
                            params = json.loads(test_row['final_params']) if test_row.get('final_params') else None
                            data = json.loads(test_row['final_body']) if test_row.get('final_body') else None
                            final_files = json.loads(test_row['final_files']) if test_row.get('final_files') else None
                            last_files = None

                            if params:
                                logger.debug(f"Параметры запроса: {json.dumps(params, indent=2, ensure_ascii=False)}")
                            if data:
                                logger.debug(f"Тело запроса: {json.dumps(data, indent=2, ensure_ascii=False)}")
                            if final_files:
                                last_files = {}
                                for name, file_type in final_files.items():

                                    if file_type == 'image/jpeg':
                                        pass
                                    elif file_type == 'image/png':
                                        file = 'files/common.png'

                                    with open(file, 'rb') as file_obj:
                                        file_content = file_obj.read()
                                    last_files[name] = (file, file_content, file_type)



                        except json.JSONDecodeError as e:
                            error_msg = f"❌ Ошибка парсинга JSON: {str(e)}"
                            logger.error(error_msg)
                            logger.debug(
                                f"Проблемные данные: params='{test_row.get('final_params')}', body='{test_row.get('final_body')}'")
                            testReport.stepResults.description(error_msg)
                            assert False, error_msg

                        # Выполнение
                        logger.debug("Отправка HTTP запроса...")
                        full_url = f"{sw_path['swagger_url']}{test_row['endpoint']}"
                        logger.debug(f"URL: {full_url}")
                        # logger.debug(f"test_data: {params}; {data}")

                        result, response = CSV_getter().send_curl(
                            base_url=sw_path['swagger_url'],
                            endpoint=test_row['endpoint'],
                            params=params,
                            headers={"Content-Type": test_row['content-type']},
                            data=data,
                            bearer=bearer,
                            method=test_row['method'],
                            files=last_files
                        )

                        # Декодирование ответа для читаемого вида
                        decoded_content = decode_response_content(response.content)

                        logger.debug(f"Запрос выполнен. Статус код: {response.status_code}")
                        logger.debug(f"Ответ сервера (первые 300 символов): {decoded_content[:300]}")

                        expected_code = test_row['auth_code_err'] if bearer is None else test_row['expCode']

                        logger.debug(f"Проверка результата:")
                        logger.debug(f"  - Фактический код: {response.status_code}")
                        logger.debug(f"  - Ожидаемый код: {expected_code}")

                        if response.status_code == expected_code:
                            success_desc = (f"✅ Тест успешно пройден\n"
                                            f"  Статус код: {response.status_code} (совпадает с ожидаемым {expected_code})\n"
                                            f"  Сценарий: {title}\n"
                                            f"  Ответ сервера:\n{decoded_content}")

                            logger.info(f"✓ Тест пройден: статус {response.status_code}")
                            testReport.stepResults.description(success_desc)
                            assert True, f"Статус код {response.status_code} соответствует ожидаемому {expected_code}"

                        else:
                            error_detail = (f"❌ Тест не пройден\n"
                                            f"  Статус код: {response.status_code} (ожидался {expected_code})\n"
                                            f"  Сценарий: {title}\n"
                                            f"  Ответ сервера:\n{decoded_content}")

                            logger.error(f"✗ Тест не пройден: получен {response.status_code}, ожидался {expected_code}")
                            logger.debug(f"Детали ошибки: {decoded_content}")

                            testReport.stepResults.description(error_detail)

                            testReport.stepResults.error_skip(
                                f"Код ответа не совпадает с ожидаемым: "
                                f"получен {response.status_code}, ожидался {expected_code}"
                            )

                    except Exception as e:
                        error_msg = (f"❌ Критическая ошибка при выполнении сценария '{title}': {str(e)}\n"
                                     f"Endpoint: {test_row['endpoint']}\n"
                                     f"Метод: {test_row['method']}")

                        logger.error(error_msg)
                        logger.debug(f"Traceback: {traceback.format_exc()}")

                        testReport.stepResults.description(error_msg)
                        assert False, error_msg

                scenario()

        except Exception as e:
            error_msg = f"❌ Ошибка в обработке сценариев авторизации: {str(e)}"
            logger.error(error_msg)
            logger.debug(f"Traceback: {traceback.format_exc()}")
            testReport.stepResults.description(error_msg)
            assert False, error_msg

    # Запуск основных шагов
    get_bearer()
    curl_test_module()


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("ЗАПУСК ТЕСТОВОГО НАБОРА")
    logger.info("=" * 50)

    # Запуск всех тестов
    testReport.run_tests(
        test_functions=[swagger_full_test],
        setup_teardown_func=setup_teardown
    )

    logger.info("=" * 50)
    logger.info("ЗАВЕРШЕНИЕ ТЕСТОВОГО НАБОРА")
    logger.info("=" * 50)