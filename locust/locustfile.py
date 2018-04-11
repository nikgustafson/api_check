from locust import HttpLocust, TaskSet, task
import configparser
import json
import requests

config = configparser.ConfigParser()
config.read('config.ini')
auth = config['AUTH']

environments = {'api':['api', 'qaapi'], 'auth':['auth', 'qaauth']}


class UserBehavior(TaskSet):

    def on_start(self):
        payload = {
        'client_id':auth['buyerClientID'],
        'grant_type': 'password',
        'username' : auth['buyerUsername'],
        'password':auth['buyerPassword'],
        'Scope': "Shopper"
        }
        headers = {'Content-Type':'application/json'}
        r = requests.post('https://auth.ordercloud.io/oauth/token', data = payload, headers = headers)

        print(r.url)
        print(r.headers)
        """ on_start is called when a Locust start before any task is scheduled """
        self.token = r.json()['access_token']
        self.headers = headers = {'Content-Type':'application/json', 'Authorization':'Bearer '+ self.token}
        print(self.token)
        self.login()

    def login(self):
       
        self.client.get('/me', headers = self.headers)

    @task(2)
    def getProducts(self):
        
        self.client.get('/products', headers = self.headers)

    @task(1)
    def getMe(self):

        self.client.get('/me', headers = self.headers)

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    host = "https://qaapi.ordercloud.io/v1"
    min_wait = 5000
    max_wait = 9000
