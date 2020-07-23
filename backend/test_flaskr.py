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
                INSERT INTO categories (id, type) VALUES (1, 'Science'), (2, 'Sport');
            """)
            self.db.engine.execute("""
                INSERT INTO questions (id, question, answer, difficulty, category) 
                VALUES (1, 'What is the answer to everything', '42', 3, 1);

                INSERT INTO questions (id, question, answer, difficulty, category) 
                VALUES (2, 'When did the big bang happen', 'When the universe was created', 3, 1);
            """)

    def tearDown(self):
        """Executed after reach test"""
        with self.app.app_context():
            self.db.engine.execute("""
                DELETE FROM categories;
                DELETE FROM questions;
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

    def test_get_questions_returns_correct_result(self):
        client = self.client()
        result = client.get("/api/questions?page=1")
        self.assertEqual(200, result.status_code)
        question = {
            "id": 1,
            "question": 'What is the answer to everything',
            "answer": '42',
            "difficulty": 3,
            "category": 'Science',
        }
        self.assertIn(question, result.json['questions'])

    def test_get_questions_fails_when_page_is_not_specified(self):
        result = self.client().get('/api/questions')
        self.assertEqual(400, result.status_code)
        all(self.assertIn(item, result.json.items()) for item in {
            "success": False,
            "code": 400,
        }.items())


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
