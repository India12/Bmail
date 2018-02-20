#!/usr/bin/env python
import os
import jinja2
import webapp2
import json
from models import Message
from models import NewEmail
from google.appengine.api import users
from google.appengine.api import urlfetch

api_key = "2b9448f3b7960c3e992c3d62064c5f19"

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)

class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:  #if params is None:
            params = {}

        user = users.get_current_user()
        params["user"] = user

        if user:
            if not NewEmail.query(NewEmail.ind_contact == user.email()).fetch():
                contact = NewEmail(ind_contact=user.email())
                contact.put()
            params["contact_list"] = NewEmail.query().fetch()
            logged_in = True
            logout_url = users.create_logout_url('/')
            params["logout_url"] = logout_url
            params["email"] = user.email()

        else:
            logged_in = False
            login_url = users.create_login_url('/')
            params["login_url"] = login_url

        params["logged_in"] = logged_in

        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))

class LoginHandler(BaseHandler):
    def get(self):
        return self.render_template("login.html")

class LayoutHandler(BaseHandler):
    def get(self):
        msg_list = Message.query(Message.deleted == False, Message.draft == False).order(-Message.dateTime).fetch()
        params = {"msg_list": msg_list}
        return self.render_template("layout.html", params=params)

class NewEmailHandler(BaseHandler):
    def get(self):
        return self.render_template("new_email.html")

    def post(self):
        email_from = self.request.get("email_from")
        email_to = self.request.get("email_to")
        title = self.request.get("title")
        text = self.request.get("text")
        Draft = self.request.get("Draft")
        Send = self.request.get("Send")

        if "<script>" in text:
            return self.write("Can't hack me :P")

        if Draft == "Draft":
            draft_message = Message(email_from=email_from, title=title, email_to=email_to, text=text)
            draft_message.draft = True
            draft_message.put()
            return self.redirect_to("draft")

        elif Send == "Send":
            message = Message(email_from=email_from, title=title, email_to=email_to, text=text)
            message.put()
            return self.redirect_to("sent")

class IndividualNewEmailHandler(BaseHandler):
    def get(self, message_id):
        contact = NewEmail.get_by_id(int(message_id))
        params = {"contact":contact}
        return self.render_template("individual_new_email.html", params=params)

    def post(self, message_id):
        email_from = self.request.get("email_from")
        email_to = self.request.get("email_to")
        title = self.request.get("title")
        text = self.request.get("text")
        Draft = self.request.get("Draft")
        Send = self.request.get("Send")

        if "<script>" in text:
            return self.write("Can't hack me :P")

        if Draft == "Draft":
            draft_message = Message(email_from=email_from, title=title, email_to=email_to, text=text)
            draft_message.draft = True
            draft_message.put()
            return self.redirect_to("draft")

        elif Send == "Send":
            message = Message(email_from=email_from, title=title, email_to=email_to, text=text)
            message.put()
            return self.redirect_to("sent")

class SendForwardHandler(BaseHandler):
    def get(self, message_id):
        ind_message = Message.get_by_id(int(message_id))

        params = {"ind_message":ind_message}
        return self.render_template("send_forward.html", params=params)

    def post(self, message_id):
        email_from = self.request.get("email_from")
        email_to = self.request.get("email_to")
        title = self.request.get("title")
        text = self.request.get("text")
        Draft = self.request.get("Draft")
        Send = self.request.get("Send")

        if "<script>" in text:
            return self.write("Can't hack me :P")

        if Draft == "Draft":
            draft_message = Message(email_from=email_from, title=title, email_to=email_to, text=text)
            draft_message.draft = True
            draft_message.put()
            return self.redirect_to("draft")

        elif Send == "Send":
            message = Message(email_from=email_from, title=title, email_to=email_to, text=text)
            message.put()
            return self.redirect_to("sent")

class SentHandler(BaseHandler):
    def get(self):
        msg_list_sent = Message.query(Message.deleted == False, Message.draft == False).order(-Message.dateTime).fetch()
        params = {"msg_list_sent": msg_list_sent}
        return self.render_template("sent.html", params=params)

class DraftHandler(BaseHandler):
    def get(self):
        draft_message = Message.query(Message.deleted == False, Message.draft == True).order(-Message.dateTime).fetch()
        params = {"draft_message":draft_message}
        return self.render_template("draft.html", params=params)

class IndividualMessageHandler(BaseHandler):
    def get(self, message_id):
        ind_message = Message.get_by_id(int(message_id))
        params = {"ind_message": ind_message}
        return self.render_template("ind_message.html", params=params)

    def post(self, message_id):
        ind_message = Message.get_by_id(int(message_id))
        ind_message.deleted = True
        ind_message.put()
        return self.redirect_to("trash")

class TrashHandler(BaseHandler):
    def get(self):
        deleted_messages = Message.query(Message.deleted == True).order(-Message.dateTime).fetch()
        params = {"deleted_messages": deleted_messages}
        return self.render_template("trash.html", params=params)

class RestoreMessageHandler(BaseHandler):
    def get(self, message_id):
        ind_message_restore = Message.get_by_id(int(message_id))
        params = {"ind_message_restore": ind_message_restore}
        return self.render_template("restore.html", params=params)

    def post(self, message_id):
        ind_message_restore = Message.get_by_id(int(message_id))
        ind_message_restore.deleted = False
        ind_message_restore.put()
        return self.redirect_to("trash")

class PermanentDeleteMessageHandler(BaseHandler):
    def get(self, message_id):
        deleted_message = Message.get_by_id(int(message_id))
        params = {"deleted_message": deleted_message}
        return self.render_template("deleted_message.html", params=params)

    def post(self, message_id):
        deleted_message = Message.get_by_id(int(message_id))
        deleted_message.key.delete()
        return self.redirect_to("trash")

class WeatherHandler(BaseHandler):
    def post(self):
        location = self.request.get("location")
        url = "http://api.openweathermap.org/data/2.5/weather?q=%s&units=metric&appid=%s" % (location, api_key)

        result = urlfetch.fetch(url)

        json_data = json.loads(result.content)
        params = {"data": json_data}

        return self.render_template("layout.html", params=params)

app = webapp2.WSGIApplication([
    webapp2.Route('/', LoginHandler),
    webapp2.Route('/layout', LayoutHandler, name="layout"),
    webapp2.Route('/new_email', NewEmailHandler),
    webapp2.Route('/message/<message_id:\d+>/individual_new_email', IndividualNewEmailHandler),
    webapp2.Route('/message/<message_id:\d+>/send_forward', SendForwardHandler),
    webapp2.Route('/sent', SentHandler, name="sent"),
    webapp2.Route('/draft', DraftHandler, name="draft"),
    webapp2.Route('/message/<message_id:\d+>', IndividualMessageHandler),
    webapp2.Route('/trash', TrashHandler, name="trash"),
    webapp2.Route('/message/<message_id:\d+>/restore', RestoreMessageHandler),
    webapp2.Route('/message/<message_id:\d+>/deleted_message', PermanentDeleteMessageHandler),
    webapp2.Route('/weather', WeatherHandler),

], debug=True)

''' TO - DO list:
- login without google login;
- search bar - Javascript?;
- WeatherHandler - when button - Get weather is submitted, empty layout.html is displayed - (weather is correct though);
- create separate email users-actions or something - so that eg: when email is deleted, it is deleted only within specific user - the one that deleted email and etc.
'''
