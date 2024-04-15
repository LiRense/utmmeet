import json

data = {
  "content": [
    {
      "id": 6,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "200",
      "fullName": "Водка",
      "producedDals": 5613726.981,
      "exportedDals": 135863.74,
      "internalDals": 1825295.864,
      "soldDals": 4017.868,
      "purchaseFromThird": 1825422.5835,
      "otherExpensesDals": 941.639,
      "returnDals": 0,
      "taxVolumeLiters": 18271447.89,
      "taxAnhydrousVolumeLiters": 7315309.991,
      "exciseRate": "",
      "exciseSum": 4484285024.81,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 24,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "211",
      "fullName": "Ликероводочные изделия с содержанием этилового спирта до 25% включительно",
      "producedDals": 7774.845,
      "exportedDals": 33.6,
      "internalDals": 43.65,
      "soldDals": 50.65,
      "purchaseFromThird": 43.65,
      "otherExpensesDals": 392.05,
      "returnDals": 0,
      "taxVolumeLiters": 76539.45,
      "taxAnhydrousVolumeLiters": 13346.739,
      "exciseRate": "",
      "exciseSum": 8181551.01,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 27,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "212",
      "fullName": "Ликероводочные изделия с содержанием этилового спирта свыше 25%",
      "producedDals": 1006104.671,
      "exportedDals": 5359.62,
      "internalDals": 290888.408,
      "soldDals": 1168.2,
      "purchaseFromThird": 290953.358,
      "otherExpensesDals": 510.61,
      "returnDals": 0,
      "taxVolumeLiters": 4189032.845,
      "taxAnhydrousVolumeLiters": 1313737.369,
      "exciseRate": "",
      "exciseSum": 805321006.08,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 48,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "229",
      "fullName": "Коньяк и арманьяк, реализуемые в бутылках",
      "producedDals": 672151.281,
      "exportedDals": 4593.06,
      "internalDals": 121498.62,
      "soldDals": 338.585,
      "purchaseFromThird": 121502.42,
      "otherExpensesDals": 108.596,
      "returnDals": 0,
      "taxVolumeLiters": 4245571.8,
      "taxAnhydrousVolumeLiters": 1699005.033,
      "exciseRate": "",
      "exciseSum": 1041490085.24,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 57,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "231",
      "fullName": "Коньяки обработанные, предназначенные для отгрузки с целью розлива на других предприятиях или промпереработки",
      "producedDals": 3395.33,
      "exportedDals": 0,
      "internalDals": 3094.9,
      "soldDals": 0,
      "purchaseFromThird": 3094.9,
      "otherExpensesDals": 7980.292,
      "returnDals": 0,
      "taxVolumeLiters": -27944.7,
      "taxAnhydrousVolumeLiters": -11177.88,
      "exciseRate": "",
      "exciseSum": -6852040.44,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 66,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "232",
      "fullName": "Бренди",
      "producedDals": 97928.6,
      "exportedDals": 215.7,
      "internalDals": 17869.02,
      "soldDals": 36.4,
      "purchaseFromThird": 17869.02,
      "otherExpensesDals": 19.245,
      "returnDals": 0,
      "taxVolumeLiters": 619748.6,
      "taxAnhydrousVolumeLiters": 248371.99,
      "exciseRate": "",
      "exciseSum": 152252029.87,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 79,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "233",
      "fullName": "Коньяк с защищенным географическим указанием",
      "producedDals": 20399.44,
      "exportedDals": 2225.02,
      "internalDals": 11168.16,
      "soldDals": 246.49,
      "purchaseFromThird": 11168.16,
      "otherExpensesDals": 0.1,
      "returnDals": 0,
      "taxVolumeLiters": -41619,
      "taxAnhydrousVolumeLiters": -16647.6,
      "exciseRate": "",
      "exciseSum": -10204978.8,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 103,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "236",
      "fullName": "Ромы",
      "producedDals": 12315.01,
      "exportedDals": 0,
      "internalDals": 4.62,
      "soldDals": 4.13,
      "purchaseFromThird": 4.62,
      "otherExpensesDals": 2.08,
      "returnDals": 0,
      "taxVolumeLiters": 123057.7,
      "taxAnhydrousVolumeLiters": 47054.58,
      "exciseRate": "",
      "exciseSum": 28844457.24,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 111,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "237",
      "fullName": "Виски",
      "producedDals": 389563.65,
      "exportedDals": 818.3,
      "internalDals": 78092.37,
      "soldDals": 20.295,
      "purchaseFromThird": 78092.37,
      "otherExpensesDals": 42.435,
      "returnDals": 0,
      "taxVolumeLiters": 2325606.1,
      "taxAnhydrousVolumeLiters": 930288.635,
      "exciseRate": "",
      "exciseSum": 570266932.95,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 123,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "252",
      "fullName": "Кальвадос",
      "producedDals": 1279.58,
      "exportedDals": 98.46,
      "internalDals": 0,
      "soldDals": 14.7,
      "purchaseFromThird": 0,
      "otherExpensesDals": 0,
      "returnDals": 0,
      "taxVolumeLiters": 11811.2,
      "taxAnhydrousVolumeLiters": 4537.28,
      "exciseRate": "",
      "exciseSum": 2781352.64,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 133,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "260",
      "fullName": "Слабоалкогольная продукция",
      "producedDals": 1734454.24,
      "exportedDals": 153018.72,
      "internalDals": 233644.317,
      "soldDals": 219.747,
      "purchaseFromThird": 233646.567,
      "otherExpensesDals": 649.416,
      "returnDals": 0,
      "taxVolumeLiters": 11141446.36,
      "taxAnhydrousVolumeLiters": 822119.862,
      "exciseRate": "",
      "exciseSum": 402838732.35,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 145,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "261",
      "fullName": "Сидр",
      "producedDals": 74813.528,
      "exportedDals": 4231.632,
      "internalDals": 5025.636,
      "soldDals": 211.844,
      "purchaseFromThird": 11370.012,
      "otherExpensesDals": 369.989,
      "returnDals": 3312.944,
      "taxVolumeLiters": 541862.48,
      "taxAnhydrousVolumeLiters": 28823.984,
      "exciseRate": "",
      "exciseSum": 13546562,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 155,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "262",
      "fullName": "Пуаре (грушевый сидр)",
      "producedDals": 2627.55,
      "exportedDals": 0,
      "internalDals": 991.8,
      "soldDals": 0,
      "purchaseFromThird": 991.8,
      "otherExpensesDals": 0,
      "returnDals": 0,
      "taxVolumeLiters": 6439.5,
      "taxAnhydrousVolumeLiters": 343.575,
      "exciseRate": "",
      "exciseSum": 160987.5,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 176,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "263",
      "fullName": "Медовуха (Медовый напиток)",
      "producedDals": 14216.85,
      "exportedDals": 1296,
      "internalDals": 0,
      "soldDals": 0,
      "purchaseFromThird": 0,
      "otherExpensesDals": 22.28,
      "returnDals": 1467.133,
      "taxVolumeLiters": 129208.5,
      "taxAnhydrousVolumeLiters": 7027.268,
      "exciseRate": "",
      "exciseSum": 3230212.5,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 187,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "270",
      "fullName": "Другие спиртные напитки с содержанием этилового спирта до 25% включительно",
      "producedDals": 61.8,
      "exportedDals": 60,
      "internalDals": 0,
      "soldDals": 0,
      "purchaseFromThird": 0,
      "otherExpensesDals": 0,
      "returnDals": 0,
      "taxVolumeLiters": 18,
      "taxAnhydrousVolumeLiters": 4.5,
      "exciseRate": "",
      "exciseSum": 2758.5,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 189,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "280",
      "fullName": "Другие спиртные напитки с содержанием этилового спирта свыше 25%",
      "producedDals": 234491.435,
      "exportedDals": 555.2,
      "internalDals": 28477.02,
      "soldDals": 95.62,
      "purchaseFromThird": 28477.22,
      "otherExpensesDals": 147.475,
      "returnDals": 0,
      "taxVolumeLiters": 1769819.95,
      "taxAnhydrousVolumeLiters": 676891.651,
      "exciseRate": "",
      "exciseSum": 414934581.77,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 203,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "321",
      "fullName": "Виноматериалы виноградные",
      "producedDals": 1099232.4,
      "exportedDals": 0,
      "internalDals": 155138.92,
      "soldDals": 0,
      "purchaseFromThird": 155138.92,
      "otherExpensesDals": 1472455.37,
      "returnDals": 0,
      "taxVolumeLiters": 7889545.6,
      "taxAnhydrousVolumeLiters": 857136.533,
      "exciseRate": "",
      "exciseSum": 268244550.4,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 215,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "322",
      "fullName": "Виноматериалы фруктовые (плодовые)",
      "producedDals": 30245.7,
      "exportedDals": 0,
      "internalDals": 0,
      "soldDals": 0,
      "purchaseFromThird": 0,
      "otherExpensesDals": 293.87,
      "returnDals": 0,
      "taxVolumeLiters": 302457,
      "taxAnhydrousVolumeLiters": 31963.43,
      "exciseRate": "",
      "exciseSum": 10283538,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 234,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "323",
      "fullName": "Специальные виноматериалы виноградные",
      "producedDals": 0,
      "exportedDals": 0,
      "internalDals": 0,
      "soldDals": 0,
      "purchaseFromThird": 0,
      "otherExpensesDals": 64964.055,
      "returnDals": 0,
      "taxVolumeLiters": 0,
      "taxAnhydrousVolumeLiters": 0,
      "exciseRate": "",
      "exciseSum": 0,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 246,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "401",
      "fullName": "Вино (виноградное)",
      "producedDals": 1397135.18,
      "exportedDals": 10528.37,
      "internalDals": 179719.864,
      "soldDals": 2312.905,
      "purchaseFromThird": 181793.914,
      "otherExpensesDals": 512.793,
      "returnDals": 0,
      "taxVolumeLiters": 10250930.312,
      "taxAnhydrousVolumeLiters": 1044245.154,
      "exciseRate": "",
      "exciseSum": 348531630.61,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 255,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "402",
      "fullName": "Вино с защищенным географическим указанием или с защищенным наименованием места происхождения",
      "producedDals": 80.1,
      "exportedDals": 0,
      "internalDals": 0,
      "soldDals": 0,
      "purchaseFromThird": 0,
      "otherExpensesDals": 0,
      "returnDals": 0,
      "taxVolumeLiters": 801,
      "taxAnhydrousVolumeLiters": 96.12,
      "exciseRate": "",
      "exciseSum": 27234,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 263,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "403",
      "fullName": "Вино (виноградное столовое)",
      "producedDals": 28526.952,
      "exportedDals": 0,
      "internalDals": 1910.085,
      "soldDals": 74.75,
      "purchaseFromThird": 1910.085,
      "otherExpensesDals": 4441.73,
      "returnDals": 0,
      "taxVolumeLiters": 247067.82,
      "taxAnhydrousVolumeLiters": 24950.923,
      "exciseRate": "",
      "exciseSum": 8400305.88,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 274,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "404",
      "fullName": "Вино с защищенным географическим указанием",
      "producedDals": 220397.91,
      "exportedDals": 1737.9,
      "internalDals": 21149.418,
      "soldDals": 1775.005,
      "purchaseFromThird": 21149.418,
      "otherExpensesDals": 363.308,
      "returnDals": 0,
      "taxVolumeLiters": 1763611.737,
      "taxAnhydrousVolumeLiters": 214389.574,
      "exciseRate": "",
      "exciseSum": 59962799.06,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 292,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "405",
      "fullName": "Вино с защищенным наименованием места происхождения",
      "producedDals": 15044.563,
      "exportedDals": 0,
      "internalDals": 647.4,
      "soldDals": 174.163,
      "purchaseFromThird": 647.4,
      "otherExpensesDals": 8.775,
      "returnDals": 0,
      "taxVolumeLiters": 137497.625,
      "taxAnhydrousVolumeLiters": 16810.737,
      "exciseRate": "",
      "exciseSum": 4674919.25,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 301,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "406",
      "fullName": "Вино коллекционное виноградное",
      "producedDals": 1159.95,
      "exportedDals": 0,
      "internalDals": 155.7,
      "soldDals": 13.8,
      "purchaseFromThird": 155.7,
      "otherExpensesDals": 0.525,
      "returnDals": 0,
      "taxVolumeLiters": 8485.5,
      "taxAnhydrousVolumeLiters": 888.837,
      "exciseRate": "",
      "exciseSum": 288507,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 312,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "411",
      "fullName": "Ликерное вино",
      "producedDals": 7874.65,
      "exportedDals": 0,
      "internalDals": 226,
      "soldDals": 135.15,
      "purchaseFromThird": 226,
      "otherExpensesDals": 590.375,
      "returnDals": 0,
      "taxVolumeLiters": 74226.5,
      "taxAnhydrousVolumeLiters": 11930.908,
      "exciseRate": "",
      "exciseSum": 7313646.31,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 326,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "412",
      "fullName": "Ликерное вино с защищенным географическим указанием",
      "producedDals": 55665.801,
      "exportedDals": 1081.5,
      "internalDals": 808.2,
      "soldDals": 638.305,
      "purchaseFromThird": 808.2,
      "otherExpensesDals": 1.93,
      "returnDals": 0,
      "taxVolumeLiters": 529679.01,
      "taxAnhydrousVolumeLiters": 87426.756,
      "exciseRate": "",
      "exciseSum": 53592600.85,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 330,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "421",
      "fullName": "Фруктовое (плодовое) вино",
      "producedDals": 411629.716,
      "exportedDals": 141,
      "internalDals": 50485.022,
      "soldDals": 19.7,
      "purchaseFromThird": 50485.022,
      "otherExpensesDals": 931.535,
      "returnDals": 0,
      "taxVolumeLiters": 3105186.72,
      "taxAnhydrousVolumeLiters": 398402.704,
      "exciseRate": "",
      "exciseSum": 105576348.48,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 348,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "430",
      "fullName": "Вино специальное с защищенным географическим указанием",
      "producedDals": 25.175,
      "exportedDals": 0,
      "internalDals": 0,
      "soldDals": 7.625,
      "purchaseFromThird": 0,
      "otherExpensesDals": 0.45,
      "returnDals": 0,
      "taxVolumeLiters": 251.75,
      "taxAnhydrousVolumeLiters": 38.626,
      "exciseRate": "",
      "exciseSum": 23677.9,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 355,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "440",
      "fullName": "Вина игристые",
      "producedDals": 685800.97,
      "exportedDals": 6548.4,
      "internalDals": 227277.765,
      "soldDals": 471.24,
      "purchaseFromThird": 227306.565,
      "otherExpensesDals": 436.165,
      "returnDals": 0,
      "taxVolumeLiters": 2246682.4,
      "taxAnhydrousVolumeLiters": 251555.004,
      "exciseRate": "",
      "exciseSum": 101100708,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 376,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "441",
      "fullName": "Вина игристые с защищенным географическим указанием",
      "producedDals": 258970.845,
      "exportedDals": 1832.76,
      "internalDals": 41792.58,
      "soldDals": 883.84,
      "purchaseFromThird": 41792.58,
      "otherExpensesDals": 334.783,
      "returnDals": 0,
      "taxVolumeLiters": 1735529.25,
      "taxAnhydrousVolumeLiters": 188682.492,
      "exciseRate": "",
      "exciseSum": 78098816.25,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 388,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "442",
      "fullName": "Вина игристые с защищенным наименованием места происхождения",
      "producedDals": 1872.225,
      "exportedDals": 58.5,
      "internalDals": 81,
      "soldDals": 115.05,
      "purchaseFromThird": 81,
      "otherExpensesDals": 7.275,
      "returnDals": 0,
      "taxVolumeLiters": 16517.25,
      "taxAnhydrousVolumeLiters": 1820.044,
      "exciseRate": "",
      "exciseSum": 743276.25,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 394,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "450",
      "fullName": "Вина шампанские",
      "producedDals": 119.55,
      "exportedDals": 0,
      "internalDals": 0.075,
      "soldDals": 2.55,
      "purchaseFromThird": 0.075,
      "otherExpensesDals": 7.275,
      "returnDals": 0,
      "taxVolumeLiters": 1194,
      "taxAnhydrousVolumeLiters": 141.818,
      "exciseRate": "",
      "exciseSum": 53730,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 402,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "461",
      "fullName": "Винный напиток, произведенный без добавления этилового спирта",
      "producedDals": 280876.08,
      "exportedDals": 19680,
      "internalDals": 56023.95,
      "soldDals": 155.7,
      "purchaseFromThird": 56023.95,
      "otherExpensesDals": 2761.71,
      "returnDals": 0,
      "taxVolumeLiters": 1491481.8,
      "taxAnhydrousVolumeLiters": 134974.212,
      "exciseRate": "",
      "exciseSum": 67116681,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 423,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "462",
      "fullName": "Винный напиток, произведенный с добавлением этилового спирта",
      "producedDals": 4693.87,
      "exportedDals": 0,
      "internalDals": 2536.2,
      "soldDals": 84.15,
      "purchaseFromThird": 2536.2,
      "otherExpensesDals": 2.17,
      "returnDals": 0,
      "taxVolumeLiters": -3785.3,
      "taxAnhydrousVolumeLiters": -583.73,
      "exciseRate": "",
      "exciseSum": -357826.8,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 431,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "500",
      "fullName": "Пиво с содержанием объемной доли этилового спирта свыше 0,5% и до 8,6% включительно",
      "producedDals": 3710604.153,
      "exportedDals": 84953.565,
      "internalDals": 5609.415,
      "soldDals": 914491.341,
      "purchaseFromThird": 1850764.315,
      "otherExpensesDals": 18881.203,
      "returnDals": 95917.468,
      "taxVolumeLiters": 17692768.58,
      "taxAnhydrousVolumeLiters": 845758.748,
      "exciseRate": "",
      "exciseSum": 442319214.5,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 444,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "510",
      "fullName": "Пиво с содержанием объемной доли этилового спирта свыше 8,6%",
      "producedDals": 0,
      "exportedDals": 0,
      "internalDals": 0,
      "soldDals": 0,
      "purchaseFromThird": 0,
      "otherExpensesDals": 0,
      "returnDals": 18.6,
      "taxVolumeLiters": 0,
      "taxAnhydrousVolumeLiters": 0,
      "exciseRate": "",
      "exciseSum": 0,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    },
    {
      "id": 458,
      "inn": "",
      "kpp": "",
      "fsrarId": "",
      "orgName": "",
      "vidApId": "520",
      "fullName": "Напитки, изготавливаемые на основе пива",
      "producedDals": 884775.463,
      "exportedDals": 34519.74,
      "internalDals": 3557.52,
      "soldDals": 273696.852,
      "purchaseFromThird": 399509.791,
      "otherExpensesDals": 5495.026,
      "returnDals": 10986.777,
      "taxVolumeLiters": 4471884.12,
      "taxAnhydrousVolumeLiters": 228224.533,
      "exciseRate": "",
      "exciseSum": 111797103,
      "exciseSumOnKpp": "",
      "year": 2023,
      "month": "1"
    }
  ],
  "pageable": {
    "sort": {
      "unsorted": True,
      "sorted": False,
      "empty": True
    },
    "pageNumber": 0,
    "pageSize": 9999,
    "offset": 0,
    "paged": True,
    "unpaged": False
  },
  "totalPages": 1,
  "totalElements": 38,
  "last": True,
  "first": True,
  "numberOfElements": 38,
  "size": 9999,
  "number": 0,
  "sort": {
    "unsorted": True,
    "sorted": False,
    "empty": True
  },
  "empty": False
}

# data_json = json.json(data)
print(data)
data2 = data['content']
print(data2)
j = 0
for i in data2:
    j += i['exciseSum']

print(j)