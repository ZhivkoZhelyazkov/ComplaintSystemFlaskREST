import json

from flask_testing import TestCase

from config import create_app
from db import db
from models import ComplainerModel, RoleType
from tests.helpers import object_as_dict


class TestAuth(TestCase):
    def setUp(self):
        db.init_app(self.app)
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_app(self):
        self.headers = {"Content-Type": "application/json"}
        return create_app("config.TestApplicationConfiguration")

    def test_register_complainer(self):
        """
        Test if a complainer is in the database when register endpoint is hit.
        Assure that the role assign is a Complainer role.
        """
        # Arrange
        url = "/register"

        data = {
            "email": "test@test.com",
            "password": "1234567",
            "first_name": "Test",
            "last_name": "Kura",
            "phone": "123456789012345",
            "iban": "BG18RZBB91550123456789",
        }

        complainers = ComplainerModel.query.all()
        assert len(complainers) == 0

        # Act
        response = self.client.post(url, data=json.dumps(data), headers=self.headers)

        # Assert
        assert response.status_code == 201
        assert "token" in response.json

        complainers = ComplainerModel.query.all()
        assert len(complainers) == 1
        complainer = object_as_dict(complainers[0])
        complainer.pop("password")
        data.pop("password")

        assert complainer == {"id": complainer["id"], "role": RoleType.complainer, **data}
