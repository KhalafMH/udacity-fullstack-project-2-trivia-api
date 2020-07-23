import unittest

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('postgres:password@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            self.db.engine.execute("""
                INSERT INTO categories (type) VALUES ('Science'), ('Sport')
            """)

    def tearDown(self):
        """Executed after reach test"""
        with self.app.app_context():
            self.db.engine.execute("""
                DELETE FROM categories
            """)
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories_returns_correct_result(self):
        client = self.client()
        result = client.get("/api/categories")
        self.assertEqual(200, result.status_code)
        self.assertIn('Sport', result.json['categories'])
        self.assertIn('Science', result.json['categories'])
        self.assertEqual(2, len(result.json['categories']))


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
