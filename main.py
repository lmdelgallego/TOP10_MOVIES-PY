import os
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired
import requests

MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_API_KEY = os.environ.get("API_KEY")  # your API key here

app = Flask(__name__)
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()

db.init_app(app)
Bootstrap(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'


class EditForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Done")


class AddForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    # year = StringField("Year", validators=[DataRequired()])
    # description = StringField("Description", validators=[DataRequired()])
    # rating = FloatField("Rating", validators=[DataRequired()])
    # ranking = IntegerField("Ranking", validators=[DataRequired()])
    # review = StringField("Review", validators=[DataRequired()])
    # img_url = StringField("Image Url", validators=[DataRequired()])
    submit = SubmitField("Add Movie")

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    all_movies = Movie.query.all()
    return render_template("index.html", movies=all_movies)

@app.route("/update", methods=["GET", "POST"])
def update():
    form = EditForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", movie=movie, form=form)


@app.route('/add', methods=["GET", "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(MOVIE_DB_SEARCH_URL, params={"api_key": MOVIE_DB_API_KEY, "query": movie_title})
        data = response.json()["results"]
        if len(data) > 0:
            return render_template("select.html", options=data)
        # new_movie = Movie(
        #     title=form.title.data,
        #     year=form.year.data,
        #     description=form.description.data,
        #     rating=form.rating.data,
        #     ranking=form.ranking.data,
        #     review=form.review.data,
        #     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
        # )
        # db.session.add(new_movie)
        # db.session.commit()
        return redirect(url_for("home"))

    return render_template("add.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)
