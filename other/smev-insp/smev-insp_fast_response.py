import json
import uuid

with (open('requests','r') as requests):
    requests_list_raw = requests.readlines()
    requests_list_js = [json.loads(x) for x in requests_list_raw]
    # requests_list = list(map(lambda x: x.replace('\n',''), [i for i in requests_list_raw]))
    # print(requests_list_js)
    with open('responses.txt', 'w') as responses:
        for i in requests_list_js:
            form = '{"id":"c0aaec4c-19d4-4301-bbb8-8953fa99b0ef","serviceId":"smev-inspector","requestId":"5e135d2d-2b8a-40c4-bbdc-3110be647f4e","requestType":"OP","xsltId":16,"clientInternalNumber":"Л-44","additionalDetails":"186833-38462-194b06e9a19","responseId":"c86c44f5-de3b-11ef-b652-0050568981ba","messageId":"bf227db0-de3b-11ef-a23c-eadaed674e7b","requestContent":{"svUl":{"nameUl":"Федеральная служба по регулированию алкогольного рынка (Росалкогольрегулирование)","ogrn":"1097746136124","innUl":"7710747640"},"requestUl":{"kppOp":"572032001","ogrn":null,"innUl":"2310031475"},"requestId":"6901a896-cbc4-4b51-bbdc-0e3a70d341e3","typeInf":"ЗапрПостУч"},"requestTimestamp":"2025-01-29T15:22:46.281+0300","updateTimestamp":"2025-01-29T15:25:31.583+0300","responseContent":{"requestId":"6901a896-cbc4-4b51-bbdc-0e3a70d341e3","svOrg":{"addressMNOP":"302507,РОССИЯ,ОРЛОВСКАЯ ОБЛ,ОРЛОВСКИЙ Р-Н,,ХАРДИКОВО Д,СОВХОЗНАЯ УЛ,ЗД. 10А,,","addressNOOP":",302030,,,ОРЕЛ Г,,МИРА ПЛ,7А,,","dataUchOP":"29.08.2022","innUL":"2310031475","kppOP":"572032001","codeNOOP":"5700","nameOP":"СКЛАД ХРАНЕНИЯ АЛКОГОЛЬНОЙ ПРОДУКЦИИ","dataSnUchOP":"","svRegIO":{"kodStrIO":"","nameROIV":"","regNomIO":""}},"stOrg":""},"kafkaPartition":1,"kafkaOffset":271721,"route":"OUT","state":"OUTGOING","archivedStatus":true,"queuedStatus":true}'
            new_gen = json.loads(form)
            new_gen["id"] = str(uuid.uuid4())
            new_gen["additionalDetails"] = i["additionalDetails"]
            new_gen["requestContent"] = i["requestContent"]
            new_gen["requestId"] = i["requestId"]
            new_gen["clientInternalNumber"] = i["clientInternalNumber"]
            new_gen["responseId"] = str(uuid.uuid4())
            new_gen["messageId"] = str(uuid.uuid4())
            new_gen["responseContent"]["requestId"] = i["requestContent"]["requestId"]
            new_gen["responseContent"]["svOrg"]["innUL"] = i["requestContent"]["requestUl"]["innUl"]
            new_gen["responseContent"]["svOrg"]["kppOP"] = i["requestContent"]["requestUl"]["kppOp"]
            last_gen = str(new_gen).replace('True', 'true')
            last_gen = last_gen.replace('False', 'false')
            last_gen = last_gen.replace("None", 'null')
            last_gen = last_gen.replace("'", '"')
            responses.write(last_gen+'\n')