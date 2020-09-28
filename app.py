from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import sys
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your email'
app.config['MAIL_PASSWORD'] = '******'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'your database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
mail = Mail(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<Users {self.id} {self.name} {self.email}>'


db.create_all()


@app.route('/users/sendEmail', methods=['POST'])
def send_email():
    userId = request.get_json()['userId']

    for id in userId:
        recipients = []
        if id is None:
            continue
        user = Users.query.get(id)
        recipients.append(user.email)
        msg = Message('Hello', sender='sender email', recipients=recipients)
        msg.body = "Hello, " + user.name + "  Thank you for your interest and we will contact you soon stay tuned "
        mail.send(msg)

    return redirect(url_for('index'))


@app.route('/users/<user_id>', methods=['DELETE'])
def delete_todo(user_id):
    try:

        user = Users.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return jsonify({'success': True})


@app.route('/users/create', methods=['Post'])
def create_user():
    error = False
    body = {}
    try:
        name = request.get_json()['name']
        email = request.get_json()['email']

        user = Users(name=name, email=email)
        db.session.add(user)
        db.session.commit()

        body['name'] = user.name
        body['email'] = user.email
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(body)


@app.route('/users')
def get_list_users():
    return render_template('index.html', users=Users.query.all())


@app.route('/')
def index():
    return redirect(url_for('get_list_users'))
