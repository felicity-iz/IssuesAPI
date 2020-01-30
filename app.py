import json
import collections
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///issueTracker.db'

db = SQLAlchemy(app)

#data model
#BUG ALERT: description_id shouldn't be in Issue but instead works as a query, currently not used but required as default
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

    def __repr__(self):
        return f"User('{self.id}','{self.username}')"

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

#tracks all label assignments
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

#Builder functions
def jsonBuilderMilestones(milestones):
    milestoneList = []
    if (not milestones):
        jsonResponse = json.dumps(milestoneList)
    else:
        if isinstance(milestones, list):
            for milestone in milestones:
                milestoneObj = collections.OrderedDict()
                milestoneObj['id'] = milestone.id
                milestoneObj['title'] = milestone.title
                milestoneList.append(milestoneObj)
        else:
            milestoneObj = collections.OrderedDict()
            milestoneObj['id'] = milestones.id
            milestoneObj['title'] = milestones.title
            milestoneList.append(milestoneObj)

        jsonResponse = json.dumps(milestoneList)

    return jsonResponse


def jsonBuilderLabels(labels):
    labelList = []
    if (not labels):
        jsonResponse = json.dumps(labelList)
    else:
        if isinstance(labels, list):
            for label in labels:
                labelObj = collections.OrderedDict()
                labelObj['id'] = label.id
                labelObj['title'] = label.title
                labelList.append(labelObj)
        else:
            labelObj = collections.OrderedDict()
            labelObj['id'] = labels.id
            labelObj['title'] = labels.title
            labelList.append(labelObj)

        jsonResponse = json.dumps(labelList)

    return jsonResponse


def jsonBuilderUsers(users):
    usersList = []
    if (not users):
        jsonResponse = json.dumps(usersList)
    else:
        if isinstance(users, list):
            for user in users:
                userObj = collections.OrderedDict()
                userObj['id'] = user.id
                userObj['username'] = user.username
                usersList.append(userObj)
        else:
            userObj = collections.OrderedDict()
            userObj['id'] = users.id
            userObj['username'] = users.username
            usersList.append(userObj)

        jsonResponse = json.dumps(usersList)

    return jsonResponse


def jsonBuilderIssues(issues):
    issuesList = []
    if(not issues):
        jsonResponse = json.dumps(issuesList)
    else:
        if isinstance(issues, list):
            for issue in issues:
                issueObj = collections.OrderedDict()
                issueObj['issueId'] = issue.id
                issueObj['createdDate'] = issue.create_date
                issueObj['closedDate'] = issue.close_date
                issueObj['status'] = issue.status
                issueObj['title'] = issue.title
                # what is first sorted by? Id? if yes then ok
                firstComment = Comment.query.filter_by(issue_id=issue.id, author_id=issue.author_id).first()
                if(firstComment):
                    description = firstComment.content[:50]
                else:
                    description = firstComment
                issueObj['description'] = description
                allComments = Comment.query.filter_by(issue_id=issue.id).count()
                actualComments = allComments - 1
                issueObj['commentCount'] = actualComments
                if (issue.milestone_id):
                    milestone = Milestone.query.get(issue.milestone_id)
                    issueObj['milestone'] = milestone.title
                else:
                    issueObj['milestone'] = issue.milestone_id
                author = User.query.get(issue.author_id)
                authorObj = collections.OrderedDict()
                authorObj['authorId'] = author.id
                authorObj['avatarURL'] = author.avatar_url
                authorObj['firstName'] = author.firstname
                authorObj['lastName'] = author.lastname
                authorObj['userName'] = author.username
                if (author.bio):
                    authorObj['bio'] = author.bio[:100]
                else:
                    authorObj['bio'] = author.bio
                authorObj['location'] = author.location
                authorObj['org'] = author.org
                authorObj['orgURL'] = author.org_url
                issueObj['author'] = authorObj
                labels = AssignedLabel.query.filter_by(issue_id=issue.id).all()
                labelslist = []
                if (labels):
                    for label in labels:
                        labelObj = collections.OrderedDict()
                        labelTitle = Label.query.get(label.label_id)
                        labelObj['labelId'] = label.label_id
                        labelObj['title'] = labelTitle.title
                        labelslist.append(labelObj)
                issueObj['labels'] = labelslist

                issuesList.append(issueObj)
        else:
            issueObj = collections.OrderedDict()
            issueObj['issueId'] = issues.id
            issueObj['createdDate'] = issues.create_date
            issueObj['closedDate'] = issues.close_date
            issueObj['status'] = issues.status
            issueObj['title'] = issues.title
            firstComment = Comment.query.filter_by(issue_id=issues.id, author_id=issues.author_id).first()
            if (firstComment):
                description = firstComment.content[:50]
            else:
                description = firstComment
            issueObj['description'] = description
            allComments = Comment.query.filter_by(issue_id=issues.id).count()
            actualComments = allComments - 1
            issueObj['commentCount'] = actualComments
            if (issues.milestone_id):
                milestone = Milestone.query.get(issues.milestone_id)
                issueObj['milestone'] = milestone.title
            else:
                issueObj['milestone'] = issues.milestone_id
            author = User.query.get(issues.author_id)
            authorObj = collections.OrderedDict()
            authorObj['authorId'] = author.id
            authorObj['avatarURL'] = author.avatar_url
            authorObj['firstName'] = author.firstname
            authorObj['lastName'] = author.lastname
            authorObj['userName'] = author.username
            if (author.bio):
                authorObj['bio'] = author.bio[:100]
            else:
                authorObj['bio'] = author.bio
            authorObj['location'] = author.location
            authorObj['org'] = author.org
            authorObj['orgURL'] = author.org_url
            issueObj['author'] = authorObj
            labels = AssignedLabel.query.filter_by(issue_id=issues.id).all()
            labelslist = []
            if (labels):
                for label in labels:
                    labelObj = collections.OrderedDict()
                    labelTitle = Label.query.get(label.label_id)
                    labelObj['labelId'] = label.label_id
                    labelObj['title'] = labelTitle.title
                    labelslist.append(labelObj)
            issueObj['labels'] = labelslist

            issuesList.append(issueObj)

    jsonResponse = json.dumps(issuesList)
    return jsonResponse

#routes
@app.route("/issues", methods= ['GET'])
@app.route('/issues/', methods = ['GET'])
def allIssues():
    #checks query string for usable queries
    label = request.args.get('label')
    status = request.args.get('status')
    if label:
        issues = Issue.query.join(AssignedLabel).filter(AssignedLabel.label_id == label).all()
    elif status:
        issues = Issue.query.filter_by(status=status.capitalize()).all()
    else:
        issues = Issue.query.all()

    response = jsonBuilderIssues(issues)

    return response

@app.route('/issues/<issueId>', methods = ['GET'])
def getIssue(issueId):
    issue = Issue.query.get(issueId)
    response = jsonBuilderIssues(issue)

    return response


@app.route('/issues/new/', methods = ['POST'])
def createIssue():
    responseStatus = 200
    message = []

    data = request.form
    d = data.to_dict()

    now = datetime.now()
    created_date = now.strftime("%m/%d/%Y")
    defaultStatus = "Open"
    #TODO refactor Issue model (no description id)
    descriptionIDDefault = 1
    #BUG ALERT: currently receiving selections twice, once as 'xxxSelection' once as 'xxx' - xxx holds selects but gets updated with actual selection
    #BUG ALERT: issue model still requires descriptionID so it's passed as default - actual description is retreived by query
    newIssue = Issue(create_date=created_date, status=defaultStatus, author_id=d['userSelection'], title=d['title'], milestone_id = d['milestoneSelection'], description_id= descriptionIDDefault)

    db.session.add(newIssue)
    db.session.commit()
    #if successful has ID
    if(newIssue.id):
        message.append("Issue was created")
        newComment = Comment(create_date=created_date,content = d['description'],author_id=d['userSelection'],issue_id = newIssue.id)
        db.session.add(newComment)
        db.session.commit()
        if not newComment.id:
            message.append("Comment was not created")
            responseStatus = 500
        else:
            message.append("Comment was created")
        if(d['labelsSelection']):
            newAssignedLabel = AssignedLabel(label_id= d['labelsSelection'],issue_id= newIssue.id)
            db.session.add(newAssignedLabel)
            db.session.commit()
            if not newAssignedLabel.id:
                message.append("Label assignment was not created")
                responseStatus = 500
            else:
                message.append("Label assignment was created")
    else:
        message.append("Issue was not created")
        responseStatus = 500

    message = ', '.join(message)
    responseMessage = {'message': message}

    return responseMessage, responseStatus

@app.route('/issues/delete/<int:issueId>', methods = ['POST'])
def deleteIssue(issueId):
    #no success message so trycatch
    failed = False
    try:
        Issue.query.filter_by(id=issueId).delete()
        Comment.query.filter_by(issue_id=issueId).delete()
        AssignedLabel.query.filter_by(issue_id=issueId).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        db.session.flush()
        failed = True

    if(not failed):
        responseStatus = 200
        responseMessage = {"message": "successfully deleted Issue" + str(issueId)}
    else:
        responseStatus = 500
        responseMessage = {"message": "Issue " + str(issueId) + " was not deleted"}

    return responseMessage,responseStatus


@app.route('/users/')
def allUsers():
    users = User.query.all()
    response = jsonBuilderUsers(users)

    return response

@app.route('/comments/')
def allComments():
    comments = Comment.query.all()
    commentExcerpts = []
    for comment in comments:
        commentExcerpts.append(comment.content[0:30])

    commentExcerptsStr = ' '.join(commentExcerpts)

    return commentExcerptsStr


@app.route('/labels/')
def allLabels():
    labels = Label.query.all()
    response = jsonBuilderLabels(labels)

    return response

@app.route('/assignedlabels/')
def allassignedLabels():
    assignedlabels = AssignedLabel.query.all()
    assignedlabelids = []
    for assignedlabel in assignedlabels:
        assignedlabelids.append(assignedlabel.label_id)

    assignedlabelidsStr = ' '.join(str(assignedlabelids))

    return assignedlabelidsStr

@app.route('/milestones/')
def allMilestones():
    milestones = Milestone.query.all()
    response = jsonBuilderMilestones(milestones)

    return response


if __name__ == "__main__":
    app.run(debug=True)