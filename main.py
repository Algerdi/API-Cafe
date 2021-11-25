from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
from sqlalchemy.sql.expression import func

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    random_cafe = db.session.query(Cafe).order_by(func.random()).first()
    r_c_json = dict(random_cafe.__dict__)
    print(r_c_json)
    del r_c_json["_sa_instance_state"]
    return jsonify(cafe=r_c_json)


@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    all_cafes = []
    for cafe in cafes:
        elem = dict(cafe.__dict__)
        del elem["_sa_instance_state"]
        all_cafes.append(elem)
    return jsonify(cafes=all_cafes)


@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    cafes = db.session.query(Cafe).filter_by(location=query_location).all()
    if cafes:
        s_cafes = []
        for cafe in cafes:
            elem = dict(cafe.__dict__)
            del elem["_sa_instance_state"]
            s_cafes.append(elem)
        return jsonify(cafe=s_cafes)
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.args.get("name"),
        map_url=request.args.get("map_url"),
        img_url=request.args.get("img_url"),
        location=request.args.get("loc"),
        has_sockets=bool(int(request.args.get("sockets"))),
        has_toilet=bool(int(request.args.get("toilet"))),
        has_wifi=bool(int(request.args.get("wifi"))),
        can_take_calls=bool(int(request.args.get("calls"))),
        seats=request.args.get("seats"),
        coffee_price=request.args.get("coffee_price"),
    )
    # http://127.0.0.1:5000/add?name=Hinki&map_url=https://g.page/Dominos_Dzerzhinskogo?share&img_url=https://berkeley-gif.github.io/caladapt-docs/_images/restapi_model.png&loc=Brest&sockets=1&toilet=1&wifi=1&calls=0&seats=30&coffee_price=3
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": f"Successfully updated the price. Now it costs {new_price}"})
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    # http://127.0.0.1:5000/report-closed/24?api-key=saskevmaske
    if api_key == "saskevmaske":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

## HTTP GET - Read Record


## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)


