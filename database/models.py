
# from app import conn
#
#
#
# class UserModel(conn.Model):
#     __tablename__ = 'users'
#
#     id = conn.Column(conn.Integer, primary_key=True)
#     username = conn.Column(conn.String(120),  nullable=False)
#     passwrd = conn.Column(conn.String(255), nullable=False)
#
#     def save_to_db(self):
#         conn.session.add(self)
#         conn.commit()
