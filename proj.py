from flask import Flask, render_template, redirect
from school_distant.data import db_session
from school_distant.data.users import User
from school_distant.data.test import Tests
from school_distant.data.tasks import Tasks
from school_distant.data.form import RegisterForm, LoginForm, TestsForm, TasksForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

db_session.global_init("db/school.sqlite")
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
COUNT_OF_OTHER_QUESTIONS = 0


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route("/")
@app.route("/school")
def index():
    session = db_session.create_session()
    test = session.query(Tests)
    return render_template("school.html", test=test)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration.html', title='Регистрация', form=form, message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('registration.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(name=form.name.data, email=form.email.data, clas=form.clas.data, occupation=form.occupation.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/school")
        return render_template('log_in.html', message="Неправильный логин или пароль", form=form)
    return render_template('log_in.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/school")


@app.route('/test', methods=['GET', 'POST'])
@login_required
def add_tests():
    global COUNT_OF_OTHER_QUESTIONS
    form = TestsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        tests = Tests()
        tests.title = form.title.data
        tests.subject = form.subject.data
        tests.count_of_questions = form.count_of_questions.data
        tests.user_id = form.user_id.data
        current_user.tests.append(tests)
        session.merge(current_user)
        session.commit()
        COUNT_OF_OTHER_QUESTIONS = int(form.count_of_questions.data)
        return redirect('/task')
    return render_template('tests.html', title='Добавление теста', form=form)


@app.route('/task', methods=['GET', 'POST'])
@login_required
def add_tasks():
    global COUNT_OF_OTHER_QUESTIONS
    form = TasksForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        tasks = Tasks()
        tasks.title = form.title.data
        tasks.ans1 = form.ans1.data
        tasks.ans2 = form.ans2.data
        tasks.ans3 = form.ans3.data
        tasks.ans4 = form.ans4.data
        tasks.correct_answer = form.correct_answer.data
        session.add(tasks)
        session.commit()
        if COUNT_OF_OTHER_QUESTIONS > 0:
            COUNT_OF_OTHER_QUESTIONS -= 1
            return redirect('/task')
        else:
            return redirect('/school')
    return render_template('task.html', title='Добавление вопроса', form=form)


@app.route('/tests_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    session = db_session.create_session()
    news = session.query(Tests).filter(Tests.id == id, Tests.user == current_user).first()
    if news:
        session.delete(news)
        session.commit()
    else:
        abort(404)
    return redirect('/school')


if __name__ == '__main__':
    app.run(port=8082, host='127.0.0.1')
