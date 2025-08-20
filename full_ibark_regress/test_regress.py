from selfReportGEn2.testItReports import testReport
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
            db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')

            db_ins.sql_req = f"SELECT x.code FROM public.num AS x WHERE code like '{forming.docId[0:6]}%' ORDER BY x.id desc limit 1"

            forming.docId = db_ins.inserter()[0][0]
            forming.update_docId()

            logger.debug('Обновили ид документа')
            assert True, "Обновили ид документа"
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
            db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')

            db_ins.sql_req = f"SELECT x.code FROM public.num AS x WHERE code like '{forming.docId[0:6]}%' ORDER BY x.id desc limit 1"

            forming.docId = db_ins.inserter()[0][0]
            forming.update_docId()

            logger.debug('Обновили ид документа')
            assert True, "Обновили ид документа"
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
            db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')

            db_ins.sql_req = f"SELECT x.code FROM public.num AS x WHERE code like '{forming.docId[0:6]}%' ORDER BY x.id desc limit 1"

            forming.docId = db_ins.inserter()[0][0]
            forming.update_docId()

            logger.debug('Обновили ид документа')
            assert True, "Обновили ид документа"
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


@testReport.stepResults.title("СМОК-тестирование repimportedproduct_v4")
def RIP_4_test():
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

    @testReport.stepResults.step("Вставка в БД")
    def rip_4_insert_db():
        nonlocal params
        testReport.stepResults.description("Кладем сформированный документ в бд outbox в matainfo")
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


@testReport.stepResults.title("СМОК-тестирование actchargeon_v2")
def ACO_2_test():
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

    @testReport.stepResults.step("Вставка в БД")
    def aco_2_insert_db():
        nonlocal params
        testReport.stepResults.description("Кладем сформированный документ в бд outbox в matainfo")
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


if __name__ == "__main__":
    # Запуск всех тестов
    testReport.run_tests(
        test_functions=[RPP_4_mark_test,
                        RPP_4_isPacked_test,
                        RPP_4_isUnPacked_test],
        setup_teardown_func=setup_teardown
    )