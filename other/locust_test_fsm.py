import random
from locust import HttpUser, TaskSet, task, between


class UserBehavior(TaskSet):
    @task
    def claimsInWork(self):
        bearer = 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJmaXJzdE5hbWUiOiJBdXRvIiwibGFzdE5hbWUiOiJBdXRvIiwicmVnaW9uQ29kZSI6Ijc3Iiwicm9sZSI6ImRldmVsb3BlciIsInBlcm1pc3Npb25zIjoiUmV0YWlsIiwicm9sZWlkIjoiMCIsImxvY2FsaXR5IjoiQXV0byIsInJlZ2lvbiI6IkF1dG8iLCJ1c2VyaWQiOiIxMjMifQ.wFuh-G7oIHflwiL8rzUWltZWkgYF96hw5EoWtV2ycHUKn-r8soNObozjgq5cc9bYTY_akyoBpk19e9Ai2HdsIA'
        headers = {
            "Authorization":f'{bearer}'
        }
        self.client.get("/api-lc-fsm/claimissuefsm/claimsInWork", headers=headers, verify=False)

    @task
    def claimsComplete(self):
        bearer = 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJmaXJzdE5hbWUiOiJBdXRvIiwibGFzdE5hbWUiOiJBdXRvIiwicmVnaW9uQ29kZSI6Ijc3Iiwicm9sZSI6ImRldmVsb3BlciIsInBlcm1pc3Npb25zIjoiUmV0YWlsIiwicm9sZWlkIjoiMCIsImxvY2FsaXR5IjoiQXV0byIsInJlZ2lvbiI6IkF1dG8iLCJ1c2VyaWQiOiIxMjMifQ.wFuh-G7oIHflwiL8rzUWltZWkgYF96hw5EoWtV2ycHUKn-r8soNObozjgq5cc9bYTY_akyoBpk19e9Ai2HdsIA'
        headers = {
            "Authorization":f'{bearer}'
        }
        self.client.get("/api-lc-fsm/claimissuefsm/claimsComplete", headers=headers, verify=False)

    @task
    def pos_ttn(self):
        bearer = 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJmaXJzdE5hbWUiOiJBdXRvIiwibGFzdE5hbWUiOiJBdXRvIiwicmVnaW9uQ29kZSI6Ijc3Iiwicm9sZSI6ImRldmVsb3BlciIsInBlcm1pc3Npb25zIjoiUmV0YWlsIiwicm9sZWlkIjoiMCIsImxvY2FsaXR5IjoiQXV0byIsInJlZ2lvbiI6IkF1dG8iLCJ1c2VyaWQiOiIxMjMifQ.wFuh-G7oIHflwiL8rzUWltZWkgYF96hw5EoWtV2ycHUKn-r8soNObozjgq5cc9bYTY_akyoBpk19e9Ai2HdsIA'
        headers = {
            "Authorization":f'{bearer}'
        }
        self.client.get("/api-lc-fsm/claimissuefsm/ttn/23352/pos?ttnType=TTNShipmentFSM&page=0&size=99999", headers=headers, verify=False)

    @task
    def complite_ttn(self):
        bearer = 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJmaXJzdE5hbWUiOiJBdXRvIiwibGFzdE5hbWUiOiJBdXRvIiwicmVnaW9uQ29kZSI6Ijc3Iiwicm9sZSI6ImRldmVsb3BlciIsInBlcm1pc3Npb25zIjoiUmV0YWlsIiwicm9sZWlkIjoiMCIsImxvY2FsaXR5IjoiQXV0byIsInJlZ2lvbiI6IkF1dG8iLCJ1c2VyaWQiOiIxMjMifQ.wFuh-G7oIHflwiL8rzUWltZWkgYF96hw5EoWtV2ycHUKn-r8soNObozjgq5cc9bYTY_akyoBpk19e9Ai2HdsIA'
        headers = {
            "Authorization":f'{bearer}'
        }
        self.client.get("/api-lc-fsm/claimissuefsm/complete/1005035/ttn?ttnType=TTNShipmentFSM", headers=headers, verify=False)

    @task
    def claimChecksComplete(self):
        bearer = 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJmaXJzdE5hbWUiOiJBdXRvIiwibGFzdE5hbWUiOiJBdXRvIiwicmVnaW9uQ29kZSI6Ijc3Iiwicm9sZSI6ImRldmVsb3BlciIsInBlcm1pc3Npb25zIjoiUmV0YWlsIiwicm9sZWlkIjoiMCIsImxvY2FsaXR5IjoiQXV0byIsInJlZ2lvbiI6IkF1dG8iLCJ1c2VyaWQiOiIxMjMifQ.wFuh-G7oIHflwiL8rzUWltZWkgYF96hw5EoWtV2ycHUKn-r8soNObozjgq5cc9bYTY_akyoBpk19e9Ai2HdsIA'
        headers = {
            "Authorization":f'{bearer}'
        }
        self.client.get("/api-lc-fsm/claimissuefsm/claimChecksComplete/1005050", headers=headers, verify=False)

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 300)
    host = "https://lk-test.egais.ru"  # Укажите ваш домен здесь