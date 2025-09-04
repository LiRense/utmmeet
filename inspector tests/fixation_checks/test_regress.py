from testitReports import testReport
import time
from regress import *
import os

# Настройка отчета
testReport.configure(
    configuration_id=os.getenv('CONFIG_ID'),
    auto_test_external_id=os.getenv('EXTERNALID'),
    report_filename="test_results.json",
    debug=True
)

# Глобальные параметры и свойства
testReport.parameter("environment", "inspector")

# Фикстура setup/teardown
def setup_teardown():
    # Setup

    yield  # Здесь выполняются тесты

    # Teardown
    # teardown = testReport.teardownResults.add("Очистка тестовых данных", "Удаление временных файлов и записей")
    # testReport.teardownResults.parameter("cleanup_method", "full")

@testReport.stepResults.title("Тесты repproduceproduct_v4")
def repproduceproduct_v4():
    doc_type = 'repproducedproduct_v4'

    @testReport.stepResults.title(f"Проверка тестового окружения для {doc_type}")
    def enviroment_check():
        try:
            db_selecter = DB_placer('fixation', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_selecter.sql_req = f"select distinct check_code from checks.documents_checks dc where check_action != 'error' and document_name_format = '{doc_type}'"
            result = db_selecter.inserter()
            if result:
                testReport.stepResults.description(f"Не все check_action в error: {result}")
                assert False, f"Не все check_action в error: {result}"
            else:
                testReport.stepResults.description("Все check_action проверок в error")
                assert True, f"Все check_action проверок в error"
        except Exception as e:
            logger.error(f'Ошибка при проверке check_action: {e}')
            assert False, f"Ошибка при проверке check_action: {e}"

    @testReport.stepResults.title("doubles")
    def rpp_4_doubles():
        corr_xml = None
        forming = None
        params = None
        sender = None

        @testReport.stepResults.step("Генерация xml")
        def rpp_4_gen_xml():
            nonlocal corr_xml, forming
            try:
                forming = Forming_xml(doc_type=doc_type)

                forming.isMark = True
                forming.isUnPacked = False

                corr_xml = forming.generate_RPP_4()
                logger.debug('Успех генерации xml')
                assert True, "Успех генерации xml"
            except Exception as e:
                logger.error(f'Ошибка при генерации xml: {e}')
                assert False, e

        @testReport.stepResults.step("Вставки в БД")
        def rpp_4_insert_db():

            @testReport.stepResults.step("doc в filedata.inboxdata")
            def doc_insert():
                nonlocal params
                testReport.stepResults.description("Кладем сформированный документ в filedata.inboxdata")
                try:
                    db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                    hex_xml = db_ins.text_to_hex(corr_xml)
                    query, params = db_ins.prepare_sql(hex_xml)
                    db_ins.sql_req = (query, params)  # Кортеж
                    db_ins.inserter()
                    logger.debug('Успех вставки в БД')
                    assert True, "Успех вставки в БД"
                except Exception as e:
                    logger.error(f'Ошибка при вставке в БД: {e}')
                    assert False, e

            @testReport.stepResults.step("Данные по productcode в references.product")
            def product_insert():
                testReport.stepResults.description("Кладем productcode в references.product")
                try:
                    db_ins = DB_placer('nsi', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')

                    db_ins.sql_req = 'INSERT INTO "references"' + f".product (alc_code, product_type_id, full_name, short_name, original_lang_name, producer_fsrar_id, importer_fsrar_id, country_id, capacity, alc_perc_min, alc_perc_max, is_unpacked, brand, row_validity_begin, row_validity_end, shelf_life_day) VALUES('{forming.product_code}', {forming.product_vcode}, '{forming.pr_name}', '{forming.pr_name}', '{forming.pr_name}', '{forming.fsrar}', '{forming.fsrar}', '643', {forming.capacity}, {forming.alc_percent}, {forming.alc_percent}, {forming.isUnPacked}, NULL, '2024-01-01', '2025-01-01', 0) ON CONFLICT (alc_code) DO NOTHING;"

                    db_ins.inserter()

                    logger.debug('Успех вставки в БД')
                    assert True, "Успех вставки в БД"
                except Exception as e:
                    logger.error(f'Ошибка при вставке в БД: {e}')
                    assert False, e

            @testReport.stepResults.step("Обновление признака фасованности по productcode в references.product")
            def product_update():
                testReport.stepResults.description("Обновляем признак фасованности по productcode в references.product")
                try:
                    db_ins = DB_placer('nsi', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')

                    db_ins.sql_req = "update " + f'"references".product set	is_unpacked = {forming.isUnPacked} where alc_code = ' + f"'{forming.product_code}'"

                    db_ins.inserter()

                    logger.debug('Успех обновления статуса фасованности в БД')
                    assert True, "Успех обновления статуса фасованности в БД"
                except Exception as e:
                    logger.error(f'Ошибка при вставке в БД: {e}')
                    assert False, e

            @testReport.stepResults.step("Данные по доку в registry.documents")
            def registry_insert():
                nonlocal params
                testReport.stepResults.description("Вставляем данные, что документ уже обрабатывался")
                try:
                    db_ins = DB_placer('documents', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')

                    db_ins.sql_req = f"INSERT INTO registry.documents (fsrarid, alccode, formb, docid, amount, vol, dt, ins, client_number, dtype, parent, forma, price, ismarked) VALUES({forming.fsrar}, {forming.product_code}, 3, 406256714, 2, 1.5000, '{forming.get_day()}', '2025-08-22 12:15:05.926', '720', '{forming.doc_type}'::registry" + '."doctype", 3, 3, 0.00, true)'
                    db_ins.inserter()

                    logger.debug('Успех вставки в БД')
                    assert True, "Успех вставки в БД"
                except Exception as e:
                    logger.error(f'Ошибка при вставке в БД: {e}')
                    assert False, e

            doc_insert()
            product_insert()
            product_update()
            registry_insert()

        @testReport.stepResults.step("Отправка json")
        def rpp_4_json_send():
            nonlocal sender
            testReport.stepResults.description("Отправляем json на обработку в inspector в confirmed")
            try:
                sender = Kafka_sender(forming.doc_type, params[1])
                sender.send()
                logger.debug('Успех отправки json')
                assert True, "Успех отправки json"
            except Exception as e:
                logger.error(f'Ошибка при отправке json: {e}')
                assert False, e

        @testReport.stepResults.step("Поиск результата")
        def rpp_4_result_checker():
            testReport.stepResults.description("Ищем ошибочный тикет")
            try:
                result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))
                if result:
                    logger.debug(f'Сообщение найдено в svs-inspector: {result}')
                    assert False, f"Сообщение найдено в svs-inspector, проверка пройдена: {result}"
                else:
                    db_selecter = Outbox_checker('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                    result = db_selecter.selecter(sender.uuid)
                    comment = db_selecter.get_comment(result)
                    if not comment:
                        logger.error('Сообщение не найдено, вероятны ошибки в логах')
                        assert False, "Сообщение не найдено, вероятны ошибки в логах"
                    elif 'принят системой на обработку' in comment:
                        logger.error('Сообщение не найдено, вероятны ошибки в логах')
                        assert False, "Сообщение не найдено, вероятны ошибки в логах"
                    else:
                        logger.error(f'Получили {comment}')
                        assert True, f"Успешно упали на проверке, получили {comment}"
            except Exception as e:
                logger.error(f'Ошибка при поиске сообщения: {e}')
                assert False, f"Ошибка при поиске сообщения: {e}"

        rpp_4_gen_xml()
        rpp_4_insert_db()
        rpp_4_json_send()
        rpp_4_result_checker()

    enviroment_check()
    rpp_4_doubles()

if __name__ == "__main__":
    # Запуск всех тестов
    testReport.run_tests(
        test_functions=[repproduceproduct_v4],
        setup_teardown_func=setup_teardown
    )