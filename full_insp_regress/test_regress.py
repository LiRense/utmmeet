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

@testReport.stepResults.title("СМОК-тестирование repproducedproduct_v4")
def RPP_4_test():
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

@testReport.stepResults.title("СМОК-тестирование waybill_v4")
def WayBill_v4_test():
    corr_xml = None
    forming = None
    params = None
    sender = None

    @testReport.stepResults.step("Генерация xml")
    def waybill_v4_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='waybill_v4')
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
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='waybillact_v4')
            corr_xml = forming.generate_WayBillActAccepted_v4()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

    @testReport.stepResults.step("Вставка в БД")
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
    def waybillactaccepted_v4_result_checker():
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
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='waybillact_v4')
            corr_xml = forming.generate_WayBillActRejected_v4()
            logger.debug('Успех генерации xml')
            assert True, "Успех генерации xml"
        except Exception as e:
            logger.error(f'Ошибка при генерации xml: {e}')
            assert False, e

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

    @testReport.stepResults.step("Генерация xml")
    def actfixbc_gen_xml():
        nonlocal corr_xml, forming
        try:
            forming = Forming_xml(doc_type='actfixbarcode')
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
        try:
            forming = Forming_xml(doc_type='actunfixbarcode')
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

    actunfixbc_gen_xml()
    actunfixbc_insert_db()
    actunfixbc_json_send()
    actunfixbc_result_checker()

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
                        ActUnFixBC_test],
        setup_teardown_func=setup_teardown
    )