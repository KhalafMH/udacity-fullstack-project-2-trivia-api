import unittest

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question


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
                INSERT INTO questions (question, answer, difficulty, category) 
                VALUES ('What is the answer to everything', '42', 3, 1);

                INSERT INTO questions (question, answer, difficulty, category) 
                VALUES ('When did the big bang happen', 'When the universe was created', 3, 1);
            """)

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            self.db.engine.execute("DELETE FROM questions")
            self.db.engine.execute("DELETE FROM categories")

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
            "question": 'What is the answer to everything',
            "answer": '42',
            "difficulty": 3,
            "category": 'Science',
        }
        try:
            exists = next(q for q in result.json['questions'] if all(item in q.items() for item in question.items()))
        except StopIteration:
            self.fail("Expected question was not found in the results")
        self.assertIsNotNone(exists)

    def test_get_questions_fails_when_page_is_not_specified(self):
        result = self.client().get('/api/questions')
        self.assertEqual(400, result.status_code)
        all(self.assertIn(item, result.json.items()) for item in {
            "success": False,
            "code": 400,
        }.items())

    def test_delete_question_succeeds(self):
        client = self.client()
        question_id = 100
        with self.app.app_context():
            value = self.db.engine.execute(f"""
                INSERT INTO questions (id, question, answer, difficulty, category) 
                VALUES ({question_id}, 'Question 100', 'Answer 100', 3, 1)
            """)
            self.assertIsNotNone(value)
        result = client.delete(f"/api/questions/{question_id}")
        self.assertEqual(200, result.status_code)
        self.assertEqual({"success": True}, result.json)
        with self.app.app_context():
            value = self.db.engine.execute(f"SELECT * FROM questions WHERE id={question_id}").first()
            self.assertIsNone(value)

    def test_delete_question_fails_when_passed_nonexistent_id(self):
        client = self.client()
        question_id = 500
        result = client.delete(f"/api/questions/{question_id}")
        self.assertEqual(404, result.status_code)
        all(self.assertIn(item, result.json.items()) for item in {
            "success": False,
            "code": 404,
        }.items())

    def test_create_question_creates_a_question(self):
        client = self.client()
        json = {
            "question": "What is the answer",
            "answer": "answer",
            "category": "Science",
            "difficulty": 5
        }
        result = client.post("/api/questions", json=json)
        self.assertEqual(201, result.status_code)
        self.assertDictEqual({"success": True}, result.json)
        with self.app.app_context():
            value = self.db.engine.execute(f"""
                SELECT * FROM questions WHERE question='{json["question"]}' 
                    AND answer='{json["answer"]}'
                    AND category='Science'
                    AND difficulty=5
            """).first()
            self.assertIsNotNone(value)

    def test_create_question_fails_when_request_is_badly_formatted(self):
        client = self.client()
        json = {
            "question": "What is the answer",
            "answer": "answer",
            "category": "Science",
            "difficulty": 5
        }
        result = client.post("/api/questions", data=json)
        self.assertEqual(415, result.status_code)
        self.assertIn(("success", False), result.json.items())

    def test_search_questions_returns_expected_results(self):
        client = self.client()

        result1 = client.post("/api/search/questions", json={"searchTerm": "the"})
        self.assertEqual(200, result1.status_code)
        self.assertEqual(2, len(result1.json["questions"]))

        result2 = client.post("/api/search/questions", json={"searchTerm": "bang"})
        self.assertEqual(200, result2.status_code)
        self.assertEqual(1, len(result2.json["questions"]))
        self.assertEqual("When did the big bang happen", result2.json["questions"][0]["question"])

        result3 = client.post("/api/search/questions", json={"searchTerm": "BANG"})
        self.assertEqual(200, result3.status_code)
        self.assertEqual(1, len(result3.json["questions"]))
        self.assertEqual("When did the big bang happen", result3.json["questions"][0]["question"])

        result4 = client.post("/api/search/questions", json={"searchTerm": "NonexistentTerm"})
        self.assertEqual(200, result4.status_code)
        self.assertEqual(0, len(result4.json["questions"]))

    def test_search_fails_when_no_search_term_is_provided(self):
        client = self.client()

        result1 = client.post("/api/search/questions", json={})
        self.assertEqual(400, result1.status_code)

        result2 = client.post("/api/search/questions", json={"searchTerm": " "})
        self.assertEqual(422, result2.status_code)

    def test_get_questions_by_category_returns_expected_questions(self):
        client = self.client()
        category_id_1 = 1
        result1 = client.get(f"/api/categories/{category_id_1}/questions")
        self.assertEqual(200, result1.status_code)
        self.assertEqual('Science', result1.json['current_category'])
        self.assertEqual(2, result1.json['total_questions'])
        self.assertEqual(2, len(result1.json['questions']))
        all(self.assertEqual('Science', question['category']) for question in result1.json['questions'])

        category_id_2 = 2
        result2 = client.get(f"/api/categories/{category_id_2}/questions")
        self.assertEqual(200, result2.status_code)
        self.assertEqual('Sport', result2.json['current_category'])
        self.assertEqual(0, result2.json['total_questions'])
        self.assertEqual(0, len(result2.json['questions']))

    def test_get_questions_by_category_fails_when_category_is_given_by_name(self):
        client = self.client()
        category = 'Science'
        result = client.get(f"/api/categories/{category}/questions")
        self.assertEqual(404, result.status_code)

    def test_get_questions_by_category_fails_when_passed_a_nonexistent_category_id(self):
        client = self.client()
        category_id = 1000
        result = client.get(f"/api/categories/{category_id}/questions")
        print(result.json)
        self.assertEqual(400, result.status_code)

    def test_get_quiz_question_returns_a_question_in_the_specified_category(self):
        client = self.client()

        result1 = client.post("/api/quizzes", json=dict(previous_questions=[], quiz_category="1"))
        self.assertEqual(200, result1.status_code)
        self.assertEqual("Science", result1.json['question']['category'])

    def test_get_quiz_question_fails_when_there_are_no_remaining_questions(self):
        client = self.client()

        result1 = client.post("/api/quizzes", json=dict(previous_questions=[
            Question(
                question="What is the answer to everything",
                answer="42",
                category="Science",
                difficulty=3).format(),
            Question(
                question="When did the big bang happen",
                answer="When the universe was created",
                category="Science",
                difficulty=3).format(),
        ], quiz_category="1"))
        self.assertEqual(404, result1.status_code)

        result2 = client.post("/api/quizzes", json=dict(previous_questions=[], quiz_category="2"))
        self.assertEqual(404, result2.status_code)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
