from flask import Flask, jsonify, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required

app = Flask(__name__)

API = "SecretAPIKey"
app.config["SECRET_KEY"] = "şwlmefsgdptme4r23pqo"

#Login User
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# Create DB
class Base(DeclarativeBase):
    pass

# Connect Databse
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

#TABLE
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)
    
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/all-cafes', methods=['GET', 'POST'])
def all_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    if all_cafes:
        cafe_list = [cafe.to_dict() for cafe in all_cafes]
        return render_template('./allcafes.html', cafe_list=cafe_list)
    else:
        return jsonify(error={'Not Found': 'Sorry, the data could not be found.'})
    
@app.route('/add-cafe', methods=['POST', 'GET'])
@login_required
def add_cafe():

    if request.method == 'GET':
        return render_template('add-cafe.html')
    elif request.method == 'POST':
        new_cafe = Cafe(
           name=request.form.get('cafe-name'),
                map_url=request.form.get('map-url'),
                img_url=request.form.get('img-url'),
                location=request.form.get('location'),
                seats=request.form.get('seats'), 
                has_toilet=request.form.get('has-toilet') == '1',
                has_wifi=request.form.get('has-wifi') == '1',
                has_sockets=request.form.get('has-sockets') == '1',
                can_take_calls=request.form.get('can-take-calls') == '1',
                coffee_price=request.form.get('coffee-price')
        )
        
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('all_cafes'))

@app.route('/delete/<int:cafe_id>')
@login_required
def delete_cafe(cafe_id):
    cafe_to_delete = db.get_or_404(Cafe, cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('all_cafes'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=username).first()

        if user and user.password == password:
            login_user(user)
            return redirect(url_for("index"))
        else:
            return jsonify({'Wrong password': 'Your password is incorrect'})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('./register.html')
    elif request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password-confirm')
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if user:
            return jsonify({'User Exists': 'This user already exists.'})
        elif password != password_confirm:
            return jsonify({'Password Error': 'Passwords do not match.'})
        else:
            new_user = User(
                email = email,
                password = password
            )
            db.session.add(new_user)
            db.session.commit()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()