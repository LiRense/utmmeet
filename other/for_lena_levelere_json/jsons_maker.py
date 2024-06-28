from DataBase.connection import *

connection_db = Connecting()
tunnel = connection_db.tooneling(jump_host='10.0.50.208', jump_port=20010, remote_host='10.10.5.189', remote_port=5432, username='martikhin',
                                 ssh_pkey='/home/ivan/.ssh/id_rsa')

info_db = connection_db.pg_sql(tunnel,'leveler','leveler','QAZwsx123',"select * from request r where service_id ='sed-integrator' and request_timestamp > '2024-05-18'")
print(info_db)

example_json = {
  "id": "fbaa2bc4-65ea-419b-8d4f-04afd8b96aeb",
  "serviceId": "sed-integrator",
  "requestId": "759ec26b-d792-4e8c-ab95-6bdfd65b6e9c",
  "requestType": "EPGU",
  "xsltId": 5,
  "responseId": "0e664cc2-f811-4734-8d7b-b698c92c06c6",
  "messageId": "276536cf-2fc2-11ef-a9a6-ce0e08294c74",
  "requestContent": {
    "epgu": {
      "orderID": "4280516629",
      "department": "100000012571",
      "serviceCode": "60013396",
      "targetCode": "-60013396",
      "statementDate": "2024-06-21"
    },
    "applicant": {
      "ul": {
        "fullName": "ЗАКРЫТОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО \"ИГРИСТЫЕ ВИНА\"",
        "shortName": "ЗАО \"ИГРИСТЫЕ ВИНА\"",
        "lastName": "ДУДКО",
        "firstName": "ЮРИЙ",
        "patronymic": "ВЛАДИМИРОВИЧ",
        "ogrn": "1027802482608",
        "inn": "7830001010",
        "kpp": "780401001"
      },
      "address": "195027, Г.САНКТ-ПЕТЕРБУРГ, НАБ СВЕРДЛОВСКАЯ, Д. 34, ЛИТЕРА А",
      "email": "info@spbvino.ru",
      "phone": "+7(812)3350404"
    },
    "oto": {
      "kindOfActivity": "Производство, хранение и поставки произведённой алкогольной продукции: игристые вина",
      "products": [
        {
          "productName": "игристые вина"
        }
      ],
      "kpp": "780401001",
      "address": "Россия, Санкт-Петербург Город, Свердловская Набережная, 34",
      "license": "\n    78ПВН0013304\n"
    },
    "appliedDocuments": [
      {
        "name": "о схеме оснащения.pdf",
        "businessName": "Схема оснащения основного технологического оборудования АСИиУ",
        "type": "application/pdf",
        "mnemonic": "c7.FileUploadComponent.oto.4280516629"
      },
      {
        "name": "о расчёте мощности.pdf",
        "businessName": "Расчёт мощности основного технологического оборудования",
        "type": "application/pdf",
        "mnemonic": "c10.FileUploadComponent.moshchnost.4280516629"
      },
      {
        "name": "перечень ОТО 21.06.2024г.pdf",
        "businessName": "Перечень приобретённого основного технологического оборудования",
        "type": "application/pdf",
        "mnemonic": "c40.FileUploadComponent.perechen.4280516629"
      }
    ]
  },
  "requestTimestamp": "2024-06-21T14:35:28.280+0300",
  "updateTimestamp": "2024-06-21T14:35:44.032+0300",
  "kafkaPartition": 0,
  "kafkaOffset": 0,
  "route": "IN",
  "attachmentPath": "/mnt/nfs2/leveler/storage/2024-06-21/276536cf-2fc2-11ef-a9a6-ce0e08294c74/Application.zip",
  "state": "OUTGOING",
  "archivedStatus": True,
  "queuedStatus": True
}


for i in info_db:
        example_json["id"] = i[0]

print(example_json)