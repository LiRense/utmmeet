import requests

ttnissue = [ 'TTNIFSM-0000022579', 'TTNIFSM-0000022580' ]


def ttn_update(ttn_issue):
    for ttn in ttn_issue:
        print('http://lk-test.test-kuber-nd.fsrar.ru/api-lc-fsm/ttnissuefsmupdatefile?regid=' + ttn + '\n')
        r = requests.post(
            'http://lk-test.test-kuber-nd.fsrar.ru/api-lc-fsm/ttnissuefsmupdatefile?regid=' + ttn,
            headers=dict(accept='application/pdf'),
            proxies=dict(http='socks5h://127.0.0.1:1080',
                         https='socks5h://127.0.0.1:1080')
        )
        print('\n', r.status_code, r.reason, '\n')

ttn_update(ttnissue)