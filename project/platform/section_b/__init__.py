import flask_restful
from project import blueprints

api = flask_restful.Api(blueprints[__name__], prefix="/blueprint2")

@api.route('/helloworld')
class HelloWorld(flask_restful.Resource):
    def get(self):
        return {'hello2': 'world2'}