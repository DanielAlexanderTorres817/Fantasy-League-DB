from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from models import User, League, Team, Player, PlayerStatistics, db, update_team_ranking

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
@views.route("/league", methods=["GET", "POST"])
def league():
    if "user" not in session:
        flash("You need to log in to access this page.", "error")
        return redirect(url_for("views.login"))

    comm = User.query.filter_by(username=session["user"]).first()

    # Handle adding a new league
    if request.method == "POST":
        league_name = request.form.get("league_name")
        league_type = request.form.get("league_type")
        max_teams = request.form.get("max_teams")
        draft_date = request.form.get("draft_date")

        # Convert the checkbox value to 'a' for active or 'i' for inactive
        if league_type == 'on':
            league_type = 'P'
        else:
            league_type = 'R'

        if not league_name:
            flash("League Name is required.", "error")
            return redirect(url_for("views.league"))

        new_league = League(
            LeagueName=league_name,
            LeagueType=league_type,
            Commissioner=comm.id,
            MaxTeams=max_teams,
            DraftDate=draft_date,
        )
        db.session.add(new_league)
        db.session.commit()
        flash("League added successfully!", "success")
        return redirect(url_for("views.league"))

    # Search/Filter Teams
    search_query = request.args.get('search', '').strip()

    #  filter teams by name
    if search_query:
        leagues = League.query.filter(League.LeagueName.ilike(f'%{search_query}%')).all()
    else:
        leagues = League.query.all()  # No search, return all teams

    return render_template('leagues.html', leagues=leagues)


@views.route("/league/edit", methods=["POST"])
def edit_league():
    if "user" not in session:
        flash("You need to log in to access this page.", "error")
        return redirect(url_for("views.login"))

    comm = User.query.filter_by(username=session["user"]).first()

    # Handle editing the team
    league_id = request.form.get("league_id")
    league = League.query.get_or_404(league_id)

    # only owner can edit team
    if league.Commissioner != comm.id:
        flash("You do not have permission to edit this league. \n No changes saved.", "error")
        return redirect(url_for("views.league"))

    league_name = request.form.get("league_name")
    league_type = request.form.get("league_type")  # Expect either 'P' or 'R' (check or not)
    max_teams = request.form.get("max_teams")
    draft_date = request.form.get("draft_date")

    if league_type == 'P':
        new_league_type = 'P'
    else:
        new_league_type = 'R'

    league.LeagueName = league_name
    league.LeagueType = new_league_type
    league.MaxTeams = max_teams
    league.DraftDate = draft_date

    db.session.commit()
    flash("League updated successfully!", "success")
    return redirect(url_for("views.league"))


@views.route("/league/delete/<int:id>", methods=["POST"])
def delete_league(id):
    if "user" not in session:
        flash("You need to log in to access this page.", "error")
        return redirect(url_for("views.login"))

    league = League.query.get_or_404(id)
    db.session.delete(league)
    db.session.commit()

    flash("League deleted successfully!", "success")
    return redirect(url_for("views.league"))


# Teams
@views.route("/teams", methods=["GET", "POST"])
def teams():
    if "user" not in session:
        flash("You need to log in to access this page.", "error")
        return redirect(url_for("views.login"))

    owner = User.query.filter_by(username=session["user"]).first()

    # Handle adding a new team
    if request.method == "POST":
        team_name = request.form.get("team_name")
        league_id = request.form.get("league_id")
        total_points = request.form.get("points")
        status_value = request.form.get("status")

        # Convert the checkbox value to 'a' for active or 'i' for inactive
        if status_value == 'on':
            status = 'A'
        else:
            status = 'I'

        if not team_name or not league_id:
            flash("Team Name, and League ID are required.", "error")
            return redirect(url_for("views.teams"))

        new_team = Team(
            TeamName=team_name,
            Owner=owner.id,
            League_ID=league_id,
            TotalPoints=total_points,
            Status=status,
        )
        db.session.add(new_team)
        db.session.commit()
        update_team_ranking(new_team.Team_ID, total_points)
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

    owner = User.query.filter_by(username=session["user"]).first()

    # Handle editing the team
    team_id = request.form.get("team_id")
    team = Team.query.get_or_404(team_id)

    # only owner can edit team
    if team.Owner != owner.id:
        flash("You do not have permission to edit this team. \n No changes saved.", "error")
        return redirect(url_for("views.teams"))

    team_name = request.form.get("team_name")
    league_id = request.form.get("league_id")
    total_points = request.form.get("points")
    status_value = request.form.get("status")  # Expect either 'A' or 'I' (check or not)

    if status_value == 'A':
        status = 'A'
    else:
        status = 'I'

    team = Team.query.get_or_404(team_id)
    team.TeamName = team_name
    team.Owner = owner.id
    team.League_ID = league_id
    team.TotalPoints = total_points
    team.Status = status

    db.session.commit()
    update_team_ranking(team_id, total_points)
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

    # Update rankings for remaining teams
    teams = Team.query.order_by(Team.TotalPoints.desc()).all()
    for rank, team in enumerate(teams, start=1):
        team.Ranking = rank
    db.session.commit()

    flash("Team deleted successfully!", "success")
    return redirect(url_for("views.teams"))


@views.route('/players', methods=['GET', 'POST'])
def players():
    if "user" not in session:
        flash("You need to log in to access this page.", "error")
        return redirect(url_for("views.login"))

    owner = User.query.filter_by(username=session["user"]).first()

    if request.method == 'POST':
        # Handle adding a new player
        full_name = request.form['full_name']
        sport = request.form['sport']
        position = request.form.get('position', '')
        real_team = request.form.get('real_team', '')
        fantasy_points = request.form['fantasy_points']
        availability_status = 'A' if 'status' in request.form else 'U'
        team_id = request.form['team_id']

        team = Team.query.filter_by(Team_ID=team_id).first()
        if not team:
            flash("The selected team does not exist.", "error")
            return redirect(url_for('views.players'))
        real_team = team.TeamName

        new_player = Player(
            FullName=full_name,
            Sport=sport,
            Position=position,
            RealTeam=real_team,
            FantasyPoints=fantasy_points,
            AvailabilityStatus=availability_status,
            Team_ID=team_id  # Associate player with the team
        )
        db.session.add(new_player)
        db.session.commit()

        flash('Player added successfully!', 'success')
        return redirect(url_for('views.players'))

    # Get the teams of the logged-in user to display in the form
    user_teams = Team.query.filter_by(Owner=owner.id).all()

    search_query = request.args.get('search', '')

    if search_query:
        players = db.session.query(Player).filter(Player.FullName.like(f'%{search_query}%')).all()
    else:
        players = db.session.query(Player).all()

    return render_template('players.html', players=players, user_teams=user_teams)


# Route to handle editing a player's details
@views.route('/players/edit', methods=['GET', 'POST'])
def edit_player():
    player_id = request.form.get('player_id')  # Get player_id from the form

    if player_id:
        player = Player.query.get_or_404(player_id)

        owner = User.query.filter_by(username=session["user"]).first()
        owned_teams = Team.query.filter_by(Owner=owner.id).all()

        # Check if the player's team is one that the user owns
        if player.Team_ID not in [team.Team_ID for team in owned_teams]:
            flash("You are not authorized to edit this player's information.", 'danger')
            return redirect(url_for('views.players'))

        if request.method == 'POST':
            full_name = request.form['full_name']
            sport = request.form['sport']
            position = request.form.get('position', '')
            fantasy_points = request.form['fantasy_points']
            availability_status = 'A' if 'status' in request.form else 'U'
            team_id = request.form['team_id']

            team = Team.query.filter_by(Team_ID=team_id).first()
            real_team = team.TeamName

            player.FullName = full_name
            player.Sport = sport
            player.Position = position
            player.FantasyPoints = fantasy_points
            player.AvailabilityStatus = availability_status
            player.RealTeam = real_team
            player.Team_ID = team_id

            db.session.commit()

            flash('Player updated successfully!', 'success')
            return redirect(url_for('views.players'))
    else:
        flash('Player not found!', 'danger')
        return redirect(url_for('views.players'))

    return render_template('edit_player.html', player=player, owned_teams=owned_teams)


# Route to handle deleting a player
@views.route('/players/delete/<int:id>', methods=['POST'])
def delete_player(id):
    player = db.session.query(Player).filter(Player.Player_ID == id).first()
    if player:
        db.session.delete(player)
        db.session.commit()
        flash('Player deleted successfully!', 'success')
    else:
        flash('Player not found.', 'error')

    return redirect(url_for('views.players'))


@views.route("/player_stats")
def player_stats():
    if "user" not in session:
        flash("You need to log in to access this page.", "error")
        return redirect(url_for("views.login"))

    search_query = request.args.get("search", "")
    if search_query:
        stats = PlayerStatistics.query.join(Player).filter(
            Player.FullName.ilike(f"%{search_query}%")
        ).all()
    else:
        stats = PlayerStatistics.query.all()

    return render_template("player_stats.html", stats=stats, search_query=search_query)


#logout
@views.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out. Have a good day!", "success")
    return redirect(url_for("views.login"))



