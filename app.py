import os
from flask import Flask, render_template, session, url_for, redirect, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime



app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)


app.config['SECRET_KEY'] = 'hard to guess string'

# Database setup
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')
    
    def __repr__(self):
        return '<Role %r>' % self.name
    
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    
    def __repr__(self):
        return '<User %r>' % self.username

class NameForm(FlaskForm):
    name = StringField('What is your name', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html',
                           current_time=datetime.utcnow(),
                           form=form,
                           name=session.get('name'),
                           known=session.get('known', False))
    
    
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)






