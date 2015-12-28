#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import cgi
import os

import wsgiref.handlers

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template

class InputTodoTemplatized(webapp.RequestHandler):

  def get(self):

    user = users.get_current_user()

    if user:
      path = os.path.join(os.path.dirname(__file__), 'templates/evententer.html')
      self.response.out.write(template.render(path, {}))
    else:
      self.redirect(users.create_login_url(self.request.uri))


class ReadTodos(webapp.RequestHandler):
  def post(self):
    todoitem = Todoitem()
    
    if users.get_current_user():
      todoitem.author = users.get_current_user()
    
    todoitem.content = self.request.get('content')
    todoitem.put()
    self.redirect('/')


class ListTodosTemplatized(webapp.RequestHandler):
  def get(self):
    todos = db.GqlQuery("SELECT * FROM Todoitem ORDER BY entereddate DESC")
    current_user = users.get_current_user()
    # pull out just the todos for the given user
    my_todos = filter(lambda x: x.author == current_user, todos)

    # pass those to the output template
    template_values = { 'todos' : my_todos }
    path = os.path.join(os.path.dirname(__file__), 'templates/eventlist.html')

    # render our output
    self.response.out.write(template.render(path, template_values))


class Todoitem(db.Model):
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  entereddate = db.DateTimeProperty(auto_now_add=True)


def main():
  application = webapp.WSGIApplication(
    [('/', InputTodoTemplatized),
     ('/additem', ReadTodos),
     ('/list', ListTodosTemplatized)],
    debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if  __name__ == '__main__':
  main()
