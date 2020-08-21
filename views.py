""" #######################################################################"""
#
#   File Name      Date          Owner            Description
#   ----------    -------      ----------       ----------------
#   views.py      8/21/20       Arch        View fns for ideaapis
#
#  Handles HTTP requests/JSON for a ideaslists restful API service using
#  Flask/SQLAlchemy. 
#  Flask session, basic authentication are
#  implemented , Flask bcrypt is used for password encryption.
#
"""###########################################################################"""

import os, logging
from flask import Flask, request, json, jsonify, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.bcrypt import Bcrypt
import models 
import utls 
import basicauth 
import logs 

app = Flask(__name__)
bcrypt = Bcrypt(app)
api = Api(app)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

class InvalidUsageException(Exception):
    """ Handles exceptions not caught by framework and sends response
    """
    status_code = 404

    def __init__(self, message, status_code=None, payload=None):
        super(InvalidUsageException,self).__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsageException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    logs.info_ (response)
    return response
    
class UserIdeasAPI(Resource):
    """ Class that defines methods for processing get/post requests 
        for /api/ideaslists endpoint 
    """

    def __init__(self):
        """ Uses RequestParser class of Flask restful to parse/validate
            flask.request 
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("title", type=str, required=True, 
                                   help="No title given for idea", 
                                   location='json')
        self.reqparse.add_argument("text", type=str, required=True,
                                   help="Idea text not provided", 
                                   location='json')
        self.reqparse.add_argument("score", type=str, required=True,
                                   help="No score level given for idea", 
                                   location='json')
        super(UserIdeasAPI, self).__init__()


    # GET /admin/ideaslists
    @basicauth.login_required
    def get(self):
        """Get all ideaslists"""
        logs.debug_ ("_______________________________________________")
        logs.debug_ ("IdeasAPI get fn: %s" %(request))

        # Query ideaslists for this admin from idea table
        # Should that be the case or should admin be able to see
        # other ideaslists as well
        userid, username = utls.get_user_from_hdr()
        query_obj = models.Idea.query.filter_by(userid=userid).all()
        if not query_obj:
            response = handle_invalid_usage(InvalidUsageException
                                ('Error: No ideaslists found', status_code=404))
            return response
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                              ('Error: No active session for this user found',
                               status_code=404))
            return response

        # Return response
        resource_fields = {}
        resource_fields['ideaid'] =fields.Integer 
        resource_fields['title']=fields.String 
        resource_fields['desc']=fields.String 
        resource_fields['score'] =fields.String 

        ideaslists = marshal(query_obj, resource_fields)
        response = jsonify(ideaslists=ideaslists)
        response.status_code = 200
        logs.info_(response)
        utls.display_tables()
        return response

    # POST /admin/ideaslists
    @basicauth.login_required
    def post(self):
        """Add new idea"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("IdeasAPI post fn: %s\nJson Request\n=============\n %s"
                     %(request, request.json))

        userid, username = utls.get_user_from_hdr()
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                                ('Error: No active session for this user found', 
                                 status_code=404))
            
            return response

        # Get values from request
        args = self.reqparse.parse_args()
        for key, value in args.iteritems():
            if value is not None:
                if (key == 'title'):
                    title = request.json['title']
                if (key == 'score'):
                    score = request.json['score']
                if (key == 'text'):
                    text = request.json['text']

        # Update tables
        idea_obj = models.Idea(title, score, text, userid)
        models.db.session.add(idea_obj)
        models.db.session.commit()
        
        # Return response
        location = "/ideaslists/%s" % idea_obj.ideaid
        query_obj = models.Idea.query.filter_by(ideaid=idea_obj.ideaid).all()

        resource_fields =  {'ideaid':fields.Integer, 
                           'title':fields.String,
                           'score':fields.String,
                           'text':fields.String,
                           'no_ques':fields.Integer
                          }
                            
        idea = marshal(query_obj, resource_fields)
        response = jsonify(idea=idea)
        response.status_code = 201
        response.location = location
        logs.info_(response)
        utls.display_tables()
        return response

class UserIdeaAPI(Resource):
    """ Class that defines methods for processing get/patch/del requests 
        for /api/ideaslists/<ideaid> endpoint 
    """

    def __init__(self):
        """ Uses RequestParser class of Flask restful to parse/validate
            flask.request 
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("title", type=str, 
                             help="No title given", location='json')
        self.reqparse.add_argument("score", type=str,
                             help="No score level set", location='json')
        self.reqparse.add_argument("text", type=str, 
                             help="text", location='json')
        super(UserIdeaAPI, self).__init__()

    # GET  /admin/ideaslists/{ideaid}
    @basicauth.login_required
    def get(self, ideaid):
        """Get idea details"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("IdeaAPI get fn: %s" %(request))

        # Check if user is auth to get details of this idea
        userid, username = utls.get_user_from_hdr()
        query_obj = models.Idea.query.filter_by(ideaid=ideaid).first()
        if (query_obj.userid != userid):
            response = handle_invalid_usage(InvalidUsageException
                       ('Error: Unauthorized Username for this idea', \
                        status_code=401))
            
            return response
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: No active session for this user found', 
                         status_code=404))
            return response

        # Query from idea table
        query_obj = models.Idea.query.filter_by(ideaid = ideaid).all()
        if not query_obj:
            response = handle_invalid_usage(InvalidUsageException
                    ('Error: Idea not found', status_code=404))
            return response

        # Return response
        resource_fields =  {'ideaid':fields.Integer, 
                           'title':fields.String,
                           'score':fields.String,
                           'text':fields.String,
                           'no_ques':fields.Integer
                          }
                            
        idea = marshal(query_obj, resource_fields)
        response = jsonify(idea=idea)
        response.status_code = 200
        logs.info_(response)
        return response

    # PATCH /admin/ideaslists/{ideaid}
    @basicauth.login_required
    def patch(self, ideaid):
        """Edit idea details"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("IdeaAPI patch fn: %s \nJson Request\n=============\n %s" 
                 %(request, request.json)) 
        userid, username = utls.get_user_from_hdr()
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                       ('Error: No active session for this user found', 
                        status_code=404))
            
            return response

        # Get values from req
        args = self.reqparse.parse_args()
        cols = {}
        no_data = True
        for key, value in args.iteritems():
            if value is not None:
                no_data = False
                cols[key] = request.json[key]

        # Check if user is auth to update this idea
        query_obj = models.Idea.query.filter_by(ideaid=ideaid).first()
        if  (query_obj.userid != userid):
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: Unauthorized Username for this idea', \
                         status_code=401))
            
            return response

        # If no input in patch request, return 400
        if no_data:
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: No input data provided in Patch req', 
                         status_code=400))
            return response

        # Update tables
        models.Idea.query.filter_by(ideaid=ideaid).update(cols)
        models.db.session.commit()

        # Return response
        query_obj = models.Idea.query.filter_by(ideaid=ideaid).all()
        resource_fields =  {'ideaid':fields.Integer, 
                           'title':fields.String,
                           'score':fields.String,
                           'text':fields.String,
                           'no_ques':fields.Integer
                          }
                            
        idea = marshal(query_obj, resource_fields)
        response = jsonify(idea=idea)
        response.status_code = 200
        logs.info_(response)
        utls.display_tables()
        return response

    # DELETE  /admin/ideaslists/{ideaid}
    @basicauth.login_required
    def delete(self, ideaid):
        """Delete idea"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("IdeaAPI delete fn: %s" %(request))

        # Check if user is auth to delete this idea
        userid, username = utls.get_user_from_hdr()
        query_obj = models.Idea.query.filter_by(ideaid=ideaid).first()
        if  (query_obj.userid != userid):
            response = handle_invalid_usage(InvalidUsageException
                             ('Error: Unauthorized Username for this idea', \
                              status_code=401
                              )
                             )
            
            return response
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                       ('Error: No active session for this user found', 
                        status_code=404))
            return response
     
        # Delete all questions table entries for the idea
        models.Question.query.join(models.Idea).filter(models.Question.ideaid == ideaid).\
                delete()
        
        # Delete all Ans choices table entries for idea
        models.Anschoice.query.join(models.Idea).filter(models.Anschoice.ideaid == ideaid).\
                delete()

        # Delete idea
        models.Idea.query.filter(models.Idea.ideaid == ideaid).delete()
        models.db.session.commit()
        
        # Return response
        utls.display_tables()
        return 204


class UsersAPI(Resource):
    """ Class that defines methods for processing post requests 
        for /users endpoint. This endpoint can either be requested
        directly from the client side or can be a result of control 
        reaching here once the send_authenticate_req function is 
        processed.
        Flask session is created once the user is created(post) or 
        logs in(get).
    """

    def __init__(self):
        """ Uses RequestParser class of Flask restful to parse/validate
            flask.request 
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("username", type=str, required=True,
                             help="No username provided", location='json')
        self.reqparse.add_argument("password", type=str, required=True,
                             help="No password given", location='json')
        super(UsersAPI, self).__init__()

    # POST /users
    def post(self):
        """Login already existing user or add new user"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("UserAPI post fn: %s\nJson Request\n=============\n %s" %(request, request.json))

        # Get values from request
        args = self.reqparse.parse_args()
        for key, value in args.iteritems():
            if value is not None:
                if (key == 'username'):
                    username = request.json['username']
                if (key == 'password'):
                    password = request.json['password']


        # Check and Update tables
        # This is implemented as if we are processing get /users
        user_obj = models.User.query.filter_by(username=username).all()
        user_index = None
        for i in range(len(user_obj)):
            if username in user_obj[i].username:
                user_index = i
        if user_index is not None:
            #match encrypted password with one in table 
            if not bcrypt.check_password_hash(user_obj[user_index].password, 
                    password):
                response = handle_invalid_usage(InvalidUsageException
                           ('Error: Password for user does not match', 
                            status_code=401))
                return response

        else:
            # Add new user
            user_obj = models.User(username, 
                                 bcrypt.generate_password_hash(password))
            models.db.session.add(user_obj)
            models.db.session.commit()

        # Create flask session here with secret key based on username
#        if 'username' not in session:
#            session['username'] = username

        # Return response
        location = "/users/%s" % user_obj.userid
        query_obj = models.User.query.filter_by(userid=user_obj.userid).all()
        resource_fields = {'userid':fields.Integer}
        user = marshal(query_obj, resource_fields)
        response = jsonify(user=user)
        response.status_code = 201
        response.location = location
        logs.info_(response)
        utls.display_tables()
        return response



class UsrIdeaRtAPI(Resource):

    # GET /user/ideaslists/{ideaid}/result
    @basicauth.login_required
    def get(self, ideaid):
        """Get result for taker of this  idea"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("UsrIdeaRtAPI get fn: %s" %(request))

        userid, username = utls.get_user_from_hdr()
        if 'username' not in session:
            response = handle_invalid_usage(InvalidUsageException
                        ('Error: No active session for this user found', 
                         status_code=404))
            return response

        # Find idea result for session
        query_obj = models.User.query.filter_by(userid=userid).first()
        result = query_obj.qzscore

        # Return response
        logs.debug_ ("Json response")
        logs.debug_ ("=============\n")
        logs.debug_ ("{\'result\':%s}\n" %(result))
        response = jsonify (result=result)
        response.status_code = 200
        utls.display_tables()
        logs.info_(response)
        return response


class SessionAPI(Resource):
    """ Class that defines methods for processing del requests 
        for /session endpoint -mainly to delete sessions
    """

    # DELETE  /session (used to delete sessions)
    @basicauth.login_required
    def delete(self):
        """Delete session"""
        logs.debug_ ("_________________________________________________")
        logs.debug_ ("SessionAPI del fn: %s" %(request.url))

        # Pop user from session
        userid, username = utls.get_user_from_hdr()
        if 'username' not in session:
            logs.debug_("User already not in session")
        else:
            session.pop('username', None)

        # Return response
        utls.display_tables()
        return 204

api.add_resource(UserIdeasAPI, '/admin/ideaslists')
api.add_resource(UserIdeaAPI, '/admin/ideaslists/<int:ideaid>')

api.add_resource(UsrIdeasAPI, '/user/ideaslists')
api.add_resource(UsrIdeaAPI, '/user/ideaslists/<int:ideaid>')

api.add_resource(UsersAPI, '/users')
api.add_resource(SessionAPI, '/session')

if __name__ == '__main__':

    #Initial config for db, this can be disabled
    models.db_init()

    utls.display_tables()
    app.debug = True

    app.run('192.168.33.10', 5001)

