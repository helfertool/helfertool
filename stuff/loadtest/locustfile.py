from locust import HttpLocust, TaskSet, task

USER="loadtest"
PASSWORD="loadtest"

EVENT="loadtest"
SHIFT_ID="11"

class UserBehavior(TaskSet):
    def on_start(self):
        self.login()

    def login(self):
        response = self.client.get("/login/")
        csrftoken = response.cookies['csrftoken']

        r = self.client.post("/login/",
                         {"username": USER,
                          "password": PASSWORD,
                          "csrfmiddlewaretoken": csrftoken})

    @task(1)
    def index(self):
        self.client.get("/")

    @task(1)
    def form(self):
        self.client.get("/%s/" % EVENT)

    @task(1)
    def register(self):
        response = self.client.get("/loadtest/")
        csrftoken = response.cookies['csrftoken']

        r = self.client.post("/loadtest/",
                         {"shift_%s" % SHIFT_ID : "on",
                          "prename": "a",
                          "surname": "b",
                          "email": "a@c.de",
                          "phone": "0",
                          "shirt": "S",
                          "infection_instruction": "No",
                          "comment": "lalalal",
                          "csrfmiddlewaretoken": csrftoken})

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait=5000
    max_wait=9000
