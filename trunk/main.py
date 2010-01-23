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


import logging
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template


from waveapi import document
from waveapi import events
from waveapi import model
from waveapi import robot
from waveapi import robot_abstract
from waveapi.robot_abstract import NewWave

class WaveHandler(webapp.RequestHandler):
  def get(self):
    logging.info("cron job called")

class GadgetsHandler(webapp.RequestHandler):
  def get(self, name):
    path = os.path.join(os.path.dirname(__file__), 'gadgets/' + name + '.xml')
    template_params = dict((k, v) for k, v in self.request.GET.iteritems())
    logging.info(template_params)
    self.response.out.write(template.render(path, template_params))

class MainHandler(webapp.RequestHandler):

  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    self.response.out.write(template.render(path, {}))


def main():
  application = webapp.WSGIApplication([('/wave', WaveHandler),
                                        ('/gadgets/(.*).xml', GadgetsHandler),
                                        ('/', MainHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
