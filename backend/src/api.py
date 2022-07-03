import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink,db
from .auth.auth import AuthError, get_token_auth_header, requires_auth
import sys
app = Flask(__name__)
setup_db(app)
CORS(app)


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    drink = [drink.short() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': drink
    }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods = ['GET'])
@requires_auth("get:drinks-detail")
def get_drinks_details(payload):
    print(payload)
    try:
        drinks = Drink.query.all()
        drink = [drink.long() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": drink
        }),200
    except:
        print(sys.exc_info())
        abort(422)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def post_drink(payload):
    print(payload)
    body = request.get_json()
    title = body.get("title", None)
    recipe = body.get("recipe", None)

    drink = Drink.query.filter_by(title=title).first()
    if drink:
        abort(409)
    
    for item in recipe:
        color = item.get("color", None)
        parts = item.get("parts", None)
        name = item.get("name", None)
        if not color or not parts or not name:
            abort(400)

    if title and recipe:
        try:
            drink = Drink(title=title, recipe=json.dumps(recipe))
            drink.insert()
            return jsonify({
                "success": True,
                "drinks": [drink.long()]
                }),200
        except:
            abort(422)
    else:
        print(sys.exc_info())
        abort(400)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth("patch:drinks")
def edit_drink(payload, id):

    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    
    body = request.get_json()
    drink_title = body.get("title", None)
    drink_recipe = body.get("recipe", None)

    if drink_title:
        drink.title = drink_title

    if drink_recipe:
        for item in drink_recipe:
            color = item.get("color", None)
            parts = item.get("parts", None)
            name = item.get("name", None)
            if not color or not parts or not name:
                abort(400)

        drink.recipe = json.dumps(drink_recipe)
    
    try:
        drink.update()
    except:
        print(sys.exc_info())
        abort(422)
    drinks = [drink.long()]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)
    else:
        try:
            drink.delete()
            return jsonify({
                "success": True,
                "delete": id
            })
        except BaseException:
            print(sys.exc_info())
            abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request'
    }), 400

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not allowed'
    }), 405


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal server error'
    }), 500


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Unauthorized'
    }), 401


@app.errorhandler(409)
def conflict(error):
    return jsonify({
        'success': False,
        'error': 409,
        'message': 'Conflict'
    }), 409


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error_handler(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error["description"]
    }), error.status_code
