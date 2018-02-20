from google.appengine.ext import ndb

class Message(ndb.Model):
    title = ndb.StringProperty()
    text = ndb.TextProperty()
    #author = ndb.StringProperty()

    email_from = ndb.StringProperty()
    email_to = ndb.StringProperty()
    dateTime = ndb.DateTimeProperty(auto_now_add=True)
    deleted = ndb.BooleanProperty(default=False)
    draft = ndb.BooleanProperty(default=False)

class NewEmail(ndb.Model):
    ind_contact = ndb.StringProperty()
