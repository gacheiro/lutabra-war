from app import db


class Death(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    char_name = db.Column(db.String(40), nullable=False)
    vocation = db.Column(db.String(15), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    guild = db.Column(db.Integer, nullable=False)

    @property
    def date(self):
        return self.datetime.date()
