# !/usr/bin/env python
import json
import logging
import os
from google.appengine.api import urlfetch

import webapp2
import jinja2

import cloudstorage as gcs

import computelandmark
# Retry can help overcome transient urlfetch or GCS issues, such as timeouts.
my_default_retry_params = gcs.RetryParams(initial_delay=0.2,
                                          max_delay=5.0,
                                          backoff_factor=2,
                                          max_retry_period=15)
# All requests to GCS using the GCS client within current GAE request and
# current thread will use this retry params as default. If a default is not
# set via this mechanism, the library's built-in default will be used.
# Any GCS client function can also be given a more specific retry params
# that overrides the default.
# Note: the built-in default is good enough for most cases. We override
# retry_params here only for demo purposes.
gcs.set_default_retry_params(my_default_retry_params)

IMG_BUCKET = '/visiontestimages/'


def saveUrl(url, title):
    '''
    saves object at url in cloud storage
    '''
    response = urlfetch.fetch(url)
    if response.status_code == 200:
        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        if not response.headers['content-type']:
            logging.error('no content-type header returned')
            logging.error(response.headers)
        gcs_file = gcs.open(title,
                            'w',
                            content_type=response.headers['content-type'],
                            options={'x-goog-acl': 'public-read'},
                            retry_params=write_retry_params)
        gcs_file.write(response.content)
        gcs_file.close()


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
config = {'webapp2_extras.sessions': dict(secret_key='93986c9cdd240540f70efaea56a9e3f2')}


class BaseHandler(webapp2.RequestHandler):
    def render(self, view_name, extraParams={}):
        template_values = {
        }
        template_values.update(extraParams)

        template = JINJA_ENVIRONMENT.get_template(view_name)
        self.response.write(template.render(template_values))


class GetFromUrlHandler(webapp2.RequestHandler):
    def get(self, url):
        name = url.hash()
        saveUrl(url, name)
        gcs_uri = 'gs://visiontestimages/'
        result = computelandmark.identify_landmark(gcs_uri + name)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(result))


class MainHandler(BaseHandler):
    def get(self):
        self.render('index.html')


class NotFoundHandler(BaseHandler):
    def get(self):
        self.response.set_status(404)
        self.render('index.html')


class SlashMurdererApp(webapp2.RequestHandler):
    def get(self, url):
        self.redirect(url)


app = webapp2.WSGIApplication([
                                  ('/', MainHandler),
                                  ('/image/(.*)', GetFromUrlHandler),
                                  ('(.*)/$', SlashMurdererApp),
                              ] + [
                                  ('/.*', NotFoundHandler),
                              ]
                              , debug=os.environ.get('SERVER_SOFTWARE', '').startswith('Development/'), config=config)
