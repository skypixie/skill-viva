import datetime
from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

import support

from data import db_session
from data.users import User
from data.posts import Post
from data.categories import Category
from forms.login_form import LoginForm
from forms.registration_form import RegistrationForm
from forms.create_post import AddPostForm
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
    return db_sess.get(User, user_id)


# USER LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/posts')


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
            return redirect('/posts')
        
        # email not found or wrong password
        return render_template('login.html',
                               message='Неправильный логин или пароль',
                               form=form)
    return render_template('login.html',
                           form=form,
                           title='Авторизация')


# REGISTRATION
@app.route('/registrate', methods=['GET', 'POST'])
def registrate():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        # 2 passwords are identic
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   title='Регистрация',
                                   message='Пароли не совпадают',
                                   form=form)
        db_sess = db_session.create_session()

        # email is unique
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html',
                                   title='Регистрация',
                                   message='Такой email уже существует',
                                   form=form)
        
        if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template('register.html',
                                   title='Регистрация',
                                   message='Такой nickname уже существует',
                                   form=form)
        
        user.nickname = form.nickname.data
        user.email = form.email.data
        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()

        return redirect('/login')
        
    return render_template('register.html',
                           title='Регистрация',
                           form=form)


# PROFILE
@app.route('/profile/<string:nickname>')
@login_required
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
@login_required
def create_post():
    form = AddPostForm()

    if form.validate_on_submit():

        text_matcher = TextMatching(api_key='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',
                                    user_text=form.content.data,
                                    topic=form.category.data)
        
        # check via chat-gpt
        try:
            if text_matcher.matching().lower() == 'нет':
                return render_template('create_post.html',
                                       message='Текст не соответствует выбранной категории.',
                                       form=form)
        except Exception:
            pass

        db_sess = db_session.create_session()

        category_id = db_sess.query(Category).filter(Category.category == form.category.data).first().id

        new_post = Post(
            heading=form.heading.data,
            content=form.content.data,
            user=current_user,
            user_id=current_user.id,
            category_id=category_id
        )
        # current_user.posts.append(new_post) - вот так вот не работает
        # (sqlalchemy.orm.exc.DetachedInstanceError)

        db_sess.add(new_post)
        db_sess.commit()
        return redirect(f'/profile/{current_user.nickname}')

    return render_template('create_post.html',
                           title='New Post',
                           form=form)


# EDIT POST
@app.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    db_sess = db_session.create_session()
    post = db_sess.get(Post, id)
    if not post:
        return render_template('404.html')
    
    if current_user.id != post.user_id:
        return render_template('401.html',
                               title='401')
    
    form = AddPostForm()
    if form.validate_on_submit():
        text_matcher = TextMatching(api_key='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',
                                    user_text=form.content.data,
                                    topic=form.category.data)
        # check via chat-gpt
        try:
            if text_matcher.matching().lower() == 'нет':
                return render_template('create_post.html',
                                       message='Текст не соответствует выбранной категории.',
                                       form=form)
        except Exception:
            pass
        post.category_id = db_sess.query(Category).filter(Category.category == form.category.data).first().id
        post.heading = form.heading.data
        post.content = form.content.data
        db_sess.commit()
        
        return redirect('/posts')

    form.heading.data = post.heading
    form.content.data = post.content
    form.category.data = db_sess.query(Category).filter(Category.id == post.category_id).first().category

    return render_template('create_post.html',
                           form=form,
                           title='Edit post')


# DETAILED POST VIEW
@app.route('/posts/<int:id>')
@login_required
def post_detail(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).get(id)
    if not post:
        return render_template('404.html', title='404')
    
    return render_template('post_detail.html',
                           title=post.heading,
                           post=post)


# MAIN PAGE
@app.route('/')
@app.route('/posts')
def index():
    db_sess = db_session.create_session()
    all_posts = db_sess.query(Post).all()
    return render_template('main_screen.html',
                           posts=all_posts)


if __name__ == '__main__':
    db_session.global_init('db/database.db')

    # inserting all categories into the database
    support.insert_categories_into_db(db_session.create_session(),
                                      Category,
                                      CATEGORIES)
    app.run()
