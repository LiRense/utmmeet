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


def check_result(sender, topic='svs-inspector', max_attempts=1, retry_interval=1):
    """Функция для проверки результата обработки сообщения"""
    try:
        result = Result_checker().find_message_by_uri(str(sender.fsrar + "-" + sender.uuid),
                                                      topic=topic,
                                                      max_attempts=max_attempts,
                                                      retry_interval=retry_interval)
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


@testReport.stepResults.title("СМОК-тестирование repproducedproduct_v4")
def RPP_4_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def rpp_4_gen_xml():
        nonlocal forming
        forming = Forming_xml(doc_type='repproducedproduct_v4')

        @testReport.stepResults.step("Вставка productCode в nsi.product_snapshot")
        def insert_db_prCode():
            try:
                db_ins = DB_placer('nsi', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                db_ins.sql_req = (
                    'insert into "references".product_snapshot ' + "( alc_code, row_validity_begin, row_validity_end, product_type_id, full_name, short_name, original_lang_name, producer_fsrar_id, importer_fsrar_id, country_id, capacity, alc_perc_min, alc_perc_max, is_unpacked, brand, alc_code_key) values ( %s, %s, %s, %s, %s, %s, %s, %s, %s,'643', %s, %s, %s, %s, NULL, %s) on conflict (alc_code) do update set row_validity_begin = excluded.row_validity_begin, row_validity_end = excluded.row_validity_end, product_type_id = excluded.product_type_id, full_name = excluded.full_name, short_name = excluded.short_name, original_lang_name = excluded.original_lang_name, producer_fsrar_id = excluded.producer_fsrar_id, importer_fsrar_id = excluded.importer_fsrar_id, country_id = excluded.country_id, capacity = excluded.capacity, alc_perc_min = excluded.alc_perc_min, alc_perc_max = excluded.alc_perc_max, is_unpacked = excluded.is_unpacked, brand = excluded.brand, alc_code_key = excluded.alc_code_key",
                    (forming.product_code, forming.get_day(), forming.get_day(), forming.product_vcode, forming.pr_name,
                     forming.pr_name, forming.pr_name, forming.fsrar, forming.fsrar, forming.capacity,
                     forming.alc_percent, forming.alc_percent, forming.isUnPacked, int(forming.product_code)))  # Кортеж
                db_ins.inserter()
                logger.debug('Успех вставки в БД')
                assert True, "Успех вставки в БД"
            except Exception as e:
                logger.error(f'Ошибка при вставке в БД: {e}')
                assert False, e

        @testReport.stepResults.step("Генерация xml")
        def xml_generator():
            nonlocal corr_xml
            try:
                corr_xml = forming.generate_RPP_4()
                logger.debug('Успех генерации xml')
                assert True, "Успех генерации xml"
            except Exception as e:
                logger.error(f'Ошибка при генерации xml: {e}')
                assert False, e

        insert_db_prCode()
        xml_generator()

    @testReport.stepResults.step("Вставка в БД")
    def rpp_4_insert_db():
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
        check_result(sender)

    rpp_4_gen_xml()
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
        check_result(sender)

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
        check_result(sender)

    aco_2_gen_xml()
    aco_2_insert_db()
    aco_2_json_send()
    aco_2_result_checker()


@testReport.stepResults.title("СМОК-тестирование waybill_v4")
def WayBill_v4_test():
    corr_xml = None
    forming = None
    params = None
    sender = None
    form_A = None

    @testReport.stepResults.step("Получение информации из БД")
    def waybill_v4_forma():
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
    def waybill_v4_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='waybill_v4')

            forming.formA = form_A

            corr_xml = forming.generate_WayBill_4()

            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставка в БД")
    def waybill_v4_insert_db():
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
    def waybill_v4_json_send():
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
    def waybill_v4_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        check_result(sender)

    waybill_v4_forma()
    waybill_v4_gen_xml()
    waybill_v4_insert_db()
    waybill_v4_json_send()
    waybill_v4_result_checker()


@testReport.stepResults.title("СМОК-тестирование waybillact_v4 accepted")
def WayBillActAccepted_v4_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def waybillactaccepted_v4_gen_xml():
        nonlocal forming

        forming = Forming_xml(doc_type='waybillact_v4')

        @testReport.stepResults.step("Получение docId")
        def waybillactaccepted_v4_prepare():
            testReport.stepResults.description("Пытаемся получить новый docId из сикуенса")
            try:
                db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                db_ins2.sql_req = f"SELECT nextval('inbox.waybill_v4');"

                new_docId = db_ins2.inserter()
                logger.debug(new_docId)

                forming.docId = new_docId[0][0]
                logger.debug('Успех получения docId')
                assert True, "Успех получения docId"
            except Exception as e:
                logger.error(f'Ошибка при получении docId из БД: {e}')
                assert False, e

        @testReport.stepResults.step("Вставляем информацию по waybill")
        def waybillactaccepted_v4_insert_pr():

            @testReport.stepResults.step("Вставляем информацию по waybill в registry.documents")
            def insert_documents():
                try:
                    db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                    db_ins.sql_req = (
                        "INSERT INTO registry.documents (fsrarid, alccode, formb, docid, amount, vol, dt, client_number, dtype, parent, forma, price, ismarked) VALUES(%s, %s, 197, %s, %s, %s, %s, '1165', 'waybill_v4'" + '::registry."doctype", 197, 142, 0.00, true)',
                        (forming.fsrar, forming.product_code, forming.docId, forming.quantity,
                         int(forming.capacity) * int(forming.quantity), forming.get_day()))  # Кортеж
                    db_ins.inserter()
                    logger.debug('Успех вставки в БД')
                    assert True, "Успех вставки в БД"
                except Exception as e:
                    logger.error(f'Ошибка при вставке в БД: {e}')
                    assert False, e

            @testReport.stepResults.step("Вставляем информацию по waybill в registry.waybills")
            def insert_waybills():
                try:
                    db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                    db_ins.sql_req = (
                        "INSERT INTO registry.waybills (docid, sender, consignee, num, dt) VALUES(%s, %s, %s,'1','2025-10-17') ON CONFLICT (docid) DO nothing",
                        (forming.docId, forming.fsrar, forming.ip_fsrar))  # Кортеж
                    db_ins.inserter()
                    logger.debug('Успех вставки в БД')
                    assert True, "Успех вставки в БД"
                except Exception as e:
                    logger.error(f'Ошибка при вставке в БД: {e}')
                    assert False, e

            insert_documents()
            insert_waybills()

        @testReport.stepResults.step("Заполнение xml")
        def waybillactaccepted_v4_final_gen():
            nonlocal corr_xml
            try:
                corr_xml = forming.generate_WayBillActAccepted_v4()
                logger.debug('Успех генерации xml')
                assert True, "Успех генерации xml"
            except Exception as e:
                logger.error(f'Ошибка при вставке в БД: {e}')
                assert False, e

        waybillactaccepted_v4_prepare()
        waybillactaccepted_v4_insert_pr()
        waybillactaccepted_v4_final_gen()

    @testReport.stepResults.step("Вставка в БД документа")
    def waybillactaccepted_v4_insert_db():
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
    def waybillactaccepted_v4_json_send():
        nonlocal sender, forming
        testReport.stepResults.description("Отправляем json на обработку в inspector в confirmed")
        try:
            sender = Kafka_sender(forming.doc_type, params[1], forming.ip_fsrar)
            sender.send()
            logger.debug('Успех отправки json')
            assert True, "Успех отправки json"
        except Exception as e:
            logger.error(f'Ошибка при отправке json: {e}')
            assert False, e

    @testReport.stepResults.step("Поиск результата")
    def waybillactaccepted_v4_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        check_result(sender)

    waybillactaccepted_v4_gen_xml()
    waybillactaccepted_v4_insert_db()
    waybillactaccepted_v4_json_send()
    waybillactaccepted_v4_result_checker()


@testReport.stepResults.title("СМОК-тестирование waybillact_v4 rejected")
def WayBillActRejected_v4_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def waybillactrejected_v4_gen_xml():
        nonlocal forming

        forming = Forming_xml(doc_type='waybillact_v4')

        @testReport.stepResults.step("Получение docId")
        def waybillactrejected_v4_prepare():
            testReport.stepResults.description("Пытаемся получить новый docId из сикуенса")
            try:
                db_ins2 = DB_placer('transport', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                db_ins2.sql_req = f"SELECT nextval('inbox.waybill_v4');"

                new_docId = db_ins2.inserter()
                logger.debug(new_docId)

                forming.docId = new_docId[0][0]
                logger.debug('Успех получения docId')
                assert True, "Успех получения docId"
            except Exception as e:
                logger.error(f'Ошибка при получении docId из БД: {e}')
                assert False, e

        @testReport.stepResults.step("Вставляем информацию по waybill")
        def waybillactrejected_v4_insert_pr():

            @testReport.stepResults.step("Вставляем информацию по waybill в registry.documents")
            def insert_documents():
                try:
                    db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                    db_ins.sql_req = (
                        "INSERT INTO registry.documents (fsrarid, alccode, formb, docid, amount, vol, dt, client_number, dtype, parent, forma, price, ismarked) VALUES(%s, %s, 197, %s, %s, %s, %s, '1165', 'waybill_v4'" + '::registry."doctype", 197, 142, 0.00, true)',
                        (forming.fsrar, forming.product_code, forming.docId, forming.quantity,
                         int(forming.capacity) * int(forming.quantity), forming.get_day()))  # Кортеж
                    db_ins.inserter()
                    logger.debug('Успех вставки в БД')
                    assert True, "Успех вставки в БД"
                except Exception as e:
                    logger.error(f'Ошибка при вставке в БД: {e}')
                    assert False, e

            @testReport.stepResults.step("Вставляем информацию по waybill в registry.waybills")
            def insert_waybills():
                try:
                    db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                    db_ins.sql_req = (
                        "INSERT INTO registry.waybills (docid, sender, consignee, num, dt) VALUES(%s, %s, %s,'1','2025-10-17') ON CONFLICT (docid) DO nothing",
                        (forming.docId, forming.fsrar, forming.ip_fsrar))  # Кортеж
                    db_ins.inserter()
                    logger.debug('Успех вставки в БД')
                    assert True, "Успех вставки в БД"
                except Exception as e:
                    logger.error(f'Ошибка при вставке в БД: {e}')
                    assert False, e

            insert_documents()
            insert_waybills()

        @testReport.stepResults.step("Заполнение xml")
        def waybillactrejected_v4_final_gen():
            nonlocal corr_xml
            try:
                corr_xml = forming.generate_WayBillActAccepted_v4()
                logger.debug('Успех генерации xml')
                assert True, "Успех генерации xml"
            except Exception as e:
                logger.error(f'Ошибка при вставке в БД: {e}')
                assert False, e

        waybillactrejected_v4_prepare()
        waybillactrejected_v4_insert_pr()
        waybillactrejected_v4_final_gen()

    @testReport.stepResults.step("Вставка в БД")
    def waybillactrejected_v4_insert_db():
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
    def waybillactrejected_v4_json_send():
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
    def waybillactrejected_v4_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        check_result(sender)

    waybillactrejected_v4_gen_xml()
    waybillactrejected_v4_insert_db()
    waybillactrejected_v4_json_send()
    waybillactrejected_v4_result_checker()


@testReport.stepResults.title("СМОК-тестирование actwriteoff_v3")
def AWO_v3_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def awo_v3_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='actwriteoff_v3')
            corr_xml = forming.generate_AWO_v3()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставка в БД")
    def awo_v3_insert_db():
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
    def awo_v3_json_send():
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
    def awo_v3_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        check_result(sender)

    awo_v3_gen_xml()
    awo_v3_insert_db()
    awo_v3_json_send()
    awo_v3_result_checker()


@testReport.stepResults.title("СМОК-тестирование actfixbarcode")
def ActFixBC_test():
    corr_xml = None
    forming = None
    params = None
    sender = None
    formB = None

    @testReport.stepResults.step("Подготовка данных для теста")
    def actfixbc_prepare_db():
        nonlocal formB
        testReport.stepResults.description("Ведем поиск последней formB")
        logger.debug("Ведем поиск последней formB")
        try:
            db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')

            db_ins.sql_req = f"SELECT x.reg_id FROM registry.form_b AS x ORDER BY x.id desc limit 1"

            formB = db_ins.inserter()[0][0]

            logger.debug('FormB найдена')
            assert True, "FormB найдена"
        except Exception as e:
            logger.error(f'Ошибка поиска fromB: {e}')
            assert False, e

    @testReport.stepResults.step("Генерация xml")
    def actfixbc_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='actfixbarcode')
            forming.formB = formB
            corr_xml = forming.generate_ActFixBC()

            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставка в БД")
    def actfixbc_insert_db():
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
    def actfixbc_json_send():
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
    def actfixbc_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        check_result(sender)

    actfixbc_prepare_db()
    actfixbc_gen_xml()
    actfixbc_insert_db()
    actfixbc_json_send()
    actfixbc_result_checker()


@testReport.stepResults.title("СМОК-тестирование actunfixbarcode")
def ActUnFixBC_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def actunfixbc_gen_xml():
        nonlocal corr_xml, forming
        formB = None
        try:
            forming = Forming_xml(doc_type='actunfixbarcode')

            @testReport.stepResults.step("Подготовка данных для теста")
            def actunfixbc_prepare_db():
                nonlocal formB
                testReport.stepResults.description("Ведем поиск последней formB")
                logger.debug("Ведем поиск последней formB")
                try:
                    db_ins = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')

                    db_ins.sql_req = f"select x.reg_id from registry.form_b as x inner join registry.documents d on d.formb = x.id where d.fsrarid = '{forming.fsrar}' order by d.ins desc limit 1"

                    formB = db_ins.inserter()[0][0]

                    logger.debug('FormB найдена')
                    assert True, "FormB найдена"
                except Exception as e:
                    logger.error(f'Ошибка поиска fromB: {e}')
                    assert False, e

            actunfixbc_prepare_db()

            forming.formB = formB

            corr_xml = forming.generate_ActUnFixBC()

            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставка в БД")
    def actunfixbc_insert_db():
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
    def actunfixbc_json_send():
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
    def actunfixbc_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        check_result(sender)

    actunfixbc_gen_xml()
    actunfixbc_insert_db()
    actunfixbc_json_send()
    actunfixbc_result_checker()


@testReport.stepResults.title("СМОК-тестирование requestrepealawo")
def RAWO_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    forming = Forming_xml(doc_type='requestrepealawo')

    @testReport.stepResults.step("Получение docId для отмены")
    def rawo_prepare():
        nonlocal forming
        testReport.stepResults.description("Пытаемся получить docId для отмены")
        try:
            db_ins2 = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"select docid from registry.documents where fsrarid = '{forming.fsrar}' and dtype = 'actwriteoff_v3' order by id desc limit 1"

            new_docId = db_ins2.inserter()
            logger.debug(new_docId)

            forming.docId = new_docId[0][0]
            logger.debug('Успех получения docId')
            assert True, "Успех получения docId"
        except Exception as e:
            logger.error(f'Ошибка при получении docId из БД: {e}')
            assert False, e

    @testReport.stepResults.step("Генерация xml")
    def rawo_gen_xml():
        nonlocal corr_xml, forming
        try:
            corr_xml = forming.generate_RAWO()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставка в БД")
    def rawo_insert_db():
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
    def rawo_json_send():
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
    def rawo_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        check_result(sender)

    rawo_prepare()
    rawo_gen_xml()
    rawo_insert_db()
    rawo_json_send()
    rawo_result_checker()


@testReport.stepResults.title("СМОК-тестирование requestrepealaco")
def RACO_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def raco_gen_xml():
        nonlocal forming

        forming = Forming_xml(doc_type='requestrepealaco')

        @testReport.stepResults.step("Получение docId")
        def raco_prepare():
            testReport.stepResults.description("Пытаемся получить последний docId из registry.documents для ACO")
            try:
                db_get = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                db_get.sql_req = f"SELECT x.docid FROM registry.documents AS x WHERE fsrarid = '{forming.fsrar}' and dtype = 'actchargeon_v2' ORDER BY x.id desc limit 1"

                last_docId = (db_get.inserter())[0][0]

                forming.docId = int(last_docId)
                logger.debug('Успех получения docId')
                assert True, "Успех получения docId"
            except Exception as e:
                logger.error(f'Ошибка при получении docId из БД: {e}')
                assert False, e

        @testReport.stepResults.step("Заполнение xml")
        def raco_final_gen():
            nonlocal corr_xml
            try:
                corr_xml = forming.generate_RACO()
                logger.debug('Успех генерации xml')
                assert True, "Успех генерации xml"
            except Exception as e:
                logger.error(f'Ошибка при вставке в БД: {e}')
                assert False, e

        raco_prepare()
        raco_final_gen()

    @testReport.stepResults.step("Вставка в БД")
    def raco_insert_db():
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
            logger.error(f'Ошибка при вставке в БД outbox в matainfo: {e}')
            assert False, e

    @testReport.stepResults.step("Отправка json")
    def raco_json_send():
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
    def raco_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике svs-inspector")
        check_result(sender)

    raco_gen_xml()
    raco_insert_db()
    raco_json_send()
    raco_result_checker()


@testReport.stepResults.title("СМОК-тестирование asiiu")
def ASIIU_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def asiiu_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='asiiusign')
            corr_xml = forming.generate_ASIIU()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставка в БД")
    def asiiu_insert_db():
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
    def asiiu_json_send():
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
    def asiiu_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        check_result(sender, topic='crater',max_attempts=1,retry_interval=1)

    asiiu_gen_xml()
    asiiu_insert_db()
    asiiu_json_send()
    asiiu_result_checker()


@testReport.stepResults.title("СМОК-тестирование asiiutime")
def ASIIUTIME_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def asiiutime_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='asiiutimesign')
            corr_xml = forming.generate_ASIIUTIME()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставка в БД")
    def asiiutime_insert_db():
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
    def asiiutime_json_send():
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
    def asiiutime_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        check_result(sender, topic='crater',max_attempts=1,retry_interval=1)

    asiiutime_gen_xml()
    asiiutime_insert_db()
    asiiutime_json_send()
    asiiutime_result_checker()


@testReport.stepResults.title("СМОК-тестирование carriernotice")
def CarrierNotice_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    forming = Forming_xml(doc_type='CarrierNotice')

    @testReport.stepResults.step("Получение docId для отмены")
    def carriernotice_prepare():
        nonlocal forming
        testReport.stepResults.description("Пытаемся получить docId для отмены")
        try:
            db_ins2 = DB_placer('codes', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
            db_ins2.sql_req = f"select docid from registry.documents where fsrarid = '{forming.fsrar}' and dtype = 'waybill_v4' order by id desc limit 1"

            new_docId = db_ins2.inserter()
            logger.debug(new_docId)

            forming.docId = new_docId[0][0]
            logger.debug('Успех получения docId')
            assert True, "Успех получения docId"
        except Exception as e:
            logger.error(f'Ошибка при получении docId из БД: {e}')
            assert False, e

    @testReport.stepResults.step("Генерация xml")
    def carriernotice_gen_xml():
        nonlocal forming

        forming.product_vcode = '205'

        @testReport.stepResults.step("Вставляем информацию по ТС в references.org_snapshot")
        def insert_documents():
            try:
                db_ins = DB_placer('nsi', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                db_ins.sql_req = (
                    "INSERT INTO \"references\".org_snapshot ( fsrar_id,  row_validity_begin,  row_validity_end,  parent_fsrar_id,  org_trademark_id,  short_name,  full_name,  inn,  kpp,  country_code,  subject_rf_fns_code,  address,  fact_address,  email,  ogrn,  fsrar_id_key) VALUES ( %s,  %s,  NULL,  NULL,  NULL,  'АО \"ЦЕНТРИНФОРМ\"',  'АКЦИОНЕРНОЕ ОБЩЕСТВО \"ЦЕНТРИНФОРМ\"',  %s,  %s,  '643',  NULL,  'Россия, 191123, САНКТ-ПЕТЕРБУРГ Г, ШПАЛЕРНАЯ УЛ, ДОМ 26',  'Россия, 117105, Москва Г, Варшавское ш, д. 37 А, стр. 8',  NULL,  NULL,  %s) ON CONFLICT (fsrar_id) DO UPDATE SET row_validity_begin = EXCLUDED.row_validity_begin, row_validity_end = EXCLUDED.row_validity_end, parent_fsrar_id = EXCLUDED.parent_fsrar_id, org_trademark_id = EXCLUDED.org_trademark_id, short_name = EXCLUDED.short_name, full_name = EXCLUDED.full_name, inn = EXCLUDED.inn, kpp = EXCLUDED.kpp, country_code = EXCLUDED.country_code, subject_rf_fns_code = EXCLUDED.subject_rf_fns_code, address = EXCLUDED.address, fact_address = EXCLUDED.fact_address, email = EXCLUDED.email, ogrn = EXCLUDED.ogrn, fsrar_id_key = EXCLUDED.fsrar_id_key;",
                    (
                        '06' + forming.fsrar[2:],  # fsrar_id
                        forming.get_day(),  # row_validity_begin
                        forming.inn,  # inn
                        forming.kpp,  # kpp
                        int('06' + forming.fsrar[2:])  # fsrarid_key
                    )
                )

                db_ins.inserter()
                logger.debug('Успех вставки в БД')
                assert True, "Успех вставки в БД"
            except Exception as e:
                logger.error(f'Ошибка при вставке в БД: {e}')
                assert False, e

        @testReport.stepResults.step("Вставка productCode в nsi.product_snapshot")
        def insert_db_prCode():
            try:
                db_ins = DB_placer('nsi', 'dba', 'vfvfvskfnfve', '46.148.205.149', '5432')
                db_ins.sql_req = (
                    'insert into "references".product_snapshot ' + "( alc_code, row_validity_begin, row_validity_end, product_type_id, full_name, short_name, original_lang_name, producer_fsrar_id, importer_fsrar_id, country_id, capacity, alc_perc_min, alc_perc_max, is_unpacked, brand, alc_code_key) values ( %s, %s, %s, %s, %s, %s, %s, %s, %s,'643', %s, %s, %s, %s, NULL, %s) on conflict (alc_code) do update set row_validity_begin = excluded.row_validity_begin, row_validity_end = excluded.row_validity_end, product_type_id = excluded.product_type_id, full_name = excluded.full_name, short_name = excluded.short_name, original_lang_name = excluded.original_lang_name, producer_fsrar_id = excluded.producer_fsrar_id, importer_fsrar_id = excluded.importer_fsrar_id, country_id = excluded.country_id, capacity = excluded.capacity, alc_perc_min = excluded.alc_perc_min, alc_perc_max = excluded.alc_perc_max, is_unpacked = excluded.is_unpacked, brand = excluded.brand, alc_code_key = excluded.alc_code_key",
                    (forming.product_code, forming.get_day(), forming.get_day(), forming.product_vcode, forming.pr_name,
                     forming.pr_name, forming.pr_name, forming.fsrar, forming.fsrar, forming.capacity,
                     forming.alc_percent, forming.alc_percent, forming.isUnPacked, int(forming.product_code)))  # Кортеж
                db_ins.inserter()
                logger.debug('Успех вставки в БД')
                assert True, "Успех вставки в БД"
            except Exception as e:
                logger.error(f'Ошибка при вставке в БД: {e}')
                assert False, e

        def gen_xml():
            nonlocal corr_xml
            try:
                corr_xml = forming.generate_CarrierNotice()
                logger.debug('Успех генерации xml')
                assert True, "Успех генерации xml"
            except Exception as e:
                logger.error(f'Ошибка при генерации xml: {e}')
                assert False, e

        insert_documents()
        insert_db_prCode()
        gen_xml()

    @testReport.stepResults.step("Вставка в БД")
    def carriernotice_insert_db():
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
    def carriernotice_json_send():
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
    def carriernotice_result_checker():
        testReport.stepResults.description("Ищем результат обработки xml в топике crater")
        check_result(sender, topic='crater',max_attempts=1,retry_interval=1)

    carriernotice_prepare()
    carriernotice_gen_xml()
    carriernotice_insert_db()
    carriernotice_json_send()
    carriernotice_result_checker()


if __name__ == "__main__":
    # Запуск всех тестов
    testReport.run_tests(
        test_functions=[RPP_4_test,
                        RIP_4_test,
                        ACO_2_test,
                        WayBill_v4_test,
                        WayBillActAccepted_v4_test,
                        WayBillActRejected_v4_test,
                        AWO_v3_test,
                        ActFixBC_test,
                        ActUnFixBC_test,
                        RAWO_test,
                        RACO_test,
                        ASIIU_test,
                        ASIIUTIME_test,
                        CarrierNotice_test],
        setup_teardown_func=setup_teardown
    )