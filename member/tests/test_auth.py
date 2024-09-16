import pytest
from faker import Faker
from ninja.testing import TestClient
from django.contrib.auth import get_user_model

from member.api import router

User = get_user_model()
fake = Faker()


class TestAuth:
    def setup_class(self):
        self.username = fake.user_name()
        self.password = fake.password()
        self.email = fake.email()

    @pytest.mark.django_db
    def test_logout(self):
        user = User.objects.create_user(username=self.username, password=self.password)

        client = TestClient(router)

        response = client.post("/logout/", user=user)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_sign_up(self):
        client = TestClient(router)

        response = client.post(
            "/sign-up/",
            json={
                "username": self.username,
                "password": self.password,
                "email": self.email,
            },
        )
        assert response.status_code == 201

        user = User.objects.get(username=self.username)
        assert user.email == self.email
