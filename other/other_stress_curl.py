import requests
from multiprocessing.pool import ThreadPool as Pool
import concurrent.futures

headers = {
    'accept': 'application/json',
}

def sto_curl(n):
    response = requests.get("http://localhost:8080/api/rsa/orginfo",headers=headers)

pool_size = 1000  # your "parallelness"

pool = Pool(pool_size)

for i in range(1000000):
    pool.apply_async(sto_curl, (i,))

pool.close()
pool.join()