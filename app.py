from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from helpers import apology, login_required, get_date
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:contraseña@localhost/nombre_de_la_base_de_datos'
db = SQLAlchemy(app)
Session(app)

PILOTS = ["Verstappen", "Pérez", "Sainz", "Leclerc", "Alonso", "Stroll", "Hamilton", "Russell", "Norris", "Piastri", "Ricciardo", "Tsunoda", "Bottas", "Zhou", "Hulkenberg", "Magnussen", "Ocon", "Gasly", "Albon", "Sargeant"]
TEAMS = ["Red Bull", "Ferrari", "Aston Martin", "Mercedes", "McLaren", "Visa CashApp", "Kick Sauber", "Hass", "Alpine", "Williams"]

@app.route("/", methods=["POST", "GET"])
@login_required
def predicciones():
	if request.method == "POST":
		circuit = request.form.get("circuit")
		img = request.form.get("img")
		race_date = request.form.get("race_date")
		race_time = request.form.get("race_time")
		qualy_date = request.form.get("qualy_date")
		qualy_time = request.form.get("qualy_time")

		return render_template("select.html", circuit=circuit, img=img, race_date=race_date, race_time=race_time, qualy_date=qualy_date, qualy_time=qualy_time)
	if request.method == "GET":
		user = session["user_id"]
		races = db.execute("SELECT * FROM races")
		return render_template("predicciones.html", races=races, user=user)
	
@app.route("/select", methods=["GET", "POST"])
@login_required
def select():
	if request.method =="POST":
		circuit = request.form.get("circuit")
		sessionType = request.form.get("session")
		race_date = request.form.get("race_date")
		race_time = request.form.get("race_time")
		qualy_date = request.form.get("qualy_date")
		qualy_time = request.form.get("qualy_time")

		predicciones = db.execute("SELECT * FROM predictions WHERE race=? AND type=? AND user=?", circuit, sessionType, session["user_id"])

		return render_template("predecir.html", circuit=circuit, sessionType=sessionType, teams=TEAMS, pilots=PILOTS, race_date=race_date, race_time=race_time, qualy_date=qualy_date, qualy_time=qualy_time, predicciones=predicciones)
	if request.method == "GET":
		return render_template("select.html")
	
@app.route("/predecir", methods=["GET", "POST"])
@login_required
def predecir():
	if request.method == "POST":
		circuit = request.form.get("circuit")
		sessionType = request.form.get("sessionType")
		top1 = request.form.get("top1")
		top2 = request.form.get("top2")
		top3 = request.form.get("top3")
		top4 = request.form.get("top4")
		top5 = request.form.get("top5")

		toplist = [top1, top2, top3, top4, top5]
		topset = set(toplist)

		if len(toplist) != len(topset):
			return apology("Pilotos repetidos")
		
		today = datetime.now()

		if sessionType == "race":
			team = request.form.get("team")
			race_date = request.form.get("race_date")
			race_time = request.form.get("race_time")
			race_datetime = get_date(race_date, race_time)
			

			if today > race_datetime:
				return apology("Fecha límite superada")
			if db.execute("SELECT * FROM predictions WHERE user=? AND race=? AND type=?", session["user_id"], circuit, sessionType):
				db.execute("DELETE FROM predictions WHERE user=? AND race=? AND type=?", session["user_id"], circuit, sessionType)

			db.execute("INSERT INTO predictions (user, race, type, top1, top2, top3, top4, top5, escuderia) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], circuit, sessionType, top1, top2, top3, top4, top5, team)
		else:
			qualy_date = request.form.get("qualy_date")
			qualy_time = request.form.get("qualy_time")
			qualy_datetime = get_date(qualy_date, qualy_time)
			today = datetime.now()

			if today > qualy_datetime:
				return apology("Fecha límite superada")
			
			if db.execute("SELECT * FROM predictions WHERE user=? AND race=? AND type=?", session["user_id"], circuit, sessionType):
				db.execute("DELETE FROM predictions WHERE user=? AND race=? AND type=?", session["user_id"], circuit, sessionType)
			
			db.execute("INSERT INTO predictions (user, race, type, top1, top2, top3, top4, top5) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], circuit, sessionType, top1, top2, top3, top4, top5)
		
		return redirect("/")

	if request.method == "GET":
		return render_template("predecir.html")
	
@app.route("/ranking")
@login_required
def ranking():
	users = db.execute("SELECT user, points FROM users ORDER BY points DESC")
	return render_template("ranking.html", users=users)

@app.route("/resultados", methods=["POST", "GET"])
@login_required
def resultados():
	if request.method == "POST":
		circuit = request.form.get("race")
		sessionType = request.form.get("session")
		top1 = request.form.get("top1")
		top2 = request.form.get("top2")
		top3 = request.form.get("top3")
		top4 = request.form.get("top4")
		top5 = request.form.get("top5")

		toplist = [top1, top2, top3, top4, top5]
		topset = set(toplist)

		if len(toplist) != len(topset):
			return apology("Pilotos repetidos")
		
		team = request.form.get("team")
		
		if not team:
			if sessionType == "race":
				return apology("Carrera necesita escudería")
			if db.execute("SELECT * FROM results WHERE user=? AND race=? AND type=?", session["user_id"], circuit, sessionType):
				db.execute("DELETE FROM results WHERE user=? AND race=? AND type=?", session["user_id"], circuit, sessionType)
			
			db.execute("INSERT INTO results (user, race, type, top1, top2, top3, top4, top5) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], circuit, sessionType, top1, top2, top3, top4, top5)
		else:
			if sessionType == "qualy":
				return apology("Clasificación no tiene escudería")
			if db.execute("SELECT * FROM results WHERE user=? AND race=? AND type=?", session["user_id"], circuit, sessionType):
				db.execute("DELETE FROM results WHERE user=? AND race=? AND type=?", session["user_id"], circuit, sessionType)
				
			db.execute("INSERT INTO results (user, race, type, top1, top2, top3, top4, top5, escuderia) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], circuit, sessionType, top1, top2, top3, top4, top5, team)
			

		predictions = db.execute("SELECT * FROM predictions WHERE race=? AND type=?", circuit, sessionType)

		for prediction in predictions:
			points = 0
			ptoplist = []
			ptoplist.append(prediction["top1"])
			ptoplist.append(prediction["top2"])
			ptoplist.append(prediction["top3"])
			ptoplist.append(prediction["top4"])
			ptoplist.append(prediction["top5"])

			for i in range(5):
				for j in range(5):
					if ptoplist[i] == toplist[j]:
						if i == j:
							points += 3
							break
						else:
							points += 1
							break
			
			if prediction["type"] == "race":
				if prediction["escuderia"] == team:
					points += 2

			if db.execute("SELECT * FROM points WHERE user=? AND race=? AND type=?", prediction["user"], circuit, sessionType):
				db.execute("DELETE FROM points WHERE user=? AND race=? AND type=?", prediction["user"], circuit, sessionType)

			db.execute("INSERT INTO points (number, user, race, type) VALUES(?, ?, ?, ?)", points, prediction["user"], circuit, sessionType)

			new_points = 0
			pointlist = db.execute("SELECT number FROM points WHERE user=?", prediction["user"])
			for plist in pointlist:
				new_points += int(plist["number"])
			usr = int(prediction["user"])
			db.execute("UPDATE users SET points=? WHERE id=?", new_points, usr)
		return redirect("/")
	if request.method == "GET":
		circuits = db.execute("SELECT circuit FROM races")
		return render_template("resultados.html", circuits=circuits, pilots=PILOTS, teams=TEAMS)
	
@app.route("/ver_resultados")
@login_required
def ver_resultados():
	resultados = db.execute("SELECT * FROM results")
	circuitos = db.execute("SELECT circuit FROM races")
	return render_template("ver_resultados.html", resultados=resultados, circuitos=circuitos)


@app.route("/login", methods=["POST", "GET"])
def login():
	session.clear()

	if request.method == "POST":
		user = request.form.get("user")
		if not user:
			return apology("You must enter a username")
		password = request.form.get("password")
		if not password:
			return apology("You must enter a password")

		rows = db.execute("SELECT * FROM users WHERE user = ?", request.form.get("user"))

		if len(rows) != 1:
			return apology("invalid username and or password", 1)
		if request.form.get("password") != rows[0]["password"]:
			return apology("invalid username and/or password", 2)

		session["user_id"] = rows[0]["id"]

		return redirect("/")

	if request.method == "GET":
		return render_template("login.html")

@app.route("/logout")
def logout():
	session.clear()
	
	return redirect("/")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)