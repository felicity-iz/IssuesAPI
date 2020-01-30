from flask_sqlalchemy import SQLAlchemy
from app import app

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///issueTracker.db'

db = SQLAlchemy(app)
#data model
class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.String, nullable=False)
    close_date = db.Column(db.String)
    title = db.Column(db.String(250), nullable=False)
    status = db.Column(db.String, nullable=False)
    description_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    milestone_id = db.Column(db.Integer, db.ForeignKey('milestone.id'))

    def __repr__(self):
        return f"Issue('{self.id}','{self.title}','{self.author_id}')"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    avatar_url = db.Column(db.String(100), nullable=False, default='https://avatars0.githubusercontent.com/u/30222736?s=400&v=4')
    location = db.Column(db.String(50))
    bio = db.Column(db.String(150))
    org = db.Column(db.String(50))
    org_url = db.Column(db.String(100))

    #def __repr__(self):
    #    return f"User('{self.id}','{self.username}')"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id'), nullable=False)

    def __repr__(self):
        return f"Comment('{self.id}','{self.issue_id}')"

class Label(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    def __repr__(self):
        return f"Label('{self.id}','{self.title}')"

class AssignedLabel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label_id = db.Column(db.Integer, db.ForeignKey('label.id'), nullable=False)
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id'), nullable=False)
    def __repr__(self):
        return f"AssignedLabel('{self.label_id}','{self.issue_id}')"

class Milestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"Milestone('{self.id}','{self.title}')"
