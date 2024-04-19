import pandas as pd


with open('../search_engine/inn.txt','w') as file_w:
    ex_data = pd.read_excel('УТМ_Отчет_по_расчету_акцизов_по_месяцам_на_31_12_2023.xls')
    ex_list = ex_data['HELP'].values.tolist()
    for i in ex_list:
        if str(i).isnumeric():
            file_w.write(str(i)+'\n')