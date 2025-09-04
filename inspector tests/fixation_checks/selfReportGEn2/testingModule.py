from testItReports import testReport
import time
import os

# Настройка отчета
testReport.configure(
    configuration_id=os.getenv('CONFIG_ID'),
    auto_test_external_id=os.getenv('EXTERNALID'),
    report_filename="test_results.json",
    debug=True
)

# Глобальные параметры и свойства
testReport.parameter("environment", "production")
testReport.add_property("version", "1.0.0")


# Фикстура setup/teardown
def setup_teardown():
    # Setup
    setup = testReport.setupResults.add("Инициализация тестового окружения", "Подготовка данных для тестов")
    testReport.setupResults.parameter("db_connection", "postgresql://user:pass@localhost:5432/test")
    testReport.setupResults.parameter("api_url", "https://api.example.com/v1")

    # Имитация долгой настройки
    time.sleep(0)

    yield  # Здесь выполняются тесты

    # Teardown
    teardown = testReport.teardownResults.add("Очистка тестовых данных", "Удаление временных файлов и записей")
    testReport.teardownResults.parameter("cleanup_method", "full")
    time.sleep(0)


# Тест 1 - Успешный с вложенными шагами
@testReport.stepResults.title("Успешный с вложенными шагами")
def test_user_api():
    testReport.stepResults.description("Тест проверяет основные методы API для работы с пользователями")
    testReport.stepResults.parameter("api_version", "v1")

    @testReport.stepResults.step("Создание пользователя")
    def create_user():
        testReport.stepResults.description("Проверка метода создания пользователя")
        testReport.stepResults.parameter("method", "POST /users")
        # Имитация API-запроса
        time.sleep(0.2)
        assert True, "Пользователь не был создан"

    @testReport.stepResults.step("Получение пользователя")
    def get_user():
        testReport.stepResults.description("Проверка метода получения данных пользователя")
        testReport.stepResults.parameter("method", "GET /users/{id}")

        @testReport.stepResults.step("Проверка полей ответа")
        def check_fields():
            testReport.stepResults.description("Проверка наличия обязательных полей")
            testReport.stepResults.parameter("required_fields", "id,name,email")
            assert True, "Не все обязательные поля присутствуют"

        # Имитация API-запроса
        time.sleep(0.15)
        assert True, "Не удалось получить данные пользователя"
        check_fields()

    create_user()
    get_user()


# Тест 1.2 - skip с вложенными skip шагами
@testReport.stepResults.title("skip с вложенными skip шагами")
def test_user_api2():
    testReport.stepResults.description("Тест проверяет основные методы API для работы с пользователями")
    testReport.stepResults.parameter("api_version", "v1")

    @testReport.stepResults.step("Создание пользователя")
    def create_user():
        testReport.stepResults.description("Проверка метода создания пользователя")
        testReport.stepResults.parameter("method", "POST /users")
        # Имитация API-запроса
        time.sleep(0.2)
        testReport.stepResults.skip("Тест временно отключен - платежный шлюз в разработке")

    @testReport.stepResults.step("Получение пользователя")
    def get_user():
        testReport.stepResults.description("Проверка метода получения данных пользователя")
        testReport.stepResults.parameter("method", "GET /users/{id}")

        @testReport.stepResults.step("Проверка полей ответа")
        def check_fields():
            testReport.stepResults.description("Проверка наличия обязательных полей")
            testReport.stepResults.parameter("required_fields", "id,name,email")

            testReport.stepResults.skip("Тест временно отключен - платежный шлюз в разработке")

        # Имитация API-запроса
        time.sleep(0.15)
        assert True, "Не удалось получить данные пользователя"
        check_fields()

    create_user()
    get_user()


# Тест 1.3 - skip+успешный во вложенных шагах
@testReport.stepResults.title("skip+успешный во вложенных шагах")
def test_user_api3():
    testReport.stepResults.description("Тест проверяет основные методы API для работы с пользователями")
    testReport.stepResults.parameter("api_version", "v1")

    @testReport.stepResults.step("Создание пользователя")
    def create_user():
        testReport.stepResults.description("Проверка метода создания пользователя")
        testReport.stepResults.parameter("method", "POST /users")
        testReport.stepResults.skip("Тест временно отключен - платежный шлюз в разработке")

    @testReport.stepResults.step("Получение пользователя")
    def get_user():
        testReport.stepResults.description("Проверка метода получения данных пользователя")
        testReport.stepResults.parameter("method", "GET /users/{id}")
        assert True, "Не удалось получить данные пользователя"

    create_user()
    get_user()

# Тест 1.4 - Успешный+skip во вложенных шагах
@testReport.stepResults.title("Успешный+skip во вложенных шагах")
def test_user_api4():
    testReport.stepResults.description("Тест проверяет основные методы API для работы с пользователями")
    testReport.stepResults.parameter("api_version", "v1")

    @testReport.stepResults.step("Создание пользователя")
    def create_user():
        testReport.stepResults.description("Проверка метода создания пользователя")
        testReport.stepResults.parameter("method", "POST /users")
        assert True, "Не удалось получить данные пользователя"

    @testReport.stepResults.step("Получение пользователя")
    def get_user():
        testReport.stepResults.description("Проверка метода получения данных пользователя")
        testReport.stepResults.parameter("method", "GET /users/{id}")

        testReport.stepResults.skip("Тест временно отключен - платежный шлюз в разработке")

    create_user()
    get_user()

# Тест 1.5 - Ошибка+skip во вложенных шагах
@testReport.stepResults.title("Ошибка+skip во вложенных шагах")
def test_user_api5():
    testReport.stepResults.description("Тест проверяет основные методы API для работы с пользователями")
    testReport.stepResults.parameter("api_version", "v1")

    @testReport.stepResults.step("Создание пользователя")
    def create_user():
        testReport.stepResults.description("Проверка метода создания пользователя")
        testReport.stepResults.parameter("method", "POST /users")
        assert False, "Не удалось получить данные пользователя"

    @testReport.stepResults.step("Получение пользователя")
    def get_user():
        testReport.stepResults.description("Проверка метода получения данных пользователя")
        testReport.stepResults.parameter("method", "GET /users/{id}")

        testReport.stepResults.skip("Тест временно отключен - платежный шлюз в разработке")

    create_user()
    get_user()

# Тест 1.6 - skip+Ошибка во вложенных шагах
@testReport.stepResults.title("skip+Ошибка во вложенных шагах")
def test_user_api6():
    testReport.stepResults.description("Тест проверяет основные методы API для работы с пользователями")
    testReport.stepResults.parameter("api_version", "v1")

    @testReport.stepResults.step("Создание пользователя")
    def create_user():
        testReport.stepResults.description("Проверка метода создания пользователя")
        testReport.stepResults.parameter("method", "POST /users")
        testReport.stepResults.skip("Тест временно отключен - платежный шлюз в разработке")

    @testReport.stepResults.step("Получение пользователя")
    def get_user():
        testReport.stepResults.description("Проверка метода получения данных пользователя")
        testReport.stepResults.parameter("method", "GET /users/{id}")
        assert False, "Не удалось получить данные пользователя"


    create_user()
    get_user()

# Тест 1.7 - Короткий Ошибочный
@testReport.stepResults.title("Короткий Ошибочный")
def test_user_api7():
    testReport.stepResults.description("Тест проверяет основные методы API для работы с пользователями")
    testReport.stepResults.parameter("api_version", "v1")
    assert False, "Не удалось получить данные пользователя"

# Тест 1.8 - Короткий Положительный
@testReport.stepResults.title("Короткий Положительный")
def test_user_api8():
    testReport.stepResults.description("Тест проверяет основные методы API для работы с пользователями")
    testReport.stepResults.parameter("api_version", "v1")
    assert True, "Не удалось получить данные пользователя"

# Тест 2 - Короткий skip
@testReport.stepResults.title("Короткий skip")
def test_payment_api():
    testReport.stepResults.description("Тест проверяет методы обработки платежей")
    testReport.stepResults.skip("Тест временно отключен - платежный шлюз в разработке")


# Тест 3 - Неудачный с вложенными шагами(false+true)
@testReport.stepResults.title("Неудачный с вложенными шагами(false+true)")
def test_shopping_cart():
    testReport.stepResults.description("Тест проверяет функционал корзины покупок")

    @testReport.stepResults.step("Добавление товара в корзину")
    def add_to_cart():
        testReport.stepResults.description("Проверка добавления товара")
        # Имитация API-запроса
        time.sleep(0.1)
        assert False, "Не удалось добавить товар в корзину"

    @testReport.stepResults.step("Оформление заказа")
    def checkout():
        testReport.stepResults.description("Проверка оформления заказа")
        testReport.stepResults.parameter("checkout_method", "POST /checkout")

        @testReport.stepResults.step("Проверка валидации данных")
        def validation():
            testReport.stepResults.description("Проверка валидации данных заказа")
            assert True, "Ошибка валидации данных"

        # Этот шаг не выполнится из-за ошибки в add_to_cart
        validation()
        assert True, "Ошибка при оформлении заказа"

    add_to_cart()
    checkout()

# Тест 3.1 - Неудачный с вложенными шагами(true+false) + true на родителе
@testReport.stepResults.title("Неудачный с вложенными шагами(true+false)")
def test_shopping_cart2():
    testReport.stepResults.description("Тест проверяет функционал корзины покупок")

    @testReport.stepResults.step("Добавление товара в корзину")
    def add_to_cart():
        testReport.stepResults.description("Проверка добавления товара")
        # Имитация API-запроса
        time.sleep(0.1)
        assert True, "Не удалось добавить товар в корзину"

    @testReport.stepResults.step("Оформление заказа")
    def checkout():
        testReport.stepResults.description("Проверка оформления заказа")
        testReport.stepResults.parameter("checkout_method", "POST /checkout")

        @testReport.stepResults.step("Проверка валидации данных")
        def validation():
            testReport.stepResults.description("Проверка валидации данных заказа")
            assert False, "Ошибка валидации данных"

        # Этот шаг не выполнится из-за ошибки в add_to_cart
        validation()
        assert True, "Ошибка при оформлении заказа"

    add_to_cart()
    checkout()


# Тест 4 - Успешный с глубокой вложенностью
@testReport.stepResults.title("Успешный с глубокой вложенностью")
def test_complex_system():
    testReport.stepResults.description("Тест проверяет взаимодействие нескольких компонентов системы")

    @testReport.stepResults.step("Модуль A")
    def module_a():
        @testReport.stepResults.step("Подмодуль A1")
        def submodule_a1():
            assert True, "Ошибка в подмодуле A1"

        @testReport.stepResults.step("Подмодуль A2")
        def submodule_a2():
            assert True, "Ошибка в подмодуле A2"

        submodule_a1()
        submodule_a2()

    @testReport.stepResults.step("Модуль B")
    def module_b():
        @testReport.stepResults.step("Подмодуль B1")
        def submodule_b1():
            @testReport.stepResults.step("Компонент B1.1")
            def component_b11():
                assert True, "Ошибка в компоненте B1.1"

            component_b11()

        submodule_b1()

    module_a()
    module_b()

# Тест 4.1 - Ошибка на глубоком уровне
@testReport.stepResults.title("Успешный с глубокой вложенностью")
def test_complex_system2():
    testReport.stepResults.description("Тест проверяет взаимодействие нескольких компонентов системы")

    @testReport.stepResults.step("Модуль A")
    def module_a():
        @testReport.stepResults.step("Подмодуль A1")
        def submodule_a1():
            assert True, "Ошибка в подмодуле A1"

        @testReport.stepResults.step("Подмодуль A2")
        def submodule_a2():
            assert True, "Ошибка в подмодуле A2"

        submodule_a1()
        submodule_a2()

    @testReport.stepResults.step("Модуль B")
    def module_b():
        @testReport.stepResults.step("Подмодуль B1")
        def submodule_b1():
            @testReport.stepResults.step("Компонент B1.1")
            def component_b11():
                assert False, "Ошибка в компоненте B1.1"

            component_b11()

        submodule_b1()

    module_a()
    module_b()

# Тест 4.2 - Ошибка на глубоком уровне
@testReport.stepResults.title("Успешный с глубокой вложенностью")
def test_complex_system3():
    testReport.stepResults.description("Тест проверяет взаимодействие нескольких компонентов системы")

    @testReport.stepResults.step("Модуль A")
    def module_a():
        @testReport.stepResults.step("Подмодуль A1")
        def submodule_a1():
            assert True, "Ошибка в подмодуле A1"

        @testReport.stepResults.step("Подмодуль A2")
        def submodule_a2():
            assert True, "Ошибка в подмодуле A2"

        submodule_a1()
        submodule_a2()

    @testReport.stepResults.step("Модуль B")
    def module_b():
        @testReport.stepResults.step("Подмодуль B1")
        def submodule_b1():
            @testReport.stepResults.step("Компонент B1.1")
            def component_b11():
                testReport.stepResults.skip("Тест временно отключен - платежный шлюз в разработке")

            component_b11()

        submodule_b1()

    module_a()
    module_b()


if __name__ == "__main__":
    # Запуск всех тестов
    testReport.run_tests(
        test_functions=[test_user_api,
                        test_user_api2,
                        test_user_api3,
                        test_user_api4,
                        test_user_api5,
                        test_user_api6,
                        test_user_api7,
                        test_user_api8,
                        test_payment_api,
                        test_shopping_cart,
                        test_shopping_cart2,
                        test_complex_system,
                        test_complex_system2,
                        test_complex_system3],
        setup_teardown_func=setup_teardown
    )