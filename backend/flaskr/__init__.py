import os
from http.client import OK

from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    db = setup_db(app)

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
        return jsonify({
            "categories": _read_all_categories()
        })

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
            "categories": _read_all_categories(),
            "current_category": None
        }
        return jsonify(result)

    @app.route('/api/questions/<id>', methods=['DELETE'])
    def delete_question(id):
        """
        DELETE question using a question ID.
        """
        try:
            Question.query.filter_by(id=id).delete()
            db.session.commit()
            return jsonify({
                "result": "success"
            })
        except:
            db.session.rollback()
        finally:
            db.session.close()

    @app.route('/api/questions/new', methods=['POST'])
    def create_question():
        """
        Creates a new question
        """
        question_text = request.json['question']
        answer = request.json['answer']
        difficulty = request.json['difficulty']
        category = request.json['category']

        question_object = Question(question_text, answer, category, difficulty)
        db.session.add(question_object)
        db.session.commit()
        return jsonify({
            "result": "success"
        })

    @app.route('/api/questions', methods=['POST'])
    def search_questions():
        """
        Returns case insensitive matches for a search term
        """
        search_term = request.json['searchTerm']
        questions = Question.query.filter(Question.question.ilike(f"%{search_term}%")).all()
        return jsonify({
            "questions": list(map(lambda x: _map_question(x), questions)),
            "total_questions": len(questions),
            "current_category": None
        })

    @app.route('/api/categories/<id>/questions')
    def get_questions_by_category(id):
        """
        Get all questions filtered by a category
        """
        questions_by_category = Question.query.filter(Question.category == id).all()
        return jsonify({
            "questions": list(map(lambda x: _map_question(x), questions_by_category)),
            "total_questions": len(questions_by_category),
            "current_category": _read_category(id),
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
        'category': _read_category(question.category),
        'difficulty': question.difficulty
    }


def _read_category(id):
    current_category_object = Category.query.get(id)
    return current_category_object.type if current_category_object is not None else None


def _read_all_categories():
    categories = Category.query.all()
    return list(map(lambda x: x.type, categories))
