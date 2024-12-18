from flask_sqlalchemy import SQLAlchemy
import random

# Initialize SQLAlchemy
db = SQLAlchemy()

# Example User Model
def generate_unique_user_id():
    """Generate a unique 8-digit numeric ID."""
    while True:
        new_id = random.randint(10000000, 99999999)
        if not User.query.filter_by(User_ID=new_id).first():  # Check if it's unique
            return new_id


def generate_unique_team_id():
    """Generate a unique 8-digit numeric ID."""
    while True:
        new_id = random.randint(10000000, 99999999)
        if not Team.query.filter_by(Team_ID=new_id).first():  # Check if it's unique
            return new_id

def generate_unique_player_id():
    """Generate a unique 8-digit numeric ID."""
    while True:
        new_id = random.randint(10000000, 99999999)
        if not Player.query.filter_by(Player_ID=new_id).first():  # Check if it's unique
            return new_id

def generate_unique_player_stat_id():
    """Generate a unique 10-digit numeric ID."""
    while True:
        new_id = random.randint(1000000000, 9999999999)
        if not PlayerStatistics.query.filter_by(Statistic_ID=new_id).first():  # Check if it's unique
            return new_id

def generate_unique_draft_id():
    """Generate a unique 8-digit numeric ID."""
    while True:
        new_id = random.randint(10000000, 99999999)
        if not Draft.query.filter_by(Draft_ID=new_id).first():  # Check if it's unique
            return new_id

def generate_unique_waiver_id():
    """Generate a unique 8-digit numeric ID."""
    while True:
        new_id = random.randint(10000000, 99999999)
        if not Waiver.query.filter_by(Waiver_ID=new_id).first():  # Check if it's unique
            return new_id


class User(db.Model):
    """Users Table"""
    # __tablename__ = 'Users'
    # id = db.Column(db.Numeric(8, 0), primary_key=True, default=generate_unique_id)
    # name = db.Column(db.String(50))
    # email = db.Column(db.String(50), nullable=False, unique=True)
    # username = db.Column(db.String(20), nullable=False, unique=True)
    # password = db.Column(db.String(64), nullable=False)  # Should be hashed/encrypted
    # profile_settings = db.Column(db.Text)

    # for xxamp, note: change User.id to User.User_ID in League and Team
    __tablename__ = 'Users'
    User_ID = db.Column('User_ID', db.Numeric(8, 0), primary_key=True, default=generate_unique_user_id)
    name = db.Column('FullName', db.String(50))
    email = db.Column('Email', db.String(50), nullable=False, unique=True)
    username = db.Column('Username', db.String(20), nullable=False, unique=True)
    password = db.Column('Password', db.String(64), nullable=False)  # Should be hashed/encrypted
    profile_settings = db.Column('ProfileSettings', db.Text)
    role = db.Column('Role', db.String(10), default='USER')


# League model
class League(db.Model):
    """Leagues Table"""
    __tablename__ = 'Leagues'
    League_ID = db.Column(db.Numeric(8, 0), primary_key=True)
    LeagueName = db.Column(db.String(30), nullable=False)
    LeagueType = db.Column(db.String(1), nullable=False, default='U')
    Commissioner = db.Column(db.Numeric(8, 0), db.ForeignKey('Users.User_ID'))
    MaxTeams = db.Column(db.Numeric(2, 0), nullable=False, default=10)
    DraftDate = db.Column(db.Date)

    # Relationships
    commissioner = db.relationship('User', backref='leagues', lazy=True)

    # Constraints
    __table_args__ = (
        db.CheckConstraint("LeagueType IN ('P', 'R')"),
    )


# Team model
class Team(db.Model):
    """Teams Table"""
    __tablename__ = 'Teams'
    Team_ID = db.Column(db.Numeric(8, 0), primary_key=True, default=generate_unique_team_id)
    TeamName = db.Column(db.String(25), nullable=False)
    Owner = db.Column(db.Numeric(8, 0), db.ForeignKey('Users.User_ID'))
    League_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Leagues.League_ID'))
    TotalPoints = db.Column(db.Numeric(6, 2), default=0.00)
    Ranking = db.Column(db.Numeric(3, 0))
    Status = db.Column(db.String(1), default='A')

    # Relationships
    owner = db.relationship('User', backref='teams', lazy=True)
    league = db.relationship('League', backref='teams', lazy=True)

    # Constraints
    __table_args__ = (
        db.CheckConstraint("Status IN ('A', 'I')"),
    )

    @staticmethod
    def update_rankings():
        """Update the rankings for all teams based on TotalPoints."""
        teams = Team.query.order_by(Team.TotalPoints.desc()).all()
        for rank, team in enumerate(teams, start=1):
            team.Ranking = rank
        db.session.commit()


def update_team_ranking(team_id, new_points):
    team = Team.query.get(team_id)
    if team:
        team.TotalPoints = new_points
        db.session.commit()
        Team.update_rankings()


# Player model
class Player(db.Model):
    """Players Table"""
    __tablename__ = 'Players'

    # Columns
    Player_ID = db.Column(db.Numeric(8, 0), primary_key=True, default=generate_unique_player_id)
    Team_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Teams.Team_ID'))
    FullName = db.Column(db.String(50), nullable=False)
    Sport = db.Column(db.String(3), nullable=False)
    Position = db.Column(db.String(3))
    RealTeam = db.Column(db.String(50))
    FantasyPoints = db.Column(db.Numeric(6, 2), default=0.00)
    AvailabilityStatus = db.Column(db.String(1), default='A')

    # Relationships
    team = db.relationship('Team', backref='players', lazy=True)

    # Constraints
    __table_args__ = (
        db.CheckConstraint("Sport IN ('FTB', 'BB', 'SB')"),
        db.CheckConstraint("AvailabilityStatus IN ('A', 'U')"),
    )


class PlayerStatistics(db.Model):
    """Player Statistics Table"""
    __tablename__ = 'PlayerStatistics'

    # Columns
    Statistic_ID = db.Column(db.Numeric(10, 0), primary_key=True, autoincrement=True,
                             default=generate_unique_player_stat_id)
    Player_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Players.Player_ID'), nullable=False)
    GameDate = db.Column(db.Date, nullable=False)
    PerformanceStatistics = db.Column(db.Text, nullable=True)
    InjuryStatus = db.Column(db.String(1), default='N', nullable=False)

    # Relationships
    player = db.relationship('Player', backref='player_statistics', lazy=True)

    # Constraints
    __table_args__ = (
        db.CheckConstraint("InjuryStatus IN ('Y', 'N')"),
    )

class Draft(db.Model):
    """Drafts Table"""
    __tablename__ = 'Drafts'

    # Columns
    Draft_ID = db.Column(db.Numeric(8, 0), primary_key=True, autoincrement=True,
                             default=generate_unique_draft_id)
    League_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Leagues.League_ID'), nullable=False)
    DraftDate = db.Column(db.Date, nullable=False)
    DraftOrder = db.Column(db.String(1), nullable=True)
    DraftStatus = db.Column(db.String(1), default='I', nullable=False)

    # Relationships
    league = db.relationship('League', backref='drafts', lazy=True)

    # Constraints
    __table_args__ = (
        db.CheckConstraint("DraftOrder IN ('R', 'S')"),
        db.CheckConstraint("DraftStatus IN ('I', 'C')"),
    )

class Draft_Players(db.Model):
    """Draft Players Table"""
    __tablename__ = 'Draft_Players'

    # Columns
    Draft_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Drafts.Draft_ID'), primary_key=True, nullable=False)
    Player_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Players.Player_ID'), primary_key=True, nullable=False)

    # Relationships
    draft = db.relationship('Draft', backref='draft_players', lazy=True)
    player = db.relationship('Player', backref='draft_players', lazy=True)




class Trade(db.Model):
    """Trades Table"""
    __tablename__ = 'Trades'

    # Columns
    Trade_ID = db.Column(db.Numeric(8, 0), primary_key=True, autoincrement=True)
    Team1_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Teams.Team_ID'), nullable=False)
    Team2_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Teams.Team_ID'), nullable=False)
    TradedPlayer1_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Players.Player_ID'), nullable=False)
    TradedPlayer2_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Players.Player_ID'), nullable=False)
    TradeDate = db.Column(db.Date, nullable=False)

    # Relationships
    team1 = db.relationship('Team', foreign_keys=[Team1_ID], backref='trades_as_team1', lazy=True)
    team2 = db.relationship('Team', foreign_keys=[Team2_ID], backref='trades_as_team2', lazy=True)
    traded_player1 = db.relationship('Player', foreign_keys=[TradedPlayer1_ID], backref='trades_as_player1', lazy=True)
    traded_player2 = db.relationship('Player', foreign_keys=[TradedPlayer2_ID], backref='trades_as_player2', lazy=True)


class Match(db.Model):
    """Matches Table"""
    __tablename__ = 'Matches'

    Match_ID = db.Column(db.Numeric(8, 0), primary_key=True)
    Team1_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Teams.Team_ID'))
    Team2_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Teams.Team_ID'))
    MatchDate = db.Column(db.Date, nullable=False)
    FinalScore = db.Column(db.String(10))  # Example: "75-68"
    Winner = db.Column(db.Numeric(8, 0), db.ForeignKey('Teams.Team_ID'))

    # Relationships
    team1 = db.relationship("Team", foreign_keys=[Team1_ID], backref="matches_as_team1")
    team2 = db.relationship("Team", foreign_keys=[Team2_ID], backref="matches_as_team2")
    winning_team = db.relationship("Team", foreign_keys=[Winner], backref="matches_won")

    # Relationship with MatchEvent
    events = db.relationship("MatchEvent", backref="match", lazy=True)


class MatchEvent(db.Model):
    """Match Events Table"""
    __tablename__ = 'match_events'

    Match_Event_ID = db.Column(db.Numeric(8, 0), primary_key=True)
    Match_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Matches.Match_ID'), nullable=False)
    Player1_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Players.Player_ID'))
    Player2_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Players.Player_ID'), nullable=True)  # Nullable for solo events
    EventType = db.Column(db.String(1), nullable=False)  # G: Goal, A: Assist, F: Foul
    EventTime = db.Column(db.Time, nullable=False)  # Time of the event in the match
    ImpactOnFantasyPoints = db.Column(db.Integer, default=0)

    # Relationships
    player1 = db.relationship("Player", foreign_keys=[Player1_ID], backref="events_as_player1")
    player2 = db.relationship("Player", foreign_keys=[Player2_ID], backref="events_as_player2")



def update_match_status(match_id, score_team1, score_team2):
    """Update match status and scores."""
    match = Match.query.get(match_id)
    if match:
        match.ScoreTeam1 = score_team1
        match.ScoreTeam2 = score_team2
        match.Status = 'C'  # Mark as Completed
        db.session.commit()

class Waiver(db.Model):
    """Waivers Table"""
    __tablename__ = 'Waivers'

    Waiver_ID = db.Column(db.Numeric(8, 0), primary_key=True, nullable=False, autoincrement=True,
                             default=generate_unique_waiver_id)
    Team_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Teams.Team_ID'), nullable=False)
    Player_ID = db.Column(db.Numeric(8, 0), db.ForeignKey('Players.Player_ID'), nullable=False)
    WaiverOrder = db.Column(db.Numeric(3, 0), nullable=True)
    WaiverStatus = db.Column(db.String(1), default='P', nullable=False)  # P: Pending, A: Approved
    WaiverPickupDate = db.Column(db.Date, nullable=True)

    # Relationships
    team = db.relationship("Team", foreign_keys=[Team_ID], backref="waivers_for_team")
    player = db.relationship("Player", foreign_keys=[Player_ID], backref="waivers_for_player")

    # Constraints
    __table_args__ = (
        db.CheckConstraint("WaiverStatus IN ('P', 'A')"),
    )