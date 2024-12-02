from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from models import User, League, Team, Player, db

# note: hash does not work for xxamp (password length exceed)
bcrypt = Bcrypt()

views =Blueprint(__name__, "views")

#landing page
@views.route("/")
def landing():
    return render_template("landing.html")


#login
@views.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        #query DB for the user
        user = User.query.filter_by(username = username).first()

        #verify the login attempt
        if user and bcrypt.check_password_hash(user.password, password):
            session["user"] = username
            return redirect(url_for("views.dashboard"))

        flash("Invalid username or password!", "error")
        return redirect(url_for("views.login"))

    return render_template("login.html")




#registration
@views.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        name = request.form["name"]  # not required (can be null)
        email = request.form["email"]

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken, please select a different username.", "error")
            return redirect(url_for("views.register"))

        # Check if the email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email already registered. Please use a different email.", "error")
            return redirect(url_for("views.register"))

        # Hash the password and save the user
        # hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(name=name, email=email, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("views.login"))

    return render_template("register.html")


#dashboard
@views.route("/dashboard")
def dashboard():
    if "user" in session:  # Check if the user is logged in
        username = session["user"]

        # Fetch general statistics from the database=
        team_count = Team.query.count()  # Count of teams
        league_count = League.query.count()  # Count of leagues
        player_count = Player.query.count()  # Count of matches

        # Pass the statistics to the template
        return render_template("dashboard.html",
                               username=username,
                               team_count=team_count,
                               league_count=league_count,
                               player_count=player_count)

    flash("You need to log in to access this page.", "error")
    return redirect(url_for("views.login"))


# Users
@views.route("/users")
def users():
    if "user" not in session:
        flash("You need to log in to access this page.", "error")
        return redirect(url_for("views.login"))
    return render_template("users.html")


# League
@views.route("/league")
def league():
    if "user" not in session:
        flash("You need to log in to access this page.", "error")
        return redirect(url_for("views.login"))
    return render_template("league.html")


# Teams
@views.route("/teams", methods=["GET", "POST"])
def teams():
    if "user" not in session:
        flash("You need to log in to access this page.", "error")
        return redirect(url_for("views.login"))

    # Handle adding a new team
    if request.method == "POST":
        team_name = request.form.get("team_name")
        owner = request.form.get("owner")
        league_id = request.form.get("league_id")
        total_points = request.form.get("points")
        ranking = request.form.get("ranking")
        status_value = request.form.get("status")

        # Convert the checkbox value to 'a' for active or 'i' for inactive
        if status_value == 'on':
            status = 'A'
        else:
            status = 'I'

        if not team_name or not owner or not league_id:
            flash("Team Name, Owner, and League ID are required.", "error")
            return redirect(url_for("views.teams"))

        new_team = Team(
            TeamName=team_name,
            Owner=owner,
            League_ID=league_id,
            TotalPoints=total_points,
            Ranking=ranking,
            Status=status,
        )
        db.session.add(new_team)
        db.session.commit()
        flash("Team added successfully!", "success")
        return redirect(url_for("views.teams"))

    # Search/Filter Teams
    search_query = request.args.get('search', '').strip()

    #  filter teams by name
    if search_query:
        teams = Team.query.filter(Team.TeamName.ilike(f'%{search_query}%')).all()
    else:
        teams = Team.query.all()  # No search, return all teams

    return render_template('teams.html', teams=teams)

@views.route("/teams/edit", methods=["POST"])
def edit_team():
    if "user" not in session:
        flash("You need to log in to access this page.", "error")
        return redirect(url_for("views.login"))

    # Handle editing the team
    team_id = request.form.get("team_id")
    team_name = request.form.get("team_name")
    owner = request.form.get("owner")
    league_id = request.form.get("league_id")
    total_points = request.form.get("points")
    ranking = request.form.get("ranking")
    status_value = request.form.get("status")  # Expect either 'A' or 'I'

    if status_value == 'A':
        status = 'A'
    else:
        status = 'I'

    team = Team.query.get_or_404(team_id)
    team.TeamName = team_name
    team.Owner = owner
    team.League_ID = league_id
    team.TotalPoints = total_points
    team.Ranking = ranking
    team.Status = status

    db.session.commit()
    flash("Team updated successfully!", "success")
    return redirect(url_for("views.teams"))



@views.route("/teams/delete/<int:id>", methods=["POST"])
def delete_team(id):
    if "user" not in session:
        flash("You need to log in to access this page.", "error")
        return redirect(url_for("views.login"))

    team = Team.query.get_or_404(id)
    db.session.delete(team)
    db.session.commit()
    flash("Team deleted successfully!", "success")
    return redirect(url_for("views.teams"))


#logout
@views.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out. Have a good day!", "success")
    return redirect(url_for("views.login"))



