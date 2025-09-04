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
    # setup = testReport.setupResults.add("Инициализация тестового окружения", "Подготовка данных для тестов")
    # testReport.setupResults.parameter("db_connection", "postgresql://user:pass@localhost:5432/test")
    # testReport.setupResults.parameter("api_url", "https://api.example.com/v1")

    yield  # Здесь выполняются тесты

    # Teardown
    # teardown = testReport.teardownResults.add("Очистка тестовых данных", "Удаление временных файлов и записей")
    # testReport.teardownResults.parameter("cleanup_method", "full")

@testReport.stepResults.title("Отправка repproducedproduct_v4 маркированная")
def RPP_4_mark_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def rpp_4_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='repproducedproduct_v4')

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

        doc_insert()
        product_insert()
        product_update()

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
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))
            if result:
                logger.debug(f'Сообщение найдено: {result}')
                assert True, f"Сообщение найдено: {result}"
            else:
                db_selecter = Outbox_checker('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                result = db_selecter.selecter(sender.uuid)
                comment = db_selecter.get_comment(result)

                if not comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                elif comment is None:
                    logger.error('Сообщение не найдено (None)')
                    assert False, "Сообщение не найдено"
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    rpp_4_gen_xml()
    rpp_4_insert_db()
    rpp_4_json_send()
    rpp_4_result_checker()

@testReport.stepResults.title("Отправка repproducedproduct_v4 немаркированная фасованная")
def RPP_4_isPacked_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def rpp_4_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='repproducedproduct_v4')

            forming.isMark = False
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

        doc_insert()
        product_insert()
        product_update()

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
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))
            if result:
                logger.debug(f'Сообщение найдено: {result}')
                assert True, f"Сообщение найдено: {result}"
            else:
                db_selecter = Outbox_checker('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                result = db_selecter.selecter(sender.uuid)
                comment = db_selecter.get_comment(result)

                if not comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                elif comment is None:
                    logger.error('Сообщение не найдено (None)')
                    assert False, "Сообщение не найдено"
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    rpp_4_gen_xml()
    rpp_4_insert_db()
    rpp_4_json_send()
    rpp_4_result_checker()

@testReport.stepResults.title("Отправка repproducedproduct_v4 немаркированная нефасованная")
def RPP_4_isUnPacked_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def rpp_4_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='repproducedproduct_v4')

            forming.isMark = False
            forming.isUnPacked = True

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

        doc_insert()
        product_insert()
        product_update()

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
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))
            if result:
                logger.debug(f'Сообщение найдено: {result}')
                assert True, f"Сообщение найдено: {result}"
            else:
                db_selecter = Outbox_checker('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                result = db_selecter.selecter(sender.uuid)
                comment = db_selecter.get_comment(result)

                if not comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                elif comment is None:
                    logger.error('Сообщение не найдено (None)')
                    assert False, "Сообщение не найдено"
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    rpp_4_gen_xml()
    rpp_4_insert_db()
    rpp_4_json_send()
    rpp_4_result_checker()


@testReport.stepResults.title("Отправка repimportedproduct_v4 маркированная")
def RIP_4_mark_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def rip_4_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='repimportedproduct_v4')

            forming.isMark = True
            forming.isUnPacked = False

            corr_xml = forming.generate_RIP_4()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставки в БД")
    def rip_4_insert_db():

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

        doc_insert()
        product_insert()
        product_update()

    @testReport.stepResults.step("Отправка json")
    def rip_4_json_send():
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
    def rip_4_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))
            if result:
                logger.debug(f'Сообщение найдено: {result}')
                assert True, f"Сообщение найдено: {result}"
            else:
                db_selecter = Outbox_checker('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                result = db_selecter.selecter(sender.uuid)
                comment = db_selecter.get_comment(result)

                if not comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                elif comment is None:
                    logger.error('Сообщение не найдено (None)')
                    assert False, "Сообщение не найдено"
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    rip_4_gen_xml()
    rip_4_insert_db()
    rip_4_json_send()
    rip_4_result_checker()

@testReport.stepResults.title("Отправка repimportedproduct_v4 немаркированная фасованная")
def RIP_4_isPacked_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def rip_4_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='repimportedproduct_v4')

            forming.isMark = False
            forming.isUnPacked = False

            corr_xml = forming.generate_RIP_4()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставки в БД")
    def rip_4_insert_db():

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

        doc_insert()
        product_insert()
        product_update()

    @testReport.stepResults.step("Отправка json")
    def rip_4_json_send():
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
    def rip_4_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))
            if result:
                logger.debug(f'Сообщение найдено: {result}')
                assert True, f"Сообщение найдено: {result}"
            else:
                db_selecter = Outbox_checker('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                result = db_selecter.selecter(sender.uuid)
                comment = db_selecter.get_comment(result)

                if not comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                elif comment is None:
                    logger.error('Сообщение не найдено (None)')
                    assert False, "Сообщение не найдено"
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    rip_4_gen_xml()
    rip_4_insert_db()
    rip_4_json_send()
    rip_4_result_checker()

@testReport.stepResults.title("Отправка repimportedproduct_v4 немаркированная нефасованная")
def RIP_4_isUnPacked_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def rip_4_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='repimportedproduct_v4')

            forming.isMark = False
            forming.isUnPacked = True

            corr_xml = forming.generate_RIP_4()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставки в БД")
    def rip_4_insert_db():

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

        doc_insert()
        product_insert()
        product_update()

    @testReport.stepResults.step("Отправка json")
    def rip_4_json_send():
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
    def rip_4_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))
            if result:
                logger.debug(f'Сообщение найдено: {result}')
                assert True, f"Сообщение найдено: {result}"
            else:
                db_selecter = Outbox_checker('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                result = db_selecter.selecter(sender.uuid)
                comment = db_selecter.get_comment(result)

                if not comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                elif comment is None:
                    logger.error('Сообщение не найдено (None)')
                    assert False, "Сообщение не найдено"
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    rip_4_gen_xml()
    rip_4_insert_db()
    rip_4_json_send()
    rip_4_result_checker()


@testReport.stepResults.title("Отправка actchargeon_v2 маркированная")
def ACO_2_mark_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def aco_2_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='actchargeon_v2')

            forming.isMark = True
            forming.isUnPacked = False

            corr_xml = forming.generate_ACO_2()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставки в БД")
    def aco_2_insert_db():

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

        doc_insert()
        product_insert()
        product_update()

    @testReport.stepResults.step("Отправка json")
    def aco_2_json_send():
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
    def aco_2_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))
            if result:
                logger.debug(f'Сообщение найдено: {result}')
                assert True, f"Сообщение найдено: {result}"
            else:
                db_selecter = Outbox_checker('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                result = db_selecter.selecter(sender.uuid)
                comment = db_selecter.get_comment(result)

                if not comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                elif comment is None:
                    logger.error('Сообщение не найдено (None)')
                    assert False, "Сообщение не найдено"
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    aco_2_gen_xml()
    aco_2_insert_db()
    aco_2_json_send()
    aco_2_result_checker()

@testReport.stepResults.title("Отправка actchargeon_v2 немаркированная фасованная")
def ACO_2_isPacked_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def aco_2_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='actchargeon_v2')

            forming.isMark = False
            forming.isUnPacked = False

            corr_xml = forming.generate_ACO_2()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставки в БД")
    def aco_2_insert_db():

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

        doc_insert()
        product_insert()
        product_update()

    @testReport.stepResults.step("Отправка json")
    def aco_2_json_send():
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
    def aco_2_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))
            if result:
                logger.debug(f'Сообщение найдено: {result}')
                assert True, f"Сообщение найдено: {result}"
            else:
                db_selecter = Outbox_checker('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                result = db_selecter.selecter(sender.uuid)
                comment = db_selecter.get_comment(result)

                if not comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                elif comment is None:
                    logger.error('Сообщение не найдено (None)')
                    assert False, "Сообщение не найдено"
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    aco_2_gen_xml()
    aco_2_insert_db()
    aco_2_json_send()
    aco_2_result_checker()

@testReport.stepResults.title("Отправка actchargeon_v2 немаркированная нефасованная")
def ACO_2_isUnPacked_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def aco_2_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='actchargeon_v2')

            forming.isMark = False
            forming.isUnPacked = True

            corr_xml = forming.generate_ACO_2()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставки в БД")
    def aco_2_insert_db():

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

        doc_insert()
        product_insert()
        product_update()

    @testReport.stepResults.step("Отправка json")
    def aco_2_json_send():
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
    def aco_2_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))
            if result:
                logger.debug(f'Сообщение найдено: {result}')
                assert True, f"Сообщение найдено: {result}"
            else:
                db_selecter = Outbox_checker('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                result = db_selecter.selecter(sender.uuid)
                comment = db_selecter.get_comment(result)

                if not comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                elif comment is None:
                    logger.error('Сообщение не найдено (None)')
                    assert False, "Сообщение не найдено"
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    aco_2_gen_xml()
    aco_2_insert_db()
    aco_2_json_send()
    aco_2_result_checker()


@testReport.stepResults.title("Отправка waybill_v4 маркированная")
def TTN_4_mark_test():
    corr_xml = None
    forming = None
    params = None
    sender = None
    form_A = None

    @testReport.stepResults.step("Получение информации из БД")
    def ttn_4_forma():
        nonlocal form_A
        testReport.stepResults.description("Ведем поиск последней FormA")
        logger.debug("Ведем поиск последней FormA")
        try:
            db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT reg_id FROM registry.form_a AS x order by reg_id DESC limit 1"

            form = db_ins.inserter()
            logger.debug(form)

            if form:
                form_A = form[0][0]

                logger.debug('Обновили форму 1 документа')
                assert True, "Обновили форму 1 документа"
            else:
                logger.debug('ФормА не найдена, используем пример формы А')
                assert True, "Используем хардкод формы А"

        except Exception as e:
            logger.error(f'Ошибка обновлении формы А: {e}')
            assert False, e

    @testReport.stepResults.step("Генерация xml")
    def ttn_4_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='waybill_v4')

            forming.isMark = True
            forming.isUnPacked = False

            forming.formA = form_A

            corr_xml = forming.generate_WayBill_4()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставки в БД")
    def ttn_4_insert_db():

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

        doc_insert()
        product_insert()
        product_update()

    @testReport.stepResults.step("Отправка json")
    def ttn_4_json_send():
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
    def ttn_4_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))
            if result:
                logger.debug(f'Сообщение найдено: {result}')
                assert True, f"Сообщение найдено: {result}"
            else:
                db_selecter = Outbox_checker('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                result = db_selecter.selecter(sender.uuid)
                comment = db_selecter.get_comment(result)

                if not comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                elif comment is None:
                    logger.error('Сообщение не найдено (None)')
                    assert False, "Сообщение не найдено"
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    ttn_4_forma()
    ttn_4_gen_xml()
    ttn_4_insert_db()
    ttn_4_json_send()
    ttn_4_result_checker()

@testReport.stepResults.title("Отправка waybill_v4 немаркированная фасованная")
def TTN_4_isPacked_test():
    corr_xml = None
    forming = None
    params = None
    sender = None
    form_A = None

    @testReport.stepResults.step("Получение информации из БД")
    def ttn_4_forma():
        nonlocal form_A
        testReport.stepResults.description("Ведем поиск последней FormA")
        logger.debug("Ведем поиск последней FormA")
        try:
            db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT reg_id FROM registry.form_a AS x order by reg_id DESC limit 1"

            form = db_ins.inserter()
            logger.debug(form)

            if form:
                form_A = form[0][0]

                logger.debug('Обновили форму 1 документа')
                assert True, "Обновили форму 1 документа"
            else:
                logger.debug('ФормА не найдена, используем пример формы А')
                assert True, "Используем хардкод формы А"

        except Exception as e:
            logger.error(f'Ошибка обновлении формы А: {e}')
            assert False, e

    @testReport.stepResults.step("Генерация xml")
    def ttn_4_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='waybill_v4')

            forming.isMark = False
            forming.isUnPacked = False

            forming.formA = form_A

            corr_xml = forming.generate_WayBill_4()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставки в БД")
    def ttn_4_insert_db():

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

        doc_insert()
        product_insert()
        product_update()

    @testReport.stepResults.step("Отправка json")
    def ttn_4_json_send():
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
    def ttn_4_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))
            if result:
                logger.debug(f'Сообщение найдено: {result}')
                assert True, f"Сообщение найдено: {result}"
            else:
                db_selecter = Outbox_checker('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                result = db_selecter.selecter(sender.uuid)
                comment = db_selecter.get_comment(result)

                if not comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                elif comment is None:
                    logger.error('Сообщение не найдено (None)')
                    assert False, "Сообщение не найдено"
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    ttn_4_forma()
    ttn_4_gen_xml()
    ttn_4_insert_db()
    ttn_4_json_send()
    ttn_4_result_checker()

@testReport.stepResults.title("Отправка waybill_v4 немаркированная нефасованная")
def TTN_4_isUnPacked_test():
    corr_xml = None
    forming = None
    params = None
    sender = None
    form_A = None

    @testReport.stepResults.step("Получение информации из БД")
    def ttn_4_forma():
        nonlocal form_A
        testReport.stepResults.description("Ведем поиск последней FormA")
        logger.debug("Ведем поиск последней FormA")
        try:
            db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT reg_id FROM registry.form_a AS x order by reg_id DESC limit 1"

            form = db_ins.inserter()
            logger.debug(form)

            if form:
                form_A = form[0][0]

                logger.debug('Обновили форму 1 документа')
                assert True, "Обновили форму 1 документа"
            else:
                logger.debug('ФормА не найдена, используем пример формы А')
                assert True, "Используем хардкод формы А"

        except Exception as e:
            logger.error(f'Ошибка обновлении формы А: {e}')
            assert False, e

    @testReport.stepResults.step("Генерация xml")
    def ttn_4_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='waybill_v4')

            forming.isMark = False
            forming.isUnPacked = True

            forming.formA = form_A

            corr_xml = forming.generate_WayBill_4()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставки в БД")
    def ttn_4_insert_db():

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

        doc_insert()
        product_insert()
        product_update()

    @testReport.stepResults.step("Отправка json")
    def ttn_4_json_send():
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
    def ttn_4_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))
            if result:
                logger.debug(f'Сообщение найдено: {result}')
                assert True, f"Сообщение найдено: {result}"
            else:
                db_selecter = Outbox_checker('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                result = db_selecter.selecter(sender.uuid)
                comment = db_selecter.get_comment(result)

                if not comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                elif comment is None:
                    logger.error('Сообщение не найдено (None)')
                    assert False, "Сообщение не найдено"
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    ttn_4_forma()
    ttn_4_gen_xml()
    ttn_4_insert_db()
    ttn_4_json_send()
    ttn_4_result_checker()


@testReport.stepResults.title("Отправка actwriteoff_v3 маркированная")
def AWO_3_mark_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def awo_3_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='actwriteoff_v3')

            forming.isMark = True
            forming.isUnPacked = False

            corr_xml = forming.generate_AWO_v3()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставки в БД")
    def awo_3_insert_db():

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

        doc_insert()
        product_insert()
        product_update()

    @testReport.stepResults.step("Отправка json")
    def awo_3_json_send():
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
    def awo_3_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))
            if result:
                logger.debug(f'Сообщение найдено: {result}')
                assert True, f"Сообщение найдено: {result}"
            else:
                db_selecter = Outbox_checker('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                result = db_selecter.selecter(sender.uuid)
                comment = db_selecter.get_comment(result)

                if not comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                elif comment is None:
                    logger.error('Сообщение не найдено (None)')
                    assert False, "Сообщение не найдено"
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    awo_3_gen_xml()
    awo_3_insert_db()
    awo_3_json_send()
    awo_3_result_checker()

@testReport.stepResults.title("Отправка actwriteoff_v3 немаркированная фасованная")
def AWO_3_isPacked_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def awo_3_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='actwriteoff_v3')

            forming.isMark = False
            forming.isUnPacked = False

            corr_xml = forming.generate_AWO_v3()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставки в БД")
    def awo_3_insert_db():

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

        doc_insert()
        product_insert()
        product_update()

    @testReport.stepResults.step("Отправка json")
    def awo_3_json_send():
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
    def awo_3_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))
            if result:
                logger.debug(f'Сообщение найдено: {result}')
                assert True, f"Сообщение найдено: {result}"
            else:
                db_selecter = Outbox_checker('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                result = db_selecter.selecter(sender.uuid)
                comment = db_selecter.get_comment(result)

                if not comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                elif comment is None:
                    logger.error('Сообщение не найдено (None)')
                    assert False, "Сообщение не найдено"
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    awo_3_gen_xml()
    awo_3_insert_db()
    awo_3_json_send()
    awo_3_result_checker()

@testReport.stepResults.title("Отправка actwriteoff_v3 немаркированная нефасованная")
def AWO_3_isUnPacked_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def awo_3_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='actwriteoff_v3')

            forming.isMark = False
            forming.isUnPacked = True

            corr_xml = forming.generate_AWO_v3()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставки в БД")
    def awo_3_insert_db():

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

        doc_insert()
        product_insert()
        product_update()

    @testReport.stepResults.step("Отправка json")
    def awo_3_json_send():
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
    def awo_3_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid))
            if result:
                logger.debug(f'Сообщение найдено: {result}')
                assert True, f"Сообщение найдено: {result}"
            else:
                db_selecter = Outbox_checker('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                result = db_selecter.selecter(sender.uuid)
                comment = db_selecter.get_comment(result)

                if not comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                elif comment is None:
                    logger.error('Сообщение не найдено (None)')
                    assert False, "Сообщение не найдено"
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    awo_3_gen_xml()
    awo_3_insert_db()
    awo_3_json_send()
    awo_3_result_checker()


if __name__ == "__main__":
    # Запуск всех тестов
    testReport.run_tests(
        test_functions=[RPP_4_mark_test,
                        RPP_4_isPacked_test,
                        RPP_4_isUnPacked_test,
                        RIP_4_mark_test,
                        RIP_4_isPacked_test,
                        RIP_4_isUnPacked_test,
                        ACO_2_mark_test,
                        ACO_2_isPacked_test,
                        ACO_2_isUnPacked_test,
                        TTN_4_mark_test,
                        TTN_4_isPacked_test,
                        TTN_4_isUnPacked_test,
                        AWO_3_mark_test,
                        AWO_3_isPacked_test,
                        AWO_3_isUnPacked_test],
        setup_teardown_func=setup_teardown
    )