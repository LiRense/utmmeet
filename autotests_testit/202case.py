import requests
import pytest
import os
import testit

name = ''
descr = ''

def get_curl_response(curl):
    params = dict()
    headers = dict()
    new_curl = curl[12:len(curl) + 1]
    new_curl = new_curl.split(" ")
    url_w_params = new_curl[0].replace("'", "")
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
    headers["accept"] = new_curl[-1].replace("'", "")
    response = requests.get(url, params=params, headers=headers)
    return response

def make_step(code):
    if code == 200:
        return True
    else:
        return False

def read_curl_list(file_path):
    with open(file_path) as file:
        return [line.strip() for line in file]

@testit.externalId('Регрессионное тестирование свагера')
@testit.displayName('Регрессионное тестирование свагера')
@pytest.mark.parametrize("curl", read_curl_list(os.path.join(os.path.dirname(__file__), "curl_list.txt")))
def test_all_curl_responses(curl):
    response = get_curl_response(curl)
    name = str(curl)
    descr = str(response.text)

    with testit.step(name, descr):
        assert make_step(response.status_code)
