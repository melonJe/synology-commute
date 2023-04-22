from peewee import *

db = MySQLDatabase('my_database', user='my_username', password='my_password',
                   host='localhost', port=3306)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField()
    email = CharField()


db.connect()
db.create_tables([User])

# Create a new user
user = User(username='john', email='john@example.com')
user.save()

# Query all users
users = User.select()
for user in users:
    print(user.username, user.email)

# Query a specific user
user = User.get(User.username == 'john')
print(user.email)

# Update a user's email
user.email = 'john.new@example.com'
user.save()

# Delete a user
user.delete_instance()
