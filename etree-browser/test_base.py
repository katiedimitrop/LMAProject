from templates import app
import unittest


class BaseTestCase(unittest.TestCase):
    """A base test case for flask-tracking."""

    def create_app(self):
        #setup test configurations
        app.configurations.from_object('config.TestConfig')
        return app

    #def setUp(self):
       # db.create_all()

   # def tearDown(self):
       # db.session.remove()
       # db.drop_all()