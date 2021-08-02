from flask_login import UserMixin

class MyUser(UserMixin):
    __tablename__ = 'users'

    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User {}>'.format(self.username)