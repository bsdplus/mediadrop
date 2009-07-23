from tg.configuration import AppConfig, Bunch, config
from routes import Mapper

import mediaplex
from mediaplex import model
from mediaplex.lib import app_globals, helpers

class MediaplexConfig(AppConfig):
    def setup_routes(self):
        """Setup our custom named routes"""
        map = Mapper(directory=config['pylons.paths']['controllers'],
                    always_scan=config['debug'])

        # home page redirect
        map.redirect('/', '/video-flow')

        # route for the concept sunday school action
        map.connect('/concept', controller='video', action='concept_preview')
        map.connect('/concept/{slug}/comment', controller='media', action='concept_comment')
        map.connect('/concept/{slug}', controller='media', action='concept_view')

        map.connect('/lessons', controller='media', action='lessons')
        map.connect('/lessons/{slug}', controller='media', action='lesson_view')
        map.connect('/lessons/{slug}/comment', controller='media', action='lesson_comment')

        # routes for all non-view, non-index, video actions
        map.connect('/video-{action}', controller='video', requirements=dict(action='flow|upload|upload_submit|upload_submit_async|upload_success|upload_failure'))
        map.connect('/video-{action}/{slug}', slug=None, controller='video', requirements=dict(action='tags|rate|serve'))
        # route for viewing videos and other video related actions
        map.connect('/video/{slug}/{action}', controller='video', action='view', requirements=dict(action='rate|serve'))

        map.connect('/media/{slug}.{type}', controller='media', action='serve')
        map.connect('/media/{slug}/{action}', controller='media', action='view', requirements=dict(action='view|rate|comment'))
        # podcasts
        map.connect('/podcasts/{slug}.xml', controller='podcasts', action='feed')
        map.connect('/podcasts/{slug}', controller='podcasts', action='view')
        map.connect('/podcasts/{podcast_slug}/{slug}/{action}', controller='media', action='view', requirements=dict(action='view|rate|comment|feed'))
        # admin routes
        map.connect('/admin/media', controller='mediaadmin', action='index')
        map.connect('/admin/media/{id}/{action}', controller='mediaadmin', action='edit', requirements=dict(action='edit|save|add_file|edit_file|reorder_file|save_album_art|update_status'))

        map.connect('/admin/podcasts', controller='podcastadmin', action='index')
        map.connect('/admin/podcasts/{id}/{action}', controller='podcastadmin', action='edit')

        map.connect('/admin/comments', controller='commentadmin', action='index')
        map.connect('/admin/comments/{id}/{action}', controller='commentadmin', action='edit')

        # Set up the default route
        map.connect('/{controller}/{action}', action='index')

        # Set up a fallback route for object dispatch
        map.connect('*url', controller='root', action='routes_placeholder')

        config['routes.map'] = map


base_config = MediaplexConfig()
base_config.renderers = []

base_config.package = mediaplex

#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi')
# if you want raw speed and have installed chameleon.genshi
# you should try to use this renderer instead.
# warning: for the moment chameleon does not handle i18n translations
#base_config.renderers.append('chameleon_genshi')

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = mediaplex.model
base_config.DBSession = mediaplex.model.DBSession

# Configure the authentication backend
base_config.auth_backend = 'sqlalchemy'
base_config.sa_auth.dbsession = model.DBSession
# what is the class you want to use to search for users in the database
base_config.sa_auth.user_class = model.User
# what is the class you want to use to search for groups in the database
base_config.sa_auth.group_class = model.Group
# what is the class you want to use to search for permissions in the database
base_config.sa_auth.permission_class = model.Permission

# override this if you would like to provide a different who plugin for
# managing login and logout of your application
base_config.sa_auth.form_plugin = None

# You may optionally define a page where you want users to be redirected to
# on login:
base_config.sa_auth.post_login_url = '/post_login'

# You may optionally define a page where you want users to be redirected to
# on logout:
base_config.sa_auth.post_logout_url = '/post_logout'

# custom auth goodness
from repoze.who.classifiers import default_request_classifier
from paste.httpheaders import USER_AGENT
from paste.httpheaders import REQUEST_METHOD
from paste.request import parse_formvars
def custom_classifier_for_flash_uploads(environ):
    """Normally classifies the request as browser, dav or xmlpost.

    When the Flash uploader is sending a file, it appends the authtkt session ID
    to the POST data so we spoof the cookie header so that the auth code will
    think this was a normal request. In the process, we overwrite any
    pseudo-cookie data that is sent by Flash.
    """
    classification = default_request_classifier(environ)
    if classification == 'browser' and REQUEST_METHOD(environ) == 'POST' and 'Flash' in USER_AGENT(environ):
        try:
            session_key = environ['repoze.who.plugins']['cookie'].cookie_name
            session_id = parse_formvars(environ)[session_key]
            environ['HTTP_COOKIE'] = '%s=%s' % (session_key, session_id)
            del environ['paste.cookies']
            del environ['paste.cookies.dict']
        except (KeyError, AttributeError):
            pass
    return classification
base_config.sa_auth.classifier = custom_classifier_for_flash_uploads


# Mimetypes
base_config.mimetype_lookup = {
    '.flv': 'video/x-flv',
    '.mp3': 'audio/mpeg',
    '.mp4': 'audio/mpeg',
    '.m4a': 'audio/mpeg',
}

base_config.embeddable_filetypes = {
    'youtube': {
        'play': 'http://youtube.com/v/%s',
        'link': 'http://youtube.com/watch?v=%s',
        'pattern': '^(http(s?)://)?(www.)?youtube.com/watch\?(.*&)?v=(?P<id>[^&#]+)'
    },
    'google': {
        'play': 'http://video.google.com/googleplayer.swf?docid=%s&hl=en&fs=true',
        'link': 'http://video.google.com/videoplay?docid=%s',
        'pattern': '^(http(s?)://)?video.google.com/videoplay\?(.*&)?docid=(?P<id>-\d+)'
    },
    'vimeo': {
        'play': 'http://vimeo.com/moogaloop.swf?clip_id=%d&server=vimeo.com&show_title=1&show_byline=1&show_portrait=0&color=&fullscreen=1',
        'link': 'http://vimeo.com/%s',
        'pattern': '^(http(s?)://)?(www.)?vimeo.com/(?P<id>\d+)'
    },
}
