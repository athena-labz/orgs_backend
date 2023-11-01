import peewee as pw
import datetime


db = pw.SqliteDatabase('test.db')


class User(pw.Model):
    id = pw.IntegerField(primary_key=True)

    email = pw.CharField(128)
    stake_address = pw.CharField(128)
    token = pw.CharField(256, null=True)

    # If the current user is active / verified
    active = pw.BooleanField(default=False)

    register_date = pw.DateField(default=datetime.datetime.utcnow)

    class Meta:
        database = db