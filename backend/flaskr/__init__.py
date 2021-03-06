import random
from re import search

from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    db = setup_db(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def set_access_control(response: app.response_class):
        response.headers.add_header("Access-Control-Allow", True)
        return response

    @app.route("/api/categories")
    def get_all_categories():
        """
        Returns all available categories.
        """
        return jsonify({
            "success": True,
            "categories": _read_all_categories()
        })

    @app.route('/api/questions')
    def get_questions():
        """
        Returns paged questions
        """
        page_input = request.args.get('page')
        if page_input is None:
            abort(400)
        page = int(page_input)
        questions: list = Question.query.all()
        start = 10 * (page - 1)
        end = 10 * page
        page_questions = questions[start:end]
        result = {
            "success": True,
            "questions": list(map(lambda x: _map_question(x), page_questions)),
            "total_questions": len(questions),
            "categories": _read_all_categories(),
            "current_category": None
        }
        return jsonify(result)

    @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """
        DELETE question using a question ID.
        """
        try:
            question = Question.query.get(question_id)
            if question is None:
                abort(404)
            question.delete()
            db.session.commit()
            return jsonify({
                "success": True,
                "deleted_question_id": question.id
            })
        except SQLAlchemyError:
            db.session.rollback()
        finally:
            db.session.close()

    @app.route('/api/questions', methods=['POST'])
    def create_question():
        """
        Creates a new question
        """
        if request.content_type != "application/json":
            abort(415)
        question_text = request.json['question']
        answer = request.json['answer']
        difficulty = request.json['difficulty']
        category = request.json['category']

        question_object = Question(question_text, answer, category, difficulty)
        db.session.add(question_object)
        db.session.commit()
        return jsonify({
            "success": True
        }), 201

    @app.route('/api/search/questions', methods=['POST'])
    def search_questions():
        """
        Returns case insensitive matches for a search term
        """
        if request.content_type != "application/json":
            abort(415)
        search_term: str = request.json.get('searchTerm')
        if search_term is None:
            abort(400)
        if search("^\\s*$", search_term) is not None:
            abort(422)
        questions = Question.query.filter(
            Question.question.ilike(f"%{search_term}%")).all()
        return jsonify({
            "success": True,
            "questions": list(map(lambda x: _map_question(x), questions)),
            "total_questions": len(questions),
            "current_category": None
        })

    @app.route('/api/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id: int):
        """
        Get all questions filtered by a category
        """
        category = Category.query.get(category_id)
        if category is None:
            abort(400)
        questions_by_category = Question.query.filter(
            Question.category == str(category_id)).all()
        return jsonify({
            "success": True,
            "questions": list(
                map(lambda x: _map_question(x), questions_by_category)),
            "total_questions": len(questions_by_category),
            "current_category": _read_category(category_id),
        })

    @app.route('/api/quizzes', methods=['POST'])
    def get_quiz_question():
        """
        This endpoint should take category and previous question parameters
        and return a random questions within the given category,
        if provided, and that is not one of the previous questions.
        """
        if request.content_type != "application/json":
            abort(415)
        previous_questions: list[int] = request.json['previous_questions']
        category: str = request.json['quiz_category']

        filtered_category: list[Category] = Category.query.filter(
            Category.type == category).all()
        category_id: int or None = filtered_category[0].id \
            if filtered_category is not None and len(filtered_category) > 0 \
            else None
        questions = Question.query.all()
        if category_id is not None:
            filtered_questions = list(
                filter(lambda x: x.category == category_id, questions))
        else:
            filtered_questions = questions
        if len(filtered_questions) == 0 or len(filtered_questions) == len(
                previous_questions):
            return jsonify({
                "success": True
            })

        selection = int(random.random() * len(filtered_questions))
        while filtered_questions[selection].id in previous_questions:
            selection = int(random.random() * len(filtered_questions))

        return jsonify({
            "success": True,
            "question": _map_question(filtered_questions[selection])
        })

    @app.errorhandler(400)
    def handle_400(error):
        return jsonify({
            "success": False,
            "error": error.description,
            "code": error.code,
        }), error.code

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({
            "success": False,
            "error": error.description,
            "code": error.code,
        }), error.code

    @app.errorhandler(415)
    def handle_415(error):
        return jsonify({
            "success": False,
            "error": error.description,
            "code": error.code,
        }), error.code

    @app.errorhandler(422)
    def handle_422(error):
        return jsonify({
            "success": False,
            "error": error.description,
            "code": error.code,
        }), error.code

    @app.errorhandler(500)
    def handle_500(error):
        return jsonify({
            "success": False,
            "error": "Internal error",
            "code": 500,
        }), 500

    return app


def _map_question(question):
    return {
        'id': question.id,
        'question': question.question,
        'answer': question.answer,
        'category': _read_category(question.category),
        'difficulty': question.difficulty
    }


def _read_category(category_id: int):
    current_category_object = Category.query.get(category_id)
    return current_category_object.type \
        if current_category_object is not None \
        else None


def _read_all_categories():
    categories = Category.query.all()
    return list(map(lambda x: x.type, categories))


if __name__ == '__main__':
    Flask.run(create_app())
