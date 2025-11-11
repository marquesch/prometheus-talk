from locust import HttpUser, task, between
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseUser(HttpUser):
    weight = 0

    def on_start(self):
        self.login()
    
    def on_stop(self):
        self.logout()
    
    def login(self):
        """Login and store the JWT token"""
        response = self.client.post("/login", json={
            "username": self.username,
            "password": self.password
        })
        
        if response.status_code == 200:
            self.token = response.json()["token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            logger.info(f"{self.username} logged in successfully")
        else:
            logger.error(f"Login failed for {self.username}")
            self.token = None
            self.headers = {}
    
    def logout(self):
        if hasattr(self, 'token') and self.token:
            self.client.post("/logout", headers=self.headers)
            logger.info(f"{self.username} logged out")


class CasualReader(BaseUser):
    wait_time = between(3, 8)
    weight = 5
    
    username = "reader_user"
    password = "reader_pass"
    
    @task(10)
    def read_posts(self):
        self.client.get("/posts", headers=self.headers, name="/posts [Read]")
    
    @task(8)
    def read_comments(self):
        post_id = random.randint(1, 20)
        self.client.get(
            f"/posts/{post_id}/comments",
            headers=self.headers,
            name="/posts/[id]/comments [Read]"
        )
    
    @task(1)
    def create_comment(self):
        post_id = random.randint(1, 20)
        self.client.post(
            f"/posts/{post_id}/comments",
            headers=self.headers,
            json={"body": f"Great post! - {random.randint(1000, 9999)}"},
            name="/posts/[id]/comments [Create]"
        )
    
    @task(2)
    def check_profile(self):
        """Check own profile"""
        self.client.get("/me", headers=self.headers)


class ActiveContributor(BaseUser):
    wait_time = between(2, 5)
    weight = 3
    
    username = "contributor_user"
    password = "contributor_pass"
    
    @task(5)
    def create_post(self):
        self.client.post(
            "/posts",
            headers=self.headers,
            json={
                "title": f"Post Title {random.randint(1000, 9999)}",
                "body": f"This is post content {random.randint(1000, 9999)}"
            },
            name="/posts [Create]"
        )
    
    @task(8)
    def create_comment(self):
        post_id = random.randint(1, 20)
        self.client.post(
            f"/posts/{post_id}/comments",
            headers=self.headers,
            json={"body": f"Interesting perspective! - {random.randint(1000, 9999)}"},
            name="/posts/[id]/comments [Create]"
        )
    
    @task(6)
    def read_posts(self):
        self.client.get("/posts", headers=self.headers, name="/posts [Read]")
    
    @task(4)
    def read_comments(self):
        post_id = random.randint(1, 20)
        self.client.get(
            f"/posts/{post_id}/comments",
            headers=self.headers,
            name="/posts/[id]/comments [Read]"
        )
    
    @task(1)
    def check_profile(self):
        self.client.get("/me", headers=self.headers)


class PowerUser(BaseUser):
    wait_time = between(1, 3)
    weight = 2
    
    username = "power_user"
    password = "power_pass"
    
    @task(10)
    def create_post(self):
        self.client.post(
            "/posts",
            headers=self.headers,
            json={
                "title": f"Power Post {random.randint(1000, 9999)}",
                "body": f"Detailed content here {random.randint(1000, 9999)}"
            },
            name="/posts [Create]"
        )
    
    @task(15)
    def create_comment(self):
        post_id = random.randint(1, 20)
        self.client.post(
            f"/posts/{post_id}/comments",
            headers=self.headers,
            json={"body": f"Detailed comment {random.randint(1000, 9999)}"},
            name="/posts/[id]/comments [Create]"
        )
    
    @task(12)
    def read_posts(self):
        self.client.get("/posts", headers=self.headers, name="/posts [Read]")
    
    @task(10)
    def read_comments(self):
        post_id = random.randint(1, 20)
        self.client.get(
            f"/posts/{post_id}/comments",
            headers=self.headers,
            name="/posts/[id]/comments [Read]"
        )
    
    @task(2)
    def check_profile(self):
        self.client.get("/me", headers=self.headers)
