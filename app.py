from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'titkos_kulcs'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rss_feed.db'
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(60), nullable = False)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)

with app.app_context():
     db.create_all()

@app.route('/', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
          user = User.query.filter_by(email = request.form.get('email')).first()
          if user and bcrypt.check_password_hash(user.password, request.form.get('password')):
              login_user(user)
              return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        hashed_password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
        new_user = User(username = request.form.get('username'), email = request.form.get('email'), password = hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/home')
def home():
    feeds = Feed.query.all()
    return render_template('home.html', feeds = feeds)

@app.route('/create_feed', methods=['GET', 'POST'])
@login_required
def create_feed():
    if request.method == 'POST':
        name = request.form.get('name')
        age = int(request.form.get('age'))
        country = request.form.get('country')
        city = request.form.get('city')
        
        new_feed = Feed(name=name, age=age, country=country, city=city)
        db.session.add(new_feed)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create.html')

@app.route('/edit_feed/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_feed(id):
    feed = Feed.query.get(id)
    
    if request.method == 'POST':
        feed.name = request.form.get('name')
        feed.age = int(request.form.get('age')) 
        feed.country = request.form.get('country')
        feed.city = request.form.get('city')
        
        db.session.commit()
        return redirect(url_for('home'))
    
    return render_template('edit.html', feed=feed)

@app.route('/delete_feed/<int:id>', methods=['POST'])
@login_required
def delete_feed(id):
    feed = Feed.query.get(id)
    db.session.delete(feed)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)