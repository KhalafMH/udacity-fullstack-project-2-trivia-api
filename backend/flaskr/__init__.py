import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''

    '''
    Returns all available categories.
    '''
    @app.route("/api/categories")
    def get_all_categories():
        """
        Returns all available categories.
        """

        categories = Category.query.all()
        return jsonify(categories)

    @app.route('/api/questions')
    def get_questions():
        """
        Returns paged questions
        """

        page = int(request.args.get('page'))
        questions: list = Question.query.all()
        start = 10 * (page - 1)
        end = 10 * page
        page_questions = questions[start:end]
        result = {
            "questions": list(map(lambda x: _map_question(x), page_questions)),
            "total_questions": len(questions),
            "categories": list(map(lambda x: x.category, page_questions)),
            "current_category": None
        }
        return jsonify(result)

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
  
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
  
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
  
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    @app.route('/api/categories/<id>/questions')
    def get_questions_by_category(id):
        """
        Get all questions filtered by a category
        """

        questions_by_category = Question.query.filter(Question.category == id).all()
        print(f"questions by category: {questions_by_category}")
        return jsonify({
            "questions": list(map(lambda x: _map_question(x), questions_by_category)),
            "total_questions": len(questions_by_category),
            "current_category": _get_category(id),
        })

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
  
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''

    return app


def _map_question(question):
    return {
        'id': question.id,
        'question': question.question,
        'answer': question.answer,
        'category': _get_category(question.category),
        'difficulty': question.difficulty
    }


def _get_category(id):
    current_category_object = Category.query.get(id)
    return current_category_object.type if current_category_object is not None else None
