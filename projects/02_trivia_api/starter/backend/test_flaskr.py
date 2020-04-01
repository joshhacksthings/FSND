import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # Pagination tests
    def test_success_pagination(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_404_pagination(self):
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Error! Route not found.")

    # Categories tests
    def test_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']) > 0)

    def test_404_sent_requesting_non_existing_category(self):
        response = self.client().get('/categories/9999')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Error! Route not found.")

    # Test Questions
    # Deleting questions test
    def test_success_delete_question(self):
        question = Question(
            question='What is your favorite color?', answer='Blue, no, green!',
            difficulty=10, category=1
        )
        question.insert()
        question_id = question.id

        response = self.client().delete("/questions/{}".format(question_id))
        data = json.loads(response.data)

        question = Question.query.filter(
            Question.id == question.id).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(question, None)

    def test_422_delete_fake_question(self):
        response = self.client().delete('/questions/a')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Error! Request could not be processed")

    # add questions
    def test_success_add_question(self):
        new_question = {
            'question': 'succcess question',
            'answer': 'success answer!',
            'difficulty': 1,
            'category': 1
        }
        total_questions_before = len(Question.query.all())
        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)
        total_questions_after = len(Question.query.all())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(total_questions_after, total_questions_before + 1)

    def test_422_add_question(self):
        new_question = {
            'question': 'some dumb question',
            'answer': 'some dumb answer',
            'category': 1
        }
        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Error! Request could not be processed")

    # Search questions
    def test_success_search_question(self):
        new_search = {'searchTerm': 'a'}
        response = self.client().post('/questions/search', json=new_search)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_404_search_question(self):
        new_search = {
            'searchTerm': '',
        }
        response = self.client().post('/questions/search', json=new_search)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Error! Route not found.")

    # Category questions
    def test_get_questions_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_questions_category(self):
        response = self.client().get('/categories/a/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Error! Route not found.")

    # Quiz success
    def test_success_quiz(self):
        new_quiz_round = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Entertainment', 'id': 5
              }
        }

        response = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_quiz(self):
        new_quiz_round = {'previous_questions': []}
        response = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Error! Request could not be processed")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()