from database import db

class Agent(db.Model):
    jid = db.Column(db.String(80), primary_key=True)
    player_type = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<Agent %r>' % self.jid
