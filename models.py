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

from flask.ext.sqlalchemy import SQLAlchemy
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

    users = db.relationship("User", backref = "Idea")


    def __init__ (self, username, password):
        self.userid = userid
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

    def __init__ (self, title, score, text, userid):
        self.ideaid = ideaid
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

    db.create_all()

    #populate User table
    admin1 = User("Archana", bcrypt.generate_password_hash("mypwd"), "admin")
    db.session.add(admin1)
    db.session.commit()
    user1 = User("User1", bcrypt.generate_password_hash("upwd"), "user")
    db.session.add(user1)
    db.session.commit()
    user2 = User("User2", bcrypt.generate_password_hash("u2pwd"), "user")
    db.session.add(user2)
    db.session.commit()

    #populate Quiz table
    qz1 = Quiz( "Python Basics  ", "Simple  ", "Explanation", 1, 2)
    qz2 = Quiz( "Python Advanced", "Moderate", "No text    ", 1)
    db.session.add(qz1)
    db.session.add(qz2)
    db.session.commit()

    #populate Questions table
    ques1 = Question("What does 'def foo(): pass do", 
                      "A fn which does nothing",1,1)
    ques2 = Question("Is python an OOP l           ", 
                      "Yes python is an OOP l",1,1)
    db.session.add(ques1)
    db.session.add(ques2)
    db.session.commit()

    #populate Answer choices table
    ans1  = Anschoice(1, 1, "a. This function does nothing      ", True)
    ans2  = Anschoice(1, 1, "b. This function returns a fn pass ", False)
    ans3  = Anschoice(1, 1, "c. This function is not yet defined", False)
    ans4  = Anschoice(1, 2, "a. Yes Python is object oriented   ", True)
    ans5  = Anschoice(1, 2, "b. No Python is not object oriented", False)
    ans6  = Anschoice(1, 2, "c. Python may not be used as OOP l ", True)
    db.session.add(ans1)
    db.session.add(ans2)
    db.session.add(ans3)
    db.session.add(ans4)
    db.session.add(ans5)
    db.session.add(ans6)
    db.session.commit()

    return None


