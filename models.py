###########################################################################
#
#   File Name      Date          Owner               Description
#   ----------   --------      ---------        -----------------
#   models.py     08/21/20   ARch             Db table design/models 
#                                                for ideasapi APIs 
#
#   Schema- models.db - tables: Users, Ideas
#
###########################################################################

from flask_sqlalchemy import SQLAlchemy
import textwrap, os
from views import app, bcrypt

file_path = os.path.abspath(os.getcwd())+"/models.db"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+file_path
db = SQLAlchemy(app)

MAXUSRS = 1000
MAXQZ = 100
MAXQS = 10000
MAXANS = 50000

class User(db.Model):
    """ Defines the columns and keys for User table """
    userid    = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String)
    password  = db.Column(db.String)



    def __init__ (self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '%i        %s            %s                    %s      %i' % (self.userid, self.username, self.password) 
    
class Idea(db.Model):
    """ Defines the columns and keys for Quiz table """
    ideaid    = db.Column(db.Integer, primary_key=True)
    title   = db.Column(db.String(80), unique = True)
    score   = db.Column(db.String(80))
    text    = db.Column(db.String(80))
    userid  = db.Column(db.Integer, db.ForeignKey('user.userid'))

    users = db.relationship("User", backref = "Idea")

    def __init__ (self, title, score, text, userid):
        self.title = title
        self.score = score
        self.text = text
        self.userid = userid

    def __repr__(self):
        return '%i   %s     %s     %s     %i    %i' % (self.ideaid, self.title, \
        self.score, (self.text).ljust(20), self.userid)
                    


def db_init():
    """ Initial config/population of the database tables """

    #Using drop_all temporarily to prevent integrity error between
    #subsequent runs. If db_init is not called this can be removed.
    #this can also be called at the end of this fn
    db.drop_all()
"""
    db.create_all()

    #populate User table
    user1 = User("User1", bcrypt.generate_password_hash("pwd123"))
    db.session.add(user1)
    db.session.commit()
    user2 = User("User2", bcrypt.generate_password_hash("abc123"))
    db.session.add(user2)
    db.session.commit()

    #populate idea table
    idea1 = Idea( "Project ", "Ease", "Build a creative project for happiness", user1)
    idea2 = Idea( "Project2", "Impact", "Build a Game from raspberrypi", user1)
    idea3 = Idea( "Project3", "Confidence", "Build a Puzzle", user2)
    idea4 = Idea( "Project4", "Impact", "Create a computer sc lesson with analogy of pizza", user2)
    db.session.add(idea1)
    db.session.commit()
    db.session.add(idea2)
    db.session.commit()
    return None
"""


