from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, DateField
from wtforms.validators import DataRequired, Optional


class TaskForm(FlaskForm):
    name = StringField(
        'Для кого:', validators=[DataRequired()]
    )
    task = TextAreaField(
        'Текст задания:', validators=[DataRequired()]
    )
    deadline = DateField(
        'Дата окончания:', validators=[DataRequired()]
    )
    submit = SubmitField('Добавить')


class ChatForm(FlaskForm):
    message = StringField(validators=[DataRequired()])
    submit = SubmitField('Отправить')


class LoginForm(FlaskForm):
    action = 'Авторизация'
    login = StringField(
        'Введите логин', validators=[DataRequired()]
    )
    password = PasswordField(
        'Введите пароль', validators=[DataRequired()]
    )
    remember = BooleanField("Запомнить меня")
    submit = SubmitField('Войти')


class SignupForm(LoginForm):
    action = 'Регистрация'
    remember = None
    name = StringField(
        'Ваше имя', validators=[DataRequired()]
    )
    surname = StringField(
        'Ваша фамилия', validators=[DataRequired()]
    )
    birthday = DateField(
        'Дата рождения', validators=[DataRequired()]
    )
    submit = SubmitField('Зарегистрироваться')
