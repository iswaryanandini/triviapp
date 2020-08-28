import os
import unittest
import json
import pdb
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
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'Admin123','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        
        self.new_quest = {
            'question': 'who is the superstar of south indian cinema',
            'answer': 'Rajinikanth',
            'difficulty': 3,
            'category': 5
        }

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

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_failed_get_questions(self):
        res = self.client().get('/questions?page=15')
        data = json.loads(res.data)

        self.assertFalse(data['questions'])
        self.assertEqual(data['success'], True)

    def test_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        # self.assertTrue(len(data['categories']))

    def test_failed_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        # pdb.set_trace()

        # self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertFalse(len(data['categories']) > 6)

    def test_delete_questions(self):
        res = self.client().delete('/questions/34')
        data = json.loads(res.data)
        quest = Question.query.filter(Question.id == 34).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 34)

    def test_failed_delete_questions(self):
        res = self.client().delete('/questions/20')
        data = json.loads(res.data)
        quest = Question.query.filter(Question.id == 20).one_or_none()

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_create_questions(self):
        res = self.client().post('/add', json=self.new_quest)
        data = json.loads(res.data)


        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_failed_create_questions(self):
        res = self.client().post('/add/45', json=self.new_quest)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_search_question_withresults(self):
        res = self.client().post('/questions', json={'searchTerm': 'title'})
        data = json.loads(res.data)
        

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['current_category'], None)
        self.assertTrue(data['total_questions'])

    def test_search_question_withoutresults(self):
        res = self.client().post('/questions', json={'searchTerm': 'maapi'})
        data = json.loads(res.data)
        

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['current_category'], None)
        self.assertEqual(data['total_questions'], 0)

    def test_get_questby_categories(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_failed_get_questby_categories(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_playquiz(self):
        res = self.client().post('/play', json={'previous_questions': [4], 'quiz_category': {'id': 2}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_failed_get_playquiz(self):
        res = self.client().post('/play', json={'quiz_category': {'id': 8}})
        data = json.loads(res.data)
        print(data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()