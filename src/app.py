from flask import Flask, render_template, jsonify, request
from database import load_tours_from_db, load_tour_from_db, add_booking_to_db

app = Flask(__name__)


# @app.route("/")
# def Home():
#   tours = load_from_db()
#   print(tours)
#   return render_template("index.html", records=tours)

@app.route("/")
def Home():
  tours = load_tours_from_db()
  print(tours)
  return render_template('home.html', 
                         tours=tours)
# sdf test
@app.route("/tour/<id>")
def show_tour(id):
  tour = load_tour_from_db(id)
  print(tour)
  if not tour:
    return "Not Found", 404
  
  return render_template('tour_page.html', 
                         tour=tour)

@app.route("/tour/<id>/book", methods=['post'])
def book_tour(id):
  data = request.form
  tour = load_tour_from_db(id)
  add_booking_to_db(id, data)
  return render_template('application_submitted.html', 
                         application=data,
                         tour=tour)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port='8080')