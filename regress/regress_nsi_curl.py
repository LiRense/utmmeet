import requests
a = ''
def get_curl_response(num_curl,curl):
    global a
    params = dict()
    headers = dict()
    new_curl = curl[12:len(curl)+1]
    new_curl = new_curl.split(" ")
    url_w_params = new_curl[0].replace("'","")
    url_w_params = url_w_params.replace("?", " ")
    url_w_params = url_w_params.replace("&", " ")
    url_data = url_w_params.split()
    url_data_len = len(url_data)
    url = url_data[0]
    url_data.remove(url)
    for i in url_data:
        key = (i.split("="))[0]
        value = (i.split("="))[1]
        params[key] = value
    headers["accept"] = new_curl[-1].replace("'","")
    response = requests.get(url, params=params,
                            headers=headers)
    file_w.write("\n"+str(num_curl+1)+' {{'+f"collapse(Запрос)\n<pre>\n{curl}\n</pre>\n"+"}}"+"\n"+"{{"+f"collapse(Ответ {str(response)})\n<pre>\n{response.text}\n</pre>\n"+"}}")


clear_curl_list = []
with open("curl_list.txt", 'r') as curl_list_txt:
    curl_list = curl_list_txt.readlines()
for i in curl_list:
    clear_curl_list.append((i.replace("\n","")))

# file_w = open('curl_log_json.txt', "w")
# file_w.seek(0)
# for num_curl in range(len(clear_curl_list)):
#     get_curl_response(num_curl,clear_curl_list[num_curl])
# file_w.close()

