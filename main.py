from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os


API_KEY = os.environ["API_KEY"]
TOKEN = os.environ["TOKEN"]

URL = "https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
bootstrap = Bootstrap(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


class Edit(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")


@app.route("/edit/", methods=["GET", "POST"])
def edit():
    form = Edit()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", movie=movie, form=form)


@app.route("/del")
def delete():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


class FindMovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


@app.route("/add", methods=["GET", "POST"])
def add():
    form = FindMovieForm()

    if form.validate_on_submit():
        url = "https://api.themoviedb.org/3/search/movie?include_adult=true&language=en-US&page=1"

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzYmM2MDkyNzE3YmVlZGMzYTA1ZTRkMDgwOTQzNWVmMiIsInN1YiI6IjY0N2RlY2QyMTc0OTczMDExODcyMjg1NiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.EOYP4kGpZTPMGs-XbxE2-KKA7AWKsgOQmcZ1tL9P1rw"
        }
        params = {
            "query": f"{form.title.data}"
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()["results"]

        return render_template("select.html", data=data)

    return render_template("add.html", form=form)


@app.route("/add_movie")
def add_movie():
    movie_title = request.args.get("movie_title")
    poster_path = request.args.get("poster_path")
    release_date = request.args.get("release_date")
    overview = request.args.get("overview")

    new_movie = Movie(
        title=movie_title,
        img_url=f"https://image.tmdb.org/t/p/w500/{poster_path}",
        year=release_date,
        description=overview,
    )

    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for("edit", id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
