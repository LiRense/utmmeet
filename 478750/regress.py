import os
import shutil
import time
from datetime import datetime
from pathlib import Path
import requests
from tqdm import tqdm

import mssql_tables
from datetime import datetime
import xml.etree.ElementTree as ET
import subprocess


def marc_checker(barc_type, barcode):
    if barc_type == 'exists':
        if barcode == 'len150':
            return '200213539562110924001SDSOOVC0XFFI9VOIW6PY6XMJ2CRX2S2ZPWCZNWV1ADKDL4J8E3JF5SW1UI2D9251SYDJIRYSRF1J4FK17HEYKOUU4XKS7HNMBZV7SANJZARN8F07S6NVLTE4NC5APHYH1'
        elif barcode == 'len68':
            return '22N2A1YNWKZ8GSH084U411070010000011129GEKMQNZFW8C5ES0UV4GJNRIUFT2LCP9'
    elif barc_type == 'fictitious':
        if barcode == 'len150':
            return '200200539562110924001SDSOOVC0XFFI90000000000000000S2ZPWCZNWV1ADKDL4J8E3JF5SW1UI2D9251SYDJIRYSRF1J4FK17HEYKOUU4XKS7HNMBZV7SANJZARN8F07S6NVLTE4NC5APHYH1'
        elif barcode == 'len68':
            return '22N2A1YNWKZ8GSH084U411070010000011483BVFODHJP3EMZMFTL1XCGA27RI6BQ0I4'

def more_marc_checker(barc_type, barcode):
    if barc_type == 'exists':
        if barcode == 'len150':
            return ['200213539562110924001SDSOOVC0XFFI9VOIW6PY6XMJ2CRX2S2ZPWCZNWV1ADKDL4J8E3JF5SW1UI2D9251SYDJIRYSRF1J4FK17HEYKOUU4XKS7HNMBZV7SANJZARN8F07S6NVLTE4NC5APHYH1',
                    '200200005578581124001KWP3TLOVES8ADKMLWBE7G6QZMJU4CXYIAFZHFALRJZLS0GBOWONBUVXSX6ZCUA9TVMDEW5RNCAOQEH6X7QC1IJPGAUPD3KBFFNRYW0VNBLMG0AQT37SO5HGR9SMODPBDZ']
        elif barcode == 'len68':
            return ['22N2A1YNWKZ8GSH084U411070010000011129GEKMQNZFW8C5ES0UV4GJNRIUFT2LCP9',
                    '22N2A1YNWKZ8GSH084U411070010000010844KNRCGUGXBZ4KAEZCS9WUQ1A0EBFY6TI']
    elif barc_type == 'fictitious':
        if barcode == 'len150':
            return ['200200539562110924001SDSOOVC0XFFI90000000000000000S2ZPWCZNWV1ADKDL4J8E3JF5SW1UI2D9251SYDJIRYSRF1J4FK17HEYKOUU4XKS7HNMBZV7SANJZARN8F07S6NVLTE4NC5APHYH1',
                    '200200539542110924001SDSOOVC0XFFI11111111122222200S2ZPWCZNWV1ADKDL4J8E3JF5SW1UI2D9251SYDJIRYSRF1J4FK17HEYKOUU4XKS7HNMBZV7SANJZARN8F07S6NVLTE4NC5APHYH1']
        elif barcode == 'len68':
            return ['22N2A1YNWKZ8GSH084U411070010000011483BVFODHJP3EMZMFTL1XCGA27RI6BQ0I4',
                    '22N2A1YNWKZ8GSH084U4110700100000106743SQFJ7WBI0XSCRFWGE2V8JX9KMYCBNP']

def get_cases():
    with open('cases', 'r') as cases_file:
        cases = cases_file.readlines()

        new_cases = []

        for i in cases:
            new_i = i.replace('# ', '')
            new_i = new_i.replace('\n', '')
            list_i = new_i.split()
            new_cases.append(list_i)
        return new_cases

def get_cheque(type, sell_type):
    if sell_type == 'sell':
        if type == 'cheque':
            return 'cheque.xml'
        elif type == 'cheque_v3':
            return 'cheque_v3.xml'
        elif type == 'cheque_v4':
            return 'cheque_v4.xml'
    elif sell_type == 'return':
        if type == 'cheque':
            return 'cheque_return.xml'
        elif type == 'cheque_v3':
            return 'cheque_v3_return.xml'
        elif type == 'cheque_v4':
            return 'cheque_v4_return.xml'

def cheque_changer(name, sell_type, barc_type, barcode):
    new_name = name.replace('.xml','_')
    tree = ET.parse(name)
    root = tree.getroot()

    now = datetime.now()
    root.set('datetime', now.strftime('%d%m%y%H%M'))
    bottle = root.find('Bottle')
    bottle.set('barcode', f'{marc_checker(barc_type, barcode)}')

    directory_path = Path('buffer/')
    directory_path.mkdir(parents=True, exist_ok=True)

    tree.write(f'buffer/{new_name+barc_type+"_"+barcode}.xml', encoding='UTF-8', xml_declaration=True)

def cheque_v3_changer(name,sell_type, barc_type, barcode):
    new_name = name.replace('.xml','_')

    directory_path = Path('buffer/')
    directory_path.mkdir(parents=True, exist_ok=True)

    now = datetime.now()

    namespaces = {
        'ns': 'http://fsrar.ru/WEGAIS/WB_DOC_SINGLE_01',
        'ck': 'http://fsrar.ru/WEGAIS/ChequeV3'
    }

    tree = ET.parse(name)
    root = tree.getroot()

    date_element = root.find('.//ck:Date', namespaces)
    if date_element is not None:
        date_element.text = now.strftime('%Y-%m-%dT%H:%M:%S')

    barcode_element = root.find('.//ck:Barcode', namespaces)
    if barcode_element is not None:
        barcode_element.text = f'{marc_checker(barc_type, barcode)}'  # New barcode value

    tree.write(f'buffer/{new_name+barc_type+"_"+barcode}.xml', encoding='UTF-8', xml_declaration=True)

def cheque_v4_return_changer(name,sell_type, barc_type, barcode):
    new_name = name.replace('.xml','_')

    directory_path = Path('buffer/')
    directory_path.mkdir(parents=True, exist_ok=True)

    now = datetime.now()

    namespaces = {
        'ns':'http://fsrar.ru/WEGAIS/WB_DOC_SINGLE_01',
        'ck':'http://fsrar.ru/WEGAIS/ChequeV4'
    }

    tree = ET.parse(name)
    root = tree.getroot()

    date_element = root.find('.//ck:Date', namespaces)
    if date_element is not None:
        date_element.text = now.strftime('%Y-%m-%dT%H:%M:%S')

    barcode_element = root.find('.//ck:Barcode', namespaces)
    if barcode_element is not None:
        barcode_element.text = f'{marc_checker(barc_type, barcode)}'  # New barcode value

    tree.write(f'buffer/{new_name+barc_type+"_"+barcode}.xml', encoding='UTF-8', xml_declaration=True)

def cheque_v4_changer(name,sell_type, barc_type, barcode):
    new_name = name.replace('.xml', '_')

    directory_path = Path('buffer/')
    directory_path.mkdir(parents=True, exist_ok=True)

    now = datetime.now()

    namespaces = {
        'ns':'http://fsrar.ru/WEGAIS/WB_DOC_SINGLE_01',
        'ck':'http://fsrar.ru/WEGAIS/ChequeV4'
    }

    tree = ET.parse(name)
    root = tree.getroot()

    date_element = root.find('.//ck:Date', namespaces)
    if date_element is not None:
        date_element.text = now.strftime('%Y-%m-%dT%H:%M:%S')

    barcode_elements = root.findall('.//ck:Barcode', namespaces)
    barcodes_list = more_marc_checker(barc_type, barcode)
    # print(barcodes_list)
    for id, barcode_element in enumerate(barcode_elements):
        barcode_element.text = barcodes_list[id]

    tree.write(f'buffer/{new_name + barc_type + "_" + barcode}.xml', encoding='UTF-8')

def create_xmls():
    mssql_tables.add_tables()
    directory_path = Path('buffer/')
    if directory_path.exists() and directory_path.is_dir():
        shutil.rmtree(directory_path)
    directory_path.mkdir(parents=True, exist_ok=True)

    cases = get_cases()
    for i in cases:
        name_case = get_cheque(i[0], i[1])
        if 'v3' in name_case:
            cheque_v3_changer(name_case, i[1], i[2], i[3])
        elif '4_return' in name_case:
            cheque_v4_return_changer(name_case, i[1], i[2], i[3])
        elif 'v4' in name_case:
            cheque_v4_changer(name_case, i[1], i[2], i[3])
        elif 'cheque' in name_case:
            cheque_changer(name_case, i[1],i[2], i[3])

def curl_cheq():
    current_working_directory = Path.cwd()
    directory_path = Path(str(current_working_directory) + '/buffer/')

    all_files = [f for f in directory_path.iterdir() if f.is_file()]

    files_v4_sell = [f for f in all_files if 'v4_e' in f.name or 'v4_f' in f.name]
    files_v4_return = [f for f in all_files if 'v4_r' in f.name]
    files_v3_sell = [f for f in all_files if 'v3_e' in f.name or 'v3_f' in f.name]
    files_v3_return = [f for f in all_files if 'v3_r' in f.name]
    files_sell = [f for f in all_files if 'e_e' in f.name or 'e_f' in f.name]
    files_return = [f for f in all_files if 'e_r' in f.name]

    files = files_v4_sell + files_v4_return + files_v3_sell + files_v3_return + files_sell + files_return

    counter = 0

    with open('results.txt', 'w') as result_file:
        for file in tqdm(files, desc="Processing files"):
            if counter in (7, 15,):
                mssql_tables.add_tables()
            if 'v3' in str(file):
                curl_command = f'curl -s -F "xml_file=@{file}" http://localhost:8080/xml?type=ChequeV3'
            elif 'v4' in str(file):
                curl_command = f'curl -s -F "xml_file=@{file}" http://localhost:8080/xml?type=ChequeV4'
            elif 'cheque' in str(file):
                curl_command = f'curl -s -F "xml_file=@{file}" http://localhost:8080/xml'
            else:
                continue
            if counter != 0:
                counter += 1

            start_time = datetime.now()
            time.sleep(5)

            result = subprocess.run(curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout = result.stdout.decode()
            stderr = result.stderr.decode()

            end_time = datetime.now()

            start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
            end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')

            docker_logs_command = f'docker logs --since {start_time_str} --until {end_time_str} barkv'
            docker_logs_result = subprocess.run(docker_logs_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            docker_logs = docker_logs_result.stdout.decode()

            result_file.write(f'# {file.name}\n')
            result_file.write(f'*result: {stdout.replace("<url>","")}*\n')
            if stderr and 'error' not in stderr.lower():
                result_file.write(f'error: {stderr}\n')
            result_file.write('{{collapse(Логи)\n')
            result_file.write('<pre>\n')
            result_file.write(docker_logs)
            result_file.write('</pre>\n')
            result_file.write('}}\n')

            if "ERROR" in docker_logs:
                result_file.write('{{collapse(Ошибка)\n<pre>\n')
                log_lines = docker_logs.splitlines()
                for i, line in enumerate(log_lines):
                    if "ERROR" in line:
                        result_file.write(line + '\n')
                        if i + 1 < len(log_lines):
                            result_file.write(log_lines[i + 1] + '\n')
                result_file.write('</pre>\n}}\n')

    print('All files have been processed.')


create_xmls()
curl_cheq()

