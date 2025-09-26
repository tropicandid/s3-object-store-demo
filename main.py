from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from flask_bcrypt import Bcrypt
import boto3
import uuid

########################## CONFIGURE S3 and DB ##########################
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


db = SQLAlchemy()
app = Flask(__name__)
#TODO: Move to env variables.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SECRET_KEY'] = '5R8bLa420ufMpd34'
db.init_app(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

########################## MODELS ##########################
# TODO: Move out into models directory
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    organization = db.Column(db.String(120), nullable=False)
    roles    = db.Column(db.String(120))
# TODO: Move out into models directory
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(100))
    filename = db.Column(db.String(100))
    bucket = db.Column(db.String(100))
    user = db.Column(db.Integer)
    organization = db.Column(db.String(120), nullable=False)
# TODO: Create an organization model & Action History Model. These are hard coded for now.

########################## FORMS ##########################
class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    print(username)

    #@staticmethod
    # def validate_username(username):
    #     existing_user_username = User.query.filter_by(
    #         username=username.data).first()
    #     if existing_user_username:
    #         raise ValidationError(
    #             'Username already exists. Please choose a different one.')
class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

########################## ROUTING LOGIC ##########################
#TODO: This also needs to be moved into it's own directory
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))  # Redirect if already logged in

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/new-user', methods=['GET', 'POST'])
def new_user():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_password, roles='editor', organization="Bacon Unlimited")
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('new_user.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == "POST":
        #TODO: Could add in file type limiter if needed like preventing .sql files
        uploaded_file = request.files["file-to-save"]
        new_filename = uuid.uuid4().hex + '.' + uploaded_file.filename.rsplit('.', 1)[1].lower()
        bucket_name = "s3-object-store-demo"
        s3 = boto3.client("s3")
        s3.upload_fileobj(
            uploaded_file,
            bucket_name,
            new_filename
        )

        file = File(original_filename=uploaded_file.filename, filename=new_filename,
                    bucket=bucket_name, user=current_user.id, organization=current_user.organization)

        db.session.add(file)
        db.session.commit()
        return redirect(url_for("dashboard"))

    files = db.session.query(File).filter(File.organization == current_user.organization)
    print(files)
    return render_template('dashboard.html',
                           user=current_user,
                           files=files)

# TODO: Create initializer that checks if db file exists and if not create schema.
########################## INSTANTIATE ##########################
if __name__ == '__main__':
    app.run(debug=True)