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
  CORS(app)
  db = SQLAlchemy(app)
  
  
  # @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  

  
  # @TODO: Use the after_request decorator to set Access-Control-Allow
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  
  @app.route('/categories',methods=['GET'])
  def get_categories():
    category = Category.query.order_by(Category.id).all()
    format_category = [eachcategory.format() for eachcategory in category]
    result = {
      'success':True,
      'categories':get_category_list()
    }
    return result

  
  # @TODO: 
  # Create an endpoint to handle GET requests for questions, 
  # including pagination (every 10 questions). 
  # This endpoint should return a list of questions, 
  # number of total questions, current category, categories. 

  # TEST: At this point, when you start the application
  # you should see questions and categories generated,
  # ten questions per page and pagination at the bottom of the screen for three pages.
  # Clicking on the page numbers should update the questions. 
  def get_category_list():
    categories = {}
    for category in Category.query.all():
        categories[category.id] = category.type
    return categories
  def get_paginated_quest(request, questions, num_of_questions):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * num_of_questions
    end = start + num_of_questions
    questions = [question.format() for question in questions]
    formatted_questions = questions[start:end]
    return formatted_questions
  @app.route('/questions',methods=['GET'])
  def get_questions():
      questions = Question.query.all()
      if len(questions) == 0:
        abort(404)

      return jsonify({
            'success': True,
            'questions': get_paginated_quest(request, questions, QUESTIONS_PER_PAGE),
            'total_questions': len(questions),
            'categories': get_category_list()
        })

  
  # @TODO: 
  # Create an endpoint to DELETE question using a question ID. 

  # TEST: When you click the trash icon next to a question, the question will be removed.
  # This removal will persist in the database and when you refresh the page. 
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_questions(question_id):
    try:
      body = request.get_json()
      quest = Question.query.filter(Question.id == question_id).one_or_none()

      if quest is None:
        abort(404)
      else:  
        quest.delete()
        db.session.commit()

        page = request.args.get('page', 1, type=int)
        start = (page-1) * 10
        end = page + 10

        questorder = Question.query.order_by(Question.id).all()
        formatted_quest = [eachquest.format() for eachquest in questorder]

        return jsonify({
          'success': True,
          'deleted': question_id,
          'questions': formatted_quest[start:end],
          'total_questions': len(formatted_quest)
        })

    except:
      abort(422)







  # @TODO: 
  # Create an endpoint to POST a new question, 
  # which will require the question and answer text, 
  # category, and difficulty score.

  # TEST: When you submit a question on the "Add" tab, 
  # the form will clear and the question will appear at the end of the last page
  # of the questions list in the "List" tab.  
  @app.route('/add', methods=['POST'])
  def create_questions():
      error= False
      body = {}
      try:
        new_quest = request.get_json()['question']
        new_answer = request.get_json()['answer']
        new_difficulty = request.get_json()['difficulty']
        new_category = request.get_json()['category']
        newquest = Question(question = new_quest ,answer = new_answer ,difficulty = new_difficulty ,category = new_category )
        db.session.add(newquest)
        db.session.commit()
        flash('Question ' + newquest.id + ' was successfully listed!')
        body['success'] = True
        body['created'] = newquest.id
      except:
        db.session.rollback()
        error = True
      finally:
        db.session.close()
      if error:
        abort(500)
      else:
        return jsonify(body)


  
  # @TODO: 
  # Create a POST endpoint to get questions based on a search term. 
  # It should return any questions for whom the search term 
  # is a substring of the question. 

  # TEST: Search by any phrase. The questions list will update to include 
  # only question that include that string within their question. 
  # Try using the word "title" to start. 
  @app.route('/questions',methods= ['POST'])
  def search_quest():
    try:
      body = request.get_json()
      search = body.get('searchTerm', None) 
      questsearch = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
      format_quest = [eachquest.format() for eachquest in questsearch]
      return jsonify({
        'questions': format_quest,
        'total_questions': len(format_quest),
        'current_category': None
      })
    except:
      abort(422)


  # @TODO: 
  # Create a GET endpoint to get questions based on category. 

  # TEST: In the "List" tab / main screen, clicking on one of the 
  # categories in the left column will cause only questions of that 
  # category to be shown. 
  @app.route('/categories/<int:category_id>/questions',methods= ['GET'])
  def get_list_category(category_id):
    
    page = request.args.get('page', 1, type=int)
    start = (page-1) * 10
    end = page + 10

    try:
      questlist = Question.query.filter(Question.category == category_id).all()
      formatted_quest = [eachquest.format() for eachquest in questlist]

      return jsonify({
            'success': True,
            'current_category': get_category_list(),
            'questions': formatted_quest,
            'total_questions': len(formatted_quest)
          })

    except:
      abort(422)




  # @TODO: 
  # Create a POST endpoint to get questions to play the quiz. 
  # This endpoint should take category and previous question parameters 
  # and return a random questions within the given category, 
  # if provided, and that is not one of the previous questions. 

  # TEST: In the "Play" tab, after a user selects "All" or a category,
  # one question at a time is displayed, the user is allowed to answer
  # and shown whether they were correct or not. 
  @app.route('/play',methods= ['POST'])
  def create_play():
    body = request.get_json()
    quizCategory = body.get('quiz_category', None).get('id')
    previousQuestions = body.get('previous_questions',None)
    if quizCategory == 0:
      quizlist = Question.query.filter(Question.id.notin_((previousQuestions))).all()
    else:
      quizlist = Question.query.filter_by(category=quizCategory).filter(Question.id.notin_((previousQuestions))).all()
    selected = []
    for eachquest in quizlist:
        selected.append(
          eachquest.format()
        )
        new_question = random.choice(selected)

    try:
          return jsonify({
            'success': True,
            'question': new_question
          })     
    except:
      abort(404)
  # '''
  # @TODO: 
  # Create error handlers for all expected errors 
  # including 404 and 422. 
  # '''
  @app.errorhandler(404)
  def resource_not_found(error):
      return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
      }), 422

  @app.errorhandler(500)
  def unprocessable(error):
      return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
      }), 500
  
  return app

    