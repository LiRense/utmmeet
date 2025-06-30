def inser_DB_data(doc_name):
    insert
    pass

def send_to_kafka(message):
    pass

docs = {"destruct": "reportdestructionamfsm_checkexp_create_from_helper",
        "iefsm": "InvoiceExportFSM_check_identifiers_from_helper",
        "ilam": "InvoiceIssueAM_check_ranges_from_helper",
        "ipi": "InvoicePlannedImport_check_exp_from_helper",
        "ipiv1": "InvoicePlannedImport_v1_check_exp",
        "ireturnfsm": "ttnissuereturnfsmcheckmarks_from_helper",
        "resipi": "Res_Ipi",
        "resipiv1": "Res_Ipi_v1",
        "resiefsm": "Res_IEFSM",
        "resdestuct": "Res_Destruct"
        }

for i in docs:
    DB_data = insert_DB_data(i)



