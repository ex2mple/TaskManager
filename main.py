from flask import Flask, render_template, redirect, url_for, flash, request
from flask_socketio import SocketIO, send, emit
from flask_login import LoginManager, current_user, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from forms import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
app.app_context().push()
login_manager = LoginManager(app)
login_manager.login_view = 'login'
socket = SocketIO(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    task_text = db.Column(db.Text)
    deadline = db.Column(db.String(30))


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(30))
    surname = db.Column(db.String(30))
    birthday = db.Column(db.String(30))
    family_status = db.Column(db.String(30), default='не указано')
    education = db.Column(db.String(255), default='не указано')
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.Integer)
    direction = db.Column(db.Integer)
    people = db.relationship('User', backref='staff')


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    author = db.relationship('User', backref=db.backref('messages', lazy=True))


db.create_all()


@socket.on('message')
def handle_message(data):
    emit('message', data, broadcast=True)


@socket.on('send_message')
def handle_send_message_event(data):
    message = data['message']
    username = current_user.login
    user = current_user
    new_message = Message(text=message, author=user)
    db.session.add(new_message)
    db.session.commit()
    emit('message', {'username': username, 'message': message}, broadcast=True)


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    tasks_list = Task.query.all()
    return render_template(
        'index.html', tasks=tasks_list
    )


@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():

    form = ChatForm()
    if form.validate_on_submit():
        message = Message()
        message.author = current_user
        message.text = form.message.data
        db.session.add(message)
        db.session.commit()
        socket.emit('message', {'username': current_user.login, 'message': form.message.data})
        form.message.data = ''

    messages = Message.query.order_by(Message.timestamp.desc()).all()[::-1]

    return render_template(
        'chat.html', form=form, messages=messages, current_user=current_user
    )


@app.route('/employees', methods=['GET', 'POST'])
@login_required
def employees():
    return render_template(
        'employees.html'
    )


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template(
        'profile.html', user=current_user
    )


@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        try:
            task = Task()
            task.name = form.name.data
            task.task_text = form.task.data
            task.deadline = form.deadline.data.strftime("%d %B")
            db.session.add(task)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception:
            return redirect(url_for('index'))
    return render_template(
        'add_task.html', form=form
    )


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = SignupForm()
    if form.validate_on_submit():
        try:
            user = User()
            user.login = form.login.data
            user.set_password(form.password.data)
            user.name = form.name.data
            user.surname = form.surname.data
            user.birthday = form.birthday.data.strftime("%d.%m.%Y")
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception:
            flash("Произошла ошибка! Попробуйте еще раз", 'error')
            return redirect(url_for('sign_up'))
    return render_template('login_signup.html', form=form, fields=list(form)[:-2])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))
        flash("Неверный логин или пароль!", 'error')
        return redirect(url_for('login'))
    return render_template('login_signup.html', form=form, fields=list(form)[:-3])


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы!")
    return redirect(url_for('login'))


if __name__ == '__main__':
    socket.run(app, debug=True, allow_unsafe_werkzeug=True)
