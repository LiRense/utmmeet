import pandas as pd
import zipfile
import os
import csv

def parser(file_with_message_id, zip_folder):
    resultdf = pd.DataFrame()
    counter = 1
    found = False
    with open('search_results.txt', 'w') as results_file:
        with open(f'{file_with_message_id}', 'r') as search_file:
            for search_string in search_file:
                search_string = search_string.strip()  # Удаляем лишние символы, такие как перенос строки
                for root, dirs, files in os.walk(zip_folder):
                    for file in files:
                        if not file.endswith('.zip'):
                            continue

                        zip_path = os.path.join(root, file)
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            for zip_info in zip_ref.infolist():
                                if not zip_info.filename.endswith('.csv') or not zip_info.filename.startswith('messages_data'):
                                    continue

                                with zip_ref.open(zip_info) as csv_file:
                                    df = pd.read_csv(csv_file, sep=';', quotechar='"', header=0)
                                    result = df[df['message_id'].isin([search_string])]

                                    if not result.empty:
                                        result_string = df[df['message_id'] == search_string]
                                        print(result_string.values)
                                        resultdf = pd.concat([resultdf, result_string])
                                        counter += 1
                                        found = True
                                        result_str = f'|- found {search_string} in [{zip_info.filename}]\n'
                                        print(str(result_str))
                                        results_file.write(result_str)

                    if found:
                        break  # Если найдено, прерываем цикл

                if not found:
                    result_str = f'{search_string} not found\n'
                    print(result_str)
                    results_file.write(result_str)

                found = False  # Сброс флага для следующей итерации

    resultdf.to_csv(f'{search_string}.csv', index=False, sep=';')

if __name__ == '__main__':
    mesage_ids = ('message_id.txt')
    folder_to_search = 'Smev_archive_2023'
    parser(mesage_ids, folder_to_search)

'''
kubectl -n smev-adapter get po -o wide -l app.kubernetes.io/instance=executor

curl -v -F file=@messages_data_2024-01-12_00.00.00.000.csv 192.168.195.190:8090/api/v1/restore
'''s