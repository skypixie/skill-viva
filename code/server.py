import datetime
from flask import Flask, render_template, redirect, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

import support

from data import db_session
from data.users import User
from data.posts import Post
from data.categories import Category
from forms.login_form import LoginForm
# from forms.registration_form import RegistrationForm
from forms.create_post import AddPostForm
# еще не сделаны
from Text_Matching import TextMatching


app = Flask(__name__)
app.config['SECRET_KEY'] = 'liusEbvsdjvimglitching123jskebv'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)

login_manager = LoginManager(app)
login_manager.init_app(app)

BASE_CSS_FILES = ['main_style']
CATEGORIES = [
        'Программирование',
        'Дизайн',
        'Английский язык',
        'Наука',
        'Финансы',
        'Маркетинг',
        'Юриспруденция',
    ]


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# USER LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        # password check
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        
        # email not found or wrong password
        return render_template('login.html',
                               message='Неправильный логин или пароль',
                               form=form,
                               css_files=BASE_CSS_FILES)
    return render_template('login.html',
                           form=form,
                           title='Авторизация',
                           css_files=BASE_CSS_FILES + ['login'])


# REGISTRATION
app.route('/registrate', methods=['GET', 'POST'])
def registrate():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        # 2 passwords are identic
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   message='Пароли не совпадают')
        db_sess = db_session.create_session()

        # email is unique
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   message='Такой пользователь уже существует')
        
        user.nickname = form.nickname.data
        user.email = form.email.data
        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()

        return redirect('/login')
        
    return render_template('registration.html',
                           title='Регистрация',
                           form=form)


# PROFILE
@app.route('/profile/<string:nickname>')
def profile(nickname):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.nickname == nickname).first()
    if not user:
        return render_template('404.html', title='404')
    return render_template('profile_view.html',
                           title=f'@{nickname}',
                           user=user)


# CREATE A POST
@app.route('/new_post', methods=['GET', 'POST'])
def create_post():
    form = AddPostForm(categories=CATEGORIES)
    if form.validate_on_submit():
        text_matcher = TextMatching(api_key='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',
                                    user_text=form.content.data,
                                    topic=form.category.data)
        
        # check via chat-gpt
        if text_matcher.matching().lower() == 'нет':
            return render_template('create_post.html',
                                   message='Текст не соответствует выбранной категории.')
        db_sess = db_session.create_session()

        new_post = Post()
        new_post.heading = form.heading.data
        new_post.content = form.content.data
        current_user.posts.append(new_post)
        
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(f'/profile/{current_user.nickname}')

    return render_template('create_post.html',
                           title='New Post',
                           form=form)


@app.route('/posts')
def main():
    db_sess = db_session.create_session()
    all_posts = db_sess.query(Post).all()
    return render_template('main_screen.html',
                           css_files=BASE_CSS_FILES + ['main_screen_style'],
                           posts=all_posts)


if __name__ == '__main__':
    db_session.global_init('db/database.db')

    # inserting all categories into the database
    support.insert_categories_into_db(db_session.create_session(),
                                      Category,
                                      CATEGORIES)
    app.run()
