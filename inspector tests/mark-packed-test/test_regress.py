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
testReport.parameter("environment", "ibark")


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


@testReport.stepResults.title("СМОК-тестирование repproducedproduct_v4 маркированная")
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
            corr_xml = forming.generate_RPP_4()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Получение информации из БД")
    def rpp_4_docId():
        testReport.stepResults.description("Ведем поиск последнего DocId")
        logger.debug("Ведем поиск последнего DocId")
        try:
            prefix = forming.docId.split("-")[0]
            db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT dtype FROM inbox.prefixes where prefix = '{prefix}'"

            docType = db_ins.inserter()

            db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"SELECT nextval('inbox.{docType[0][0]}');"

            new_docId = db_ins2.inserter()
            logger.debug(new_docId)

            if new_docId:
                id = new_docId[0][0]
                forming.update_docId(id)
                logger.debug('Обновили ид документа')
                assert True, "Обновили ид документа"
            else:
                logger.debug('DocId не найден, используем пример docId')
                forming.plus_docId()
                assert True, "Сгенерировали свой DocId"

        except Exception as e:
            logger.error(f'Ошибка обновлении докИд: {e}')
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
            sender = Kafka_sender(forming.doc_type, params[1], 'svs-inspector', forming.docId)
            sender.send()
            logger.debug('Успех отправки json')
            assert True, "Успех отправки json"
        except Exception as e:
            logger.error(f'Ошибка при отправке json: {e}')
            assert False, e

    @testReport.stepResults.step("Поиск результата")
    def rpp_4_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid), topic='crater')
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
    rpp_4_docId()
    rpp_4_insert_db()
    rpp_4_json_send()
    rpp_4_result_checker()


@testReport.stepResults.title("СМОК-тестирование repproducedproduct_v4 немаркированная фасованная")
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

    @testReport.stepResults.step("Получение информации из БД")
    def rpp_4_docId():
        testReport.stepResults.description("Ведем поиск последнего DocId")
        logger.debug("Ведем поиск последнего DocId")
        try:
            prefix = forming.docId.split("-")[0]
            db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT dtype FROM inbox.prefixes where prefix = '{prefix}'"

            docType = db_ins.inserter()

            db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"SELECT nextval('inbox.{docType[0][0]}');"

            new_docId = db_ins2.inserter()
            logger.debug(new_docId)

            if new_docId:
                id = new_docId[0][0]
                forming.update_docId(id)
                logger.debug('Обновили ид документа')
                assert True, "Обновили ид документа"
            else:
                logger.debug('DocId не найден, используем пример docId')
                forming.plus_docId()
                assert True, "Сгенерировали свой DocId"

        except Exception as e:
            logger.error(f'Ошибка обновлении докИд: {e}')
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
            sender = Kafka_sender(forming.doc_type, params[1], 'svs-inspector', forming.docId)
            sender.send()
            logger.debug('Успех отправки json')
            assert True, "Успех отправки json"
        except Exception as e:
            logger.error(f'Ошибка при отправке json: {e}')
            assert False, e

    @testReport.stepResults.step("Поиск результата")
    def rpp_4_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid), topic='crater')
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
    rpp_4_docId()
    rpp_4_insert_db()
    rpp_4_json_send()
    rpp_4_result_checker()


@testReport.stepResults.title("СМОК-тестирование repproducedproduct_v4 немаркированная нефасованная")
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

    @testReport.stepResults.step("Получение информации из БД")
    def rpp_4_docId():
        testReport.stepResults.description("Ведем поиск последнего DocId")
        logger.debug("Ведем поиск последнего DocId")
        try:
            prefix = forming.docId.split("-")[0]
            db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT dtype FROM inbox.prefixes where prefix = '{prefix}'"

            docType = db_ins.inserter()

            db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"SELECT nextval('inbox.{docType[0][0]}');"

            new_docId = db_ins2.inserter()
            logger.debug(new_docId)

            if new_docId:
                id = new_docId[0][0]
                forming.update_docId(id)
                logger.debug('Обновили ид документа')
                assert True, "Обновили ид документа"
            else:
                logger.debug('DocId не найден, используем пример docId')
                forming.plus_docId()
                assert True, "Сгенерировали свой DocId"

        except Exception as e:
            logger.error(f'Ошибка обновлении докИд: {e}')
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
            sender = Kafka_sender(forming.doc_type, params[1], 'svs-inspector', forming.docId)
            sender.send()
            logger.debug('Успех отправки json')
            assert True, "Успех отправки json"
        except Exception as e:
            logger.error(f'Ошибка при отправке json: {e}')
            assert False, e

    @testReport.stepResults.step("Поиск результата")
    def rpp_4_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid), topic='crater')
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
    rpp_4_docId()
    rpp_4_insert_db()
    rpp_4_json_send()
    rpp_4_result_checker()


@testReport.stepResults.title("СМОК-тестирование repimportedproduct_v4 маркированная")
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
            corr_xml = forming.generate_RIP_4()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Получение информации из БД")
    def rip_4_docId():
        testReport.stepResults.description("Ведем поиск последнего DocId")
        logger.debug("Ведем поиск последнего DocId")
        try:
            prefix = forming.docId.split("-")[0]
            db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT dtype FROM inbox.prefixes where prefix = '{prefix}'"

            docType = db_ins.inserter()

            db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"SELECT nextval('inbox.{docType[0][0]}');"

            new_docId = db_ins2.inserter()
            logger.debug(new_docId)

            if new_docId:
                id = new_docId[0][0]
                forming.update_docId(id)
                logger.debug('Обновили ид документа')
                assert True, "Обновили ид документа"
            else:
                logger.debug('DocId не найден, используем пример docId')
                forming.plus_docId()
                assert True, "Сгенерировали свой DocId"

        except Exception as e:
            logger.error(f'Ошибка обновлении докИд: {e}')
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
            sender = Kafka_sender(forming.doc_type, params[1], 'svs-inspector', forming.docId)
            sender.send()
            logger.debug('Успех отправки json')
            assert True, "Успех отправки json"
        except Exception as e:
            logger.error(f'Ошибка при отправке json: {e}')
            assert False, e

    @testReport.stepResults.step("Поиск результата")
    def rip_4_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid), topic='crater')
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
    rip_4_docId()
    rip_4_insert_db()
    rip_4_json_send()
    rip_4_result_checker()


@testReport.stepResults.title("СМОК-тестирование repimportedproduct_v4 немаркированная фасованная")
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

    @testReport.stepResults.step("Получение информации из БД")
    def rip_4_docId():
        testReport.stepResults.description("Ведем поиск последнего DocId")
        logger.debug("Ведем поиск последнего DocId")
        try:
            prefix = forming.docId.split("-")[0]
            db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT dtype FROM inbox.prefixes where prefix = '{prefix}'"

            docType = db_ins.inserter()

            db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"SELECT nextval('inbox.{docType[0][0]}');"

            new_docId = db_ins2.inserter()
            logger.debug(new_docId)

            if new_docId:
                id = new_docId[0][0]
                forming.update_docId(id)
                logger.debug('Обновили ид документа')
                assert True, "Обновили ид документа"
            else:
                logger.debug('DocId не найден, используем пример docId')
                forming.plus_docId()
                assert True, "Сгенерировали свой DocId"

        except Exception as e:
            logger.error(f'Ошибка обновлении докИд: {e}')
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
            sender = Kafka_sender(forming.doc_type, params[1], 'svs-inspector', forming.docId)
            sender.send()
            logger.debug('Успех отправки json')
            assert True, "Успех отправки json"
        except Exception as e:
            logger.error(f'Ошибка при отправке json: {e}')
            assert False, e

    @testReport.stepResults.step("Поиск результата")
    def rip_4_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid), topic='crater')
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
    rip_4_docId()
    rip_4_insert_db()
    rip_4_json_send()
    rip_4_result_checker()


@testReport.stepResults.title("СМОК-тестирование repimportedproduct_v4 немаркированная нефасованная")
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

    @testReport.stepResults.step("Получение информации из БД")
    def rip_4_docId():
        testReport.stepResults.description("Ведем поиск последнего DocId")
        logger.debug("Ведем поиск последнего DocId")
        try:
            prefix = forming.docId.split("-")[0]
            db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT dtype FROM inbox.prefixes where prefix = '{prefix}'"

            docType = db_ins.inserter()

            db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"SELECT nextval('inbox.{docType[0][0]}');"

            new_docId = db_ins2.inserter()
            logger.debug(new_docId)

            if new_docId:
                id = new_docId[0][0]
                forming.update_docId(id)
                logger.debug('Обновили ид документа')
                assert True, "Обновили ид документа"
            else:
                logger.debug('DocId не найден, используем пример docId')
                forming.plus_docId()
                assert True, "Сгенерировали свой DocId"

        except Exception as e:
            logger.error(f'Ошибка обновлении докИд: {e}')
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
            sender = Kafka_sender(forming.doc_type, params[1], 'svs-inspector', forming.docId)
            sender.send()
            logger.debug('Успех отправки json')
            assert True, "Успех отправки json"
        except Exception as e:
            logger.error(f'Ошибка при отправке json: {e}')
            assert False, e

    @testReport.stepResults.step("Поиск результата")
    def rip_4_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid), topic='crater')
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
    rip_4_docId()
    rip_4_insert_db()
    rip_4_json_send()
    rip_4_result_checker()


@testReport.stepResults.title("СМОК-тестирование actchargeon_v2 маркированная")
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
            corr_xml = forming.generate_ACO_2()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Получение информации из БД")
    def aco_2_docId():
        testReport.stepResults.description("Ведем поиск последнего DocId")
        logger.debug("Ведем поиск последнего DocId")
        try:
            prefix = forming.docId.split("-")[0]
            db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT dtype FROM inbox.prefixes where prefix = '{prefix}'"

            docType = db_ins.inserter()

            db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"SELECT nextval('inbox.{docType[0][0]}');"

            new_docId = db_ins2.inserter()
            logger.debug(new_docId)

            if new_docId:
                id = new_docId[0][0]
                forming.update_docId(id)
                logger.debug('Обновили ид документа')
                assert True, "Обновили ид документа"
            else:
                logger.debug('DocId не найден, используем пример docId')
                forming.plus_docId()
                assert True, "Сгенерировали свой DocId"

        except Exception as e:
            logger.error(f'Ошибка обновлении докИд: {e}')
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
            sender = Kafka_sender(forming.doc_type, params[1], 'svs-inspector', forming.docId)
            sender.send()
            logger.debug('Успех отправки json')
            assert True, "Успех отправки json"
        except Exception as e:
            logger.error(f'Ошибка при отправке json: {e}')
            assert False, e

    @testReport.stepResults.step("Поиск результата")
    def aco_2_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid), topic='crater')
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
    aco_2_docId()
    aco_2_insert_db()
    aco_2_json_send()
    aco_2_result_checker()


@testReport.stepResults.title("СМОК-тестирование actchargeon_v2 немаркированная фасованная")
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

    @testReport.stepResults.step("Получение информации из БД")
    def aco_2_docId():
        testReport.stepResults.description("Ведем поиск последнего DocId")
        logger.debug("Ведем поиск последнего DocId")
        try:
            prefix = forming.docId.split("-")[0]
            db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT dtype FROM inbox.prefixes where prefix = '{prefix}'"

            docType = db_ins.inserter()

            db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"SELECT nextval('inbox.{docType[0][0]}');"

            new_docId = db_ins2.inserter()
            logger.debug(new_docId)

            if new_docId:
                id = new_docId[0][0]
                forming.update_docId(id)
                logger.debug('Обновили ид документа')
                assert True, "Обновили ид документа"
            else:
                logger.debug('DocId не найден, используем пример docId')
                forming.plus_docId()
                assert True, "Сгенерировали свой DocId"

        except Exception as e:
            logger.error(f'Ошибка обновлении докИд: {e}')
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
            sender = Kafka_sender(forming.doc_type, params[1], 'svs-inspector', forming.docId)
            sender.send()
            logger.debug('Успех отправки json')
            assert True, "Успех отправки json"
        except Exception as e:
            logger.error(f'Ошибка при отправке json: {e}')
            assert False, e

    @testReport.stepResults.step("Поиск результата")
    def aco_2_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid), topic='crater')
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
    aco_2_docId()
    aco_2_insert_db()
    aco_2_json_send()
    aco_2_result_checker()


@testReport.stepResults.title("СМОК-тестирование actchargeon_v2 немаркированная нефасованная")
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

    @testReport.stepResults.step("Получение информации из БД")
    def aco_2_docId():
        testReport.stepResults.description("Ведем поиск последнего DocId")
        logger.debug("Ведем поиск последнего DocId")
        try:
            prefix = forming.docId.split("-")[0]
            db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT dtype FROM inbox.prefixes where prefix = '{prefix}'"

            docType = db_ins.inserter()

            db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"SELECT nextval('inbox.{docType[0][0]}');"

            new_docId = db_ins2.inserter()
            logger.debug(new_docId)

            if new_docId:
                id = new_docId[0][0]
                forming.update_docId(id)
                logger.debug('Обновили ид документа')
                assert True, "Обновили ид документа"
            else:
                logger.debug('DocId не найден, используем пример docId')
                forming.plus_docId()
                assert True, "Сгенерировали свой DocId"

        except Exception as e:
            logger.error(f'Ошибка обновлении докИд: {e}')
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
            sender = Kafka_sender(forming.doc_type, params[1], 'svs-inspector', forming.docId)
            sender.send()
            logger.debug('Успех отправки json')
            assert True, "Успех отправки json"
        except Exception as e:
            logger.error(f'Ошибка при отправке json: {e}')
            assert False, e

    @testReport.stepResults.step("Поиск результата")
    def aco_2_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid), topic='crater')
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
    aco_2_docId()
    aco_2_insert_db()
    aco_2_json_send()
    aco_2_result_checker()


@testReport.stepResults.title("СМОК-тестирование actwriteoff_v3 маркированная")
def AWO_3_mark_test():
    corr_xml = None
    forming = None
    params = None
    sender = None
    forming = Forming_xml(doc_type='actwriteoff_v3')

    @testReport.stepResults.step("Поиск марки для списания")
    def awo_3_get_bcode():
        nonlocal forming
        testReport.stepResults.description("Ведем поиск марки для списания")
        logger.debug("Ведем поиск марки для списания")
        try:
            db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT code, val FROM balance_{forming.fsrar} order by id desc limit 1"

            data = db_ins.inserter()
            logger.debug(data)

            if data:
                forming.bcode = data[0][0]
                forming.formB = data[0][1]
                logger.debug('Обновили информацию о марке')
                assert True, "Обновили информацию о марке"
            else:
                logger.debug('Марки отсутствуют')
                assert True, "Нет информации по маркам"

        except Exception as e:
            logger.error(f'Ошибка обновлении информации по марке: {e}')
            assert False, e

    @testReport.stepResults.step("Генерация xml")
    def awo_3_gen_xml():
        nonlocal corr_xml, forming
        try:

            forming.isMark = True
            forming.isUnPacked = True

            corr_xml = forming.generate_AWO_3()

            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Получение информации из БД")
    def awo_3_docId():
        testReport.stepResults.description("Ведем поиск последнего DocId")
        logger.debug("Ведем поиск последнего DocId")
        try:
            prefix = forming.docId.split("-")[0]
            db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT dtype FROM inbox.prefixes where prefix = '{prefix}'"

            docType = db_ins.inserter()

            db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"SELECT nextval('inbox.{docType[0][0]}');"

            new_docId = db_ins2.inserter()
            logger.debug(new_docId)

            if new_docId:
                id = new_docId[0][0]
                forming.update_docId(id)
                logger.debug('Обновили ид документа')
                assert True, "Обновили ид документа"
            else:
                logger.debug('DocId не найден, используем пример docId')
                forming.plus_docId()
                assert True, "Сгенерировали свой DocId"

        except Exception as e:
            logger.error(f'Ошибка обновлении докИд: {e}')
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
            sender = Kafka_sender(forming.doc_type, params[1], 'svs-inspector', forming.docId)
            sender.send()
            logger.debug('Успех отправки json')
            assert True, "Успех отправки json"
        except Exception as e:
            logger.error(f'Ошибка при отправке json: {e}')
            assert False, e

    @testReport.stepResults.step("Поиск результата")
    def awo_3_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid), topic='crater')
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
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    awo_3_get_bcode()
    awo_3_gen_xml()
    awo_3_docId()
    awo_3_insert_db()
    awo_3_json_send()
    awo_3_result_checker()


@testReport.stepResults.title("СМОК-тестирование actwriteoff_v3 немаркированная фасованная")
def AWO_3_isPacked_test():
    corr_xml = None
    forming = None
    params = None
    sender = None
    forming = Forming_xml(doc_type='actwriteoff_v3')

    @testReport.stepResults.step("Поиск FB для списания")
    def awo_3_get_formb():
        nonlocal forming
        testReport.stepResults.description("Ведем поиск марки для списания")
        logger.debug("Ведем поиск марки для списания")
        try:
            k = 0
            FB = ""
            while FB == "":
                db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                db_ins.sql_req = f"select formb from registry.documents where fsrarid = '{forming.fsrar}' and dtype = 'actchargeon_v2' order by id desc limit 1 offset {k}"

                data = db_ins.inserter()
                logger.debug(data)

                FBofficial = f"FB-{data[0][0]:015d}"

                db_ins2 = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                db_ins2.sql_req = f"select code from public.balance_{forming.fsrar} where val = '{FBofficial}'"

                data2 = db_ins2.inserter()
                logger.debug(data2)

                db_ins3 = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                db_ins3.sql_req = f"select 1 from public.nomark_{forming.fsrar} where code = '{FBofficial}'"

                data3 = db_ins3.inserter()
                logger.debug(data3)

                if data2 == [] and data3 != []:
                    FB = FBofficial
                k += 1

            if FB:
                forming.formB = FB
                logger.debug('Обновили информацию о форме Б')
                assert True, "Обновили информацию о форме Б"
            else:
                logger.debug('Форма Б отсутствует')
                assert True, "Нет информации по формам"

        except Exception as e:
            logger.error(f'Ошибка обновлении информации по форме: {e}')
            assert False, e

    @testReport.stepResults.step("Генерация xml")
    def awo_3_gen_xml():
        nonlocal corr_xml, forming
        try:

            forming.isMark = False
            forming.isUnPacked = False

            corr_xml = forming.generate_AWO_3()

            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Получение информации из БД")
    def awo_3_docId():
        testReport.stepResults.description("Ведем поиск последнего DocId")
        logger.debug("Ведем поиск последнего DocId")
        try:
            prefix = forming.docId.split("-")[0]
            db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT dtype FROM inbox.prefixes where prefix = '{prefix}'"

            docType = db_ins.inserter()

            db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"SELECT nextval('inbox.{docType[0][0]}');"

            new_docId = db_ins2.inserter()
            logger.debug(new_docId)

            if new_docId:
                id = new_docId[0][0]
                forming.update_docId(id)
                logger.debug('Обновили ид документа')
                assert True, "Обновили ид документа"
            else:
                logger.debug('DocId не найден, используем пример docId')
                forming.plus_docId()
                assert True, "Сгенерировали свой DocId"

        except Exception as e:
            logger.error(f'Ошибка обновлении докИд: {e}')
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
            sender = Kafka_sender(forming.doc_type, params[1], 'svs-inspector', forming.docId)
            sender.send()
            logger.debug('Успех отправки json')
            assert True, "Успех отправки json"
        except Exception as e:
            logger.error(f'Ошибка при отправке json: {e}')
            assert False, e

    @testReport.stepResults.step("Поиск результата")
    def awo_3_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid), topic='crater')
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
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    awo_3_get_formb()
    awo_3_gen_xml()
    awo_3_docId()
    awo_3_insert_db()
    awo_3_json_send()
    awo_3_result_checker()


@testReport.stepResults.title("СМОК-тестирование actwriteoff_v3 немаркированная нефасованная")
def AWO_3_isUnPacked_test():
    corr_xml = None
    forming = None
    params = None
    sender = None
    forming = Forming_xml(doc_type='actwriteoff_v3')

    @testReport.stepResults.step("Поиск FB для списания")
    def awo_3_get_formb():
        nonlocal forming
        testReport.stepResults.description("Ведем поиск марки для списания")
        logger.debug("Ведем поиск марки для списания")
        try:
            k = 0
            FB = ""
            while FB == "":
                db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                db_ins.sql_req = f"select formb from registry.documents where fsrarid = '{forming.fsrar}' and dtype = 'actchargeon_v2' order by id desc limit 1 offset {k}"

                data = db_ins.inserter()
                logger.debug(data)

                FBofficial = f"FB-{data[0][0]:015d}"

                db_ins2 = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                db_ins2.sql_req = f"select code from public.balance_{forming.fsrar} where val = '{FBofficial}'"

                data2 = db_ins2.inserter()
                logger.debug(data2)

                db_ins3 = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                db_ins3.sql_req = f"select 1 from public.nomark_{forming.fsrar} where code = '{FBofficial}'"

                data3 = db_ins3.inserter()
                logger.debug(data3)

                if data2 == [] and data3 != []:
                    FB = FBofficial
                k += 1

            if FB:
                forming.formB = FB
                logger.debug('Обновили информацию о форме Б')
                assert True, "Обновили информацию о форме Б"
            else:
                logger.debug('Форма Б отсутствует')
                assert True, "Нет информации по формам"

        except Exception as e:
            logger.error(f'Ошибка обновлении информации по форме: {e}')
            assert False, e

    @testReport.stepResults.step("Генерация xml")
    def awo_3_gen_xml():
        nonlocal corr_xml, forming
        try:

            forming.isMark = False
            forming.isUnPacked = True

            corr_xml = forming.generate_AWO_3()

            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Получение информации из БД")
    def awo_3_docId():
        testReport.stepResults.description("Ведем поиск последнего DocId")
        logger.debug("Ведем поиск последнего DocId")
        try:
            prefix = forming.docId.split("-")[0]
            db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT dtype FROM inbox.prefixes where prefix = '{prefix}'"

            docType = db_ins.inserter()

            db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"SELECT nextval('inbox.{docType[0][0]}');"

            new_docId = db_ins2.inserter()
            logger.debug(new_docId)

            if new_docId:
                id = new_docId[0][0]
                forming.update_docId(id)
                logger.debug('Обновили ид документа')
                assert True, "Обновили ид документа"
            else:
                logger.debug('DocId не найден, используем пример docId')
                forming.plus_docId()
                assert True, "Сгенерировали свой DocId"

        except Exception as e:
            logger.error(f'Ошибка обновлении докИд: {e}')
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
            sender = Kafka_sender(forming.doc_type, params[1], 'svs-inspector', forming.docId)
            sender.send()
            logger.debug('Успех отправки json')
            assert True, "Успех отправки json"
        except Exception as e:
            logger.error(f'Ошибка при отправке json: {e}')
            assert False, e

    @testReport.stepResults.step("Поиск результата")
    def awo_3_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid), topic='crater')
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
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    awo_3_get_formb()
    awo_3_gen_xml()
    awo_3_docId()
    awo_3_insert_db()
    awo_3_json_send()
    awo_3_result_checker()


@testReport.stepResults.title("СМОК-тестирование actfixbarcode маркированная")
def AFBC_mark_test():
    corr_xml = None
    forming = None
    params = None
    sender = None
    forming = Forming_xml(doc_type='actfixbarcode')

    @testReport.stepResults.step("Поиск марки для списания")
    def afbc_get_bcode():
        nonlocal forming
        testReport.stepResults.description("Ведем поиск марки для списания")
        logger.debug("Ведем поиск марки для списания")
        try:
            db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT code, val FROM public.archive where val like '%{forming.fsrar}%' order by id desc limit 1"

            data = db_ins.inserter()
            logger.debug(data)

            bcode = data[0][0]
            val = data[0][1]

            # val_hash_dec = val.split(':')[0]
            #
            # db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            # db_ins.sql_req = f"SELECT code, val FROM public.archive where val like '%{forming.fsrar}%' order by id desc limit 1"
            #
            # data = db_ins.inserter()
            # logger.debug(data)

            if data:
                forming.bcode = bcode
                # forming.formB = data[0][1]
                logger.debug('Обновили информацию о марке')
                assert True, "Обновили информацию о марке"
            else:
                logger.debug('Марки отсутствуют')
                assert True, "Нет информации по маркам"

        except Exception as e:
            logger.error(f'Ошибка обновлении информации по марке: {e}')
            assert False, e

    @testReport.stepResults.step("Генерация xml")
    def afbc_gen_xml():
        nonlocal corr_xml, forming
        try:

            forming.isMark = True
            forming.isUnPacked = True

            corr_xml = forming.generate_AFBC()

            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Получение информации из БД")
    def afbc_docId():
        testReport.stepResults.description("Ведем поиск последнего DocId")
        logger.debug("Ведем поиск последнего DocId")
        try:
            prefix = forming.docId.split("-")[0]
            db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT dtype FROM inbox.prefixes where prefix = '{prefix}'"

            docType = db_ins.inserter()

            db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"SELECT nextval('inbox.{docType[0][0]}');"

            new_docId = db_ins2.inserter()
            logger.debug(new_docId)

            if new_docId:
                id = new_docId[0][0]
                forming.update_docId(id)
                logger.debug('Обновили ид документа')
                assert True, "Обновили ид документа"
            else:
                logger.debug('DocId не найден, используем пример docId')
                forming.plus_docId()
                assert True, "Сгенерировали свой DocId"

        except Exception as e:
            logger.error(f'Ошибка обновлении докИд: {e}')
            assert False, e

    @testReport.stepResults.step("Вставки в БД")
    def afbc_insert_db():

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
    def afbc_json_send():
        nonlocal sender
        testReport.stepResults.description("Отправляем json на обработку в inspector в confirmed")
        try:
            sender = Kafka_sender(forming.doc_type, params[1], 'svs-inspector', forming.docId)
            sender.send()
            logger.debug('Успех отправки json')
            assert True, "Успех отправки json"
        except Exception as e:
            logger.error(f'Ошибка при отправке json: {e}')
            assert False, e

    @testReport.stepResults.step("Поиск результата")
    def afbc_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid), topic='crater')
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
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    afbc_get_bcode()
    afbc_gen_xml()
    afbc_docId()
    afbc_insert_db()
    afbc_json_send()
    afbc_result_checker()


@testReport.stepResults.title("СМОК-тестирование waybill_v4 маркированная")
def TTN_4_mark_test():
    corr_xml = None
    forming = None
    params = None
    sender = None
    RPP_docId = None
    formA = None
    formB = None
    bcode = None
    corr_xml_v2 = None
    logger.debug('Запуск тестов для TTN_4_mark')

    @testReport.stepResults.step("Производство продукции посредством RPP_v4")
    def RPP_4_mark_send():
        nonlocal RPP_docId
        corr_xml = None
        forming = None
        params = None
        sender = None

        @testReport.stepResults.step("Генерация xml")
        def rpp_4_gen_xml():
            nonlocal corr_xml, forming
            try:
                forming = Forming_xml(doc_type='repproducedproduct_v4')
                corr_xml = forming.generate_RPP_4()
                logger.debug('Успех генерации xml')
                assert True, "Успех генерации xml"
            except Exception as e:
                logger.error(f'Ошибка при генерации xml: {e}')
                assert False, e

        @testReport.stepResults.step("Получение информации из БД")
        def rpp_4_docId():
            nonlocal RPP_docId
            testReport.stepResults.description("Ведем поиск последнего DocId")
            logger.debug("Ведем поиск последнего DocId")
            try:
                prefix = forming.docId.split("-")[0]
                db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                db_ins.sql_req = f"SELECT dtype FROM inbox.prefixes where prefix = '{prefix}'"

                docType = db_ins.inserter()

                db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                db_ins2.sql_req = f"SELECT nextval('inbox.{docType[0][0]}');"

                new_docId = db_ins2.inserter()
                logger.debug(new_docId)

                if new_docId:
                    id = new_docId[0][0]
                    forming.update_docId(id)
                    RPP_docId = forming.docId
                    logger.debug(f'Записали RPP_docId = {RPP_docId}')
                    logger.debug('Обновили ид документа')
                    assert True, "Обновили ид документа"
                else:
                    logger.debug('DocId не найден, используем пример docId')
                    forming.plus_docId()
                    assert True, "Сгенерировали свой DocId"

            except Exception as e:
                logger.error(f'Ошибка обновлении докИд: {e}')
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
                sender = Kafka_sender(forming.doc_type, params[1], 'svs-inspector', forming.docId)
                sender.send()
                logger.debug('Успех отправки json')
                assert True, "Успех отправки json"
            except Exception as e:
                logger.error(f'Ошибка при отправке json: {e}')
                assert False, e

        @testReport.stepResults.step("Поиск результата")
        def rpp_4_result_checker():
            testReport.stepResults.description("Ищем результат обработки xml в топике crater")
            try:
                result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid), topic='crater')
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
        rpp_4_docId()
        rpp_4_insert_db()
        rpp_4_json_send()
        rpp_4_result_checker()

    @testReport.stepResults.step("Получение Form из БД")
    def ttn_4_getForm():
        nonlocal RPP_docId, formA, formB, bcode
        testReport.stepResults.description("Ведем поиск Form A, B")
        logger.debug("Ведем поиск Form A, B")
        try:
            db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT reg_id FROM registry.form_a WHERE docid = '{RPP_docId}' ORDER BY id DESC"

            data = db_ins.inserter()
            logger.debug(f'Запрос в бд выполнен: {data}')

            formA = data[0][0]
            logger.debug(f'FormA найдена = {formA}')

            db_ins2 = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"SELECT reg_id FROM registry.form_b WHERE forma = '{formA}'"

            data2 = db_ins2.inserter()
            logger.debug(f'Запрос в бд выполнен: {data2}')

            formB = data2[0][0]
            logger.debug(f'FormB найдена = {formB}')

            db_ins3 = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins3.sql_req = f"SELECT code FROM public.balance_030000434308 where val = '{formB}' limit 1"

            data3 = db_ins3.inserter()
            logger.debug(data3)

            bcode = data3[0][0]

        except Exception as e:
            logger.error(f'Ошибка поиска Form A, B: {e}')
            assert False, e

    @testReport.stepResults.step("Генерация xml ttn")
    def ttn_4_gen_xml():
        nonlocal corr_xml, forming, RPP_docId, formA, formB, bcode
        try:
            forming = Forming_xml(doc_type='waybill_v4')

            forming.formA = formA
            forming.formB = formB
            forming.bcode = bcode

            forming.isMark = True
            corr_xml = forming.generate_TTN()

            logger.debug(f"Генерируем {forming.doc_type}, получили RPP - {RPP_docId}")
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Получение информации из БД")
    def ttn_4_docId():
        testReport.stepResults.description("Ведем поиск последнего DocId")
        logger.debug("Ведем поиск последнего DocId")
        try:
            prefix = forming.docId.split("-")[0]
            db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins.sql_req = f"SELECT dtype FROM inbox.prefixes where prefix = '{prefix}'"

            docType = db_ins.inserter()

            db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"SELECT nextval('inbox.{docType[0][0]}');"

            new_docId = db_ins2.inserter()
            logger.debug(new_docId)

            if new_docId:
                id = new_docId[0][0]
                forming.update_docId(id)
                logger.debug('Обновили ид документа')
                assert True, "Обновили ид документа"
            else:
                logger.debug('DocId не найден, используем пример docId')
                forming.plus_docId()
                assert True, "Сгенерировали свой DocId"

        except Exception as e:
            logger.error(f'Ошибка обновлении докИд: {e}')
            assert False, e

    @testReport.stepResults.step("Генерация xml ttninformreg и отправка")
    def inforeg_gen():
        nonlocal forming, corr_xml_v2

        testReport.stepResults.description("Генерируем тикет")

        @testReport.stepResults.step("Генерация новой formB")
        def get_new_form():
            nonlocal forming


            isMark = 0

            if forming.isMark == True:
                isMark = 1
            else:
                isMark = 0

            testReport.stepResults.description("Генерируем новую форму Б")
            logger.debug("Генерируем новую форму Б")
            try:
                db_ins2 = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                db_ins2.sql_req = f"SELECT registry.get_formb('{forming.formB}', '{forming.formA}', '{forming.docId}', {isMark});"

                new_fb = db_ins2.inserter()
                logger.debug(new_fb)

                if new_fb:
                    forming.formB = new_fb[0][0]
                    logger.debug('Обновили формуБ')
                    assert True, "Обновили формуБ"
                else:
                    logger.debug('Ошибка в выполнении функции postgress')
                    assert False, "Ошибка в выполнении функции postgress"

            except Exception as e:
                logger.error(f'Ошибка обновлении form B: {e}')
                assert False, e

        @testReport.stepResults.step("Генерация xml ttninformf2reg")
        def gen_xml_inforeg():
            nonlocal corr_xml_v2, forming

            testReport.stepResults.description("Генерируем тикет ttninformf2reg")
            try:
                forming.doc_type='ttninformf2reg'
                corr_xml_v2 = forming.generate_TTNinformreg()
                forming.doc_type='waybill_v4'

                logger.debug('Успех генерации xml')
                assert True, "Успех генерации xml"
            except Exception as e:
                logger.error(f'Ошибка при генерации xml: {e}')
                assert False, e

        get_new_form()
        gen_xml_inforeg()

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

    @testReport.stepResults.step("Вставки в БД по info2reg")
    def insert_db_result():
            nonlocal corr_xml_v2, params, forming
            testReport.stepResults.description("Кладем сформированный документ в filedata.outbox")

            uuid_file = uuid.uuid4()
            try:
                db_ins = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                hex_xml = db_ins.text_to_hex(corr_xml_v2)
                query = f"INSERT INTO filedata.outboxdata (uri, inboxuri, filedata) VALUES('{uuid_file}', '{params[1]}', decode('{hex_xml}','hex'));"
                db_ins.sql_req = (query, params)  # Кортеж
                db_ins.inserter()
                logger.debug('Успех вставки в filedata')

                db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                query = f"INSERT INTO outbox.meta (fsrarid, state, ts, dsign, certhumbprint, uri, dtype, ts_update, ipaddress) VALUES('{forming.fsrar}', false, '2025-10-27 16:50:50.645', NULL, NULL, '{uuid_file}', 'ttninformf2reg', '2025-10-27 16:50:38.850', NULL);"
                db_ins2.sql_req = (query, params)  # Кортеж
                db_ins2.inserter()

                assert True, "Успех вставки в БД"
            except Exception as e:
                logger.error(f'Ошибка при вставке в БД: {e}')
                assert False, e

    @testReport.stepResults.step("Отправка json")
    def ttn_4_json_send():
        nonlocal sender, forming
        testReport.stepResults.description("Отправляем json на обработку в inspector в confirmed")
        try:
            sender = Kafka_sender(forming.doc_type, params[1], 'svs-inspector', forming.docId)
            sender.send()
            logger.debug('Успех отправки json')
            assert True, "Успех отправки json"
        except Exception as e:
            logger.error(f'Ошибка при отправке json: {e}')
            assert False, e

    @testReport.stepResults.step("Поиск результата")
    def ttn_4_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        try:
            result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid), topic='crater')
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
                elif 'принят системой на обработку' in comment:
                    logger.error('Сообщение не найдено')
                    assert False, "Сообщение не найдено"
                else:
                    logger.error(f'Получили {comment}')
                    assert False, f"Получили {comment}"
        except Exception as e:
            logger.error(f'Ошибка при поиске сообщения: {e}')
            assert False, f"Ошибка при поиске сообщения: {e}"

    RPP_4_mark_send()
    ttn_4_getForm()
    ttn_4_gen_xml()
    ttn_4_docId()
    inforeg_gen()
    ttn_4_insert_db()
    insert_db_result()
    ttn_4_json_send()
    ttn_4_result_checker()


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
                        AWO_3_mark_test,
                        AWO_3_isPacked_test,
                        AWO_3_isUnPacked_test,
                        # AFBC_mark_test,
                        TTN_4_mark_test],
        setup_teardown_func=setup_teardown
    )