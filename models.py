from flask_sqlalchemy import SQLAlchemy
import random

# Initialize SQLAlchemy
db = SQLAlchemy()

# Example User Model
def generate_unique_id():
    """Generate a unique 8-digit numeric ID."""
    while True:
        new_id = random.randint(10000000, 99999999)
        if not User.query.filter_by(id=new_id).first():  # Check if it's unique
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
    id = db.Column('User_ID', db.Numeric(8, 0), primary_key=True, default=generate_unique_id)
    name = db.Column('FullName', db.String(50))
    email = db.Column('Email', db.String(50), nullable=False, unique=True)
    username = db.Column('Username', db.String(20), nullable=False, unique=True)
    password = db.Column('Password', db.String(64), nullable=False)  # Should be hashed/encrypted
    profile_settings = db.Column('ProfileSettings', db.Text)


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
    Team_ID = db.Column(db.Numeric(8, 0), primary_key=True)
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


# Player model
class Player(db.Model):
    """Players Table"""
    __tablename__ = 'Players'

    # Columns
    Player_ID = db.Column(db.Numeric(8, 0), primary_key=True)
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