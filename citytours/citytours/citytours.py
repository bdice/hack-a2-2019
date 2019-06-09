from flask import Flask, session, request, url_for, render_template, flash, g
from werkzeug import url_encode
import jinja2
from flask_assets import Environment, Bundle
from flask_turbolinks import turbolinks
import os
import sys
import logging
import warnings
import shlex
import argparse
import inspect
from functools import lru_cache
from numbers import Real
import json
import natsort

from .version import __version__
from .pagination import Pagination
from .util import LazyView
from .tour import Tour

logger = logging.getLogger(__name__)


class CityTours:
    """Instance of the citytours application.

    This class is designed to be used as a base class for a child
    class which can be customized and launched via
    its command line interface (CLI). The CLI is invoked by calling
    :py:meth:`.main` on an instance of this class.

    **Configuration options:** The :code:`config` dictionary recognizes the
    following options:

    - **HOST**: Sets binding address (default: localhost).
    - **PORT**: Sets port to listen on (default: 8888).
    - **DEBUG**: Enables debug mode if :code:`True` (default: :code:`False`).
    - **PROFILE**: Enables the profiler
      :py:class:`werkzeug.middleware.profiler.ProfilerMiddleware` if
      :code:`True` (default: :code:`False`).
    - **SECRET_KEY**: This must be specified to run via WSGI with multiple
      workers, so that sessions remain intact. See the
      `Flask docs <http://flask.pocoo.org/docs/1.0/config/#SECRET_KEY>`_
      for more information.

    :param config: Configuration dictionary (default: :code:`{}`).
    :type config: dict
    """
    def __init__(self, config={}, tours={}):
        self.config = config
        self.tours = tours
        self._prepare()

    def _create_app(self, config={}):
        """Creates a Flask application.

        :param config: Dictionary of configuration parameters.
        """
        app = Flask('citytours')
        app.config.update({
            'SECRET_KEY': os.urandom(24),
            'SEND_FILE_MAX_AGE_DEFAULT': 300,  # Cache control for static files
        })

        # Load the provided config
        app.config.update(config)

        # Enable profiling
        if app.config.get('PROFILE'):
            logger.warning("Application profiling is enabled.")
            from werkzeug.contrib.profiler import ProfilerMiddleware
            app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[10])

        # Set up default static and template paths
        package_path = os.path.dirname(__file__)
        app.static_folder = package_path + '/static'
        app.template_folder = package_path + '/templates'

        # Set up custom template paths
        # The paths in DASHBOARD_PATHS give the preferred order of template
        # loading
        loader_list = []
        for dashpath in list(app.config.get('DASHBOARD_PATHS', [])):
            logger.warning("Adding '{}' to CityTour paths.".format(dashpath))
            loader_list.append(
                jinja2.FileSystemLoader(dashpath + '/templates'))

        # The default loader goes last and is overridden by any custom paths
        loader_list.append(app.jinja_loader)

        app.jinja_loader = jinja2.ChoiceLoader(loader_list)

        turbolinks(app)

        return app

    def _create_assets(self):
        """Add assets for inclusion in the CityTour HTML."""

        assets = Environment(self.app)
        # jQuery is served as a standalone file
        jquery = Bundle('js/jquery-*.min.js', output='gen/jquery.min.js')
        # JavaScript is combined into one file and minified
        js_all = Bundle('js/js_all/*.js',
                        filters='jsmin',
                        output='gen/app.min.js')
        # SCSS (Sassy CSS) is compiled to CSS
        scss_all = Bundle('scss/app.scss',
                          filters='libsass',
                          output='gen/app.css')
        assets.register('jquery', jquery)
        assets.register('js_all', js_all)
        assets.register('scss_all', scss_all)
        return assets

    def _prepare(self):
        """Prepare this CityTour instance to run."""

        # Create and configure the Flask application
        self.app = self._create_app(self.config)

        # Add assets and routes
        self.assets = self._create_assets()
        self._register_routes()

        # Clear CityTour caches.
        self.update_cache()

    def run(self, *args, **kwargs):
        """Runs the CityTour webserver.

        Use :py:meth:`~.main` instead of this method for the command-line
        interface. Arguments to this function are passed directly to
        :py:meth:`flask.Flask.run`.
        """
        host = self.config.get('HOST', 'localhost')
        port = self.config.get('PORT', 8888)
        max_retries = 5

        for _ in range(max_retries):
            try:
                self.app.run(host, port, *args, **kwargs)
                break
            except OSError as e:
                logger.warning(e)
                if port:
                    port += 1
                pass

    def tour_title(self, tour):
        """Override this method for custom tour titles.

        :param tour: The tour being titled.
        :type tour: Tour
        :returns: Title to be displayed.
        :rtype: str
        """
        return tour['title']

    def tour_subtitle(self, tour):
        """Override this method for custom tour subtitles.

        :param tour: The tour being subtitled.
        :type tour: Tour.
        :returns: Subtitle to be displayed.
        :rtype: str
        """
        return tour['subtitle']

    def tour_sorter(self, tour):
        """Override this method for custom tour sorting.

        This method returns a key that can be compared to sort tours. By
        default, the sorting key is based on :py:func:`Dashboard.tour_title`,
        with natural sorting of numbers. Good examples of such keys are
        strings or tuples of properties that should be used to sort.

        :param tour: The tour being sorted.
        :type tour: Tour.
        :returns: Key for sorting.
        :rtype: any comparable type
        """
        key = natsort.natsort_keygen(key=self.tour_title, alg=natsort.REAL)
        return key(tour)

    @lru_cache(maxsize=65536)
    def _tour_details(self, tour):
        return {
            'tour': tour,
            'title': self.tour_title(tour),
            'subtitle': self.tour_subtitle(tour),
        }

    def _setup_pagination(self, tours):
        total_count = len(tours) if isinstance(tours, list) else 0
        page = request.args.get('page', 1)
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1
            flash('Pagination Error. Displaying page {}.'.format(page),
                  'danger')
        pagination = Pagination(page, self.config['PER_PAGE'], total_count)
        if pagination.page < 1 or pagination.page > pagination.pages:
            pagination.page = max(1, min(pagination.page, pagination.pages))
            if pagination.pages > 0:
                flash('Pagination Error. Displaying page {}.'.format(
                    pagination.page), 'danger')
        return pagination

    def _render_error(self, error):
        if isinstance(error, Exception):
            error_string = "{}: {}".format(type(error).__name__, error)
        else:
            error_string = error
        logger.error(error_string)
        flash(error_string, 'danger')
        return render_template('error.html')

    def _get_tour_details(self, tours):
        return [self._tour_details(tour) for tour in list(tours)]

    def add_url(self, import_name, url_rules=[],
                import_file='citytours', **options):
        """Add a route to the CityTour.

        This method allows custom view functions to be triggered for specified
        routes. These view functions are imported lazily, when their route
        is triggered. For example, write a file :code:`my_views.py`:

        .. code-block:: python

            def my_custom_view(CityTour):
                return 'This is a custom message.'

        Then, in :code:`CityTour.py`:

        .. code-block:: python

            from citytours import Dashboard

            class MyDashboard(Dashboard):
                pass

            if __name__ == '__main__':
                CityTour = MyDashboard()
                CityTour.add_url('my_custom_view', url_rules=['/custom-url'],
                                  import_file='my_views')
                CityTour.main()

        Finally, launching the CityTour with :code:`python CityTour.py run`
        and navigating to :code:`/custom-url` will show the custom
        message. This can be used in conjunction with user-provided jinja
        templates and the method :py:func:`flask.render_template` for extending
        CityTour functionality.

        :param import_name: The view function name to be imported.
        :type import_name: str
        :param url_rules: A list of URL rules, see
            :py:meth:`flask.Flask.add_url_rule`.
        :type url_rules: list
        :param import_file: The module from which to import (default:
            :code:`'citytours'`).
        :type import_file: str
        :param \\**options: Additional options to pass to
            :py:meth:`flask.Flask.add_url_rule`.
        """
        if import_file is not None:
            import_name = import_file + '.' + import_name
        for url_rule in url_rules:
            self.app.add_url_rule(
                rule=url_rule,
                view_func=LazyView(citytour=self, import_name=import_name),
                **options)

    def _register_routes(self):
        """Registers routes with the Flask application.

        This method configures context processors, templates, and sets up
        routes for a basic CityTours instance.
        """
        CityTours = self

        @CityTours.app.after_request
        def prevent_caching(response):
            if 'Cache-Control' not in response.headers:
                response.headers['Cache-Control'] = 'no-store'
            return response

        @CityTours.app.context_processor
        def injections():
            return {
                'APP_NAME': self.config.get('name', 'City Tours'),
                'APP_VERSION': __version__,
            }

        # Add pagination support from http://flask.pocoo.org/snippets/44/
        @CityTours.app.template_global()
        def url_for_other_page(page):
            args = request.args.copy()
            args['page'] = page
            return url_for(request.endpoint, **args)

        @CityTours.app.template_global()
        def modify_query(**new_values):
            args = request.args.copy()
            for key, value in new_values.items():
                args[key] = value
            return '{}?{}'.format(request.path, url_encode(args))

        @CityTours.app.errorhandler(404)
        def page_not_found(error):
            return self._render_error(str(error))

        self.add_url('views.home', ['/'])
        self.add_url('views.tours_list', ['/tours/'])
        self.add_url('views.show_tour', ['/tours/<tourname>'])

    def update_cache(self):
        """Clear CityTour server caches.

        The CityTour relies on caching for performance. If the data space is
        altered, this method may need to be called before the CityTour
        reflects those changes.
        """

        # Clear caches of all CityTour methods
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        for func in filter(lambda f: hasattr(f, 'cache_clear'),
                           map(lambda x: x[1], members)):
            func.cache_clear()

    def __call__(self, environ, start_response):
        """Call the CityTour as a WSGI application."""
        return self.app(environ, start_response)

    def main(self):
        """Runs the command line interface.

        Call this function to use CityTour from its command line
        interface. For example, save this script as :code:`citytour.py`:

        .. code-block:: python

            from citytours import CityTour

            class MyCityTour(CityTour):
                pass

            if __name__ == '__main__':
                MyCityTour().main()

        Then the CityTour can be launched with:

        .. code-block:: bash

            python citytour.py run
        """

        def _run(args):
            kwargs = vars(args)
            if kwargs.get('host', None) is not None:
                self.config['HOST'] = kwargs.pop('host')
            if kwargs.get('port', None) is not None:
                self.config['PORT'] = kwargs.pop('port')
            self.config['PROFILE'] = kwargs.pop('profile')
            self.config['DEBUG'] = kwargs.pop('debug')
            self.run()

        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--debug',
            action='store_true',
            help="Show traceback on error for debugging.")
        parser.add_argument(
            '--version',
            action='store_true',
            help="Display the version number and exit.")
        subparsers = parser.add_subparsers()

        parser_run = subparsers.add_parser('run')
        parser_run.add_argument(
            '-p', '--profile',
            action='store_true',
            help='Enable flask performance profiling.')
        parser_run.add_argument(
            '-d', '--debug',
            action='store_true',
            help='Enable flask debug mode.')
        parser_run.add_argument(
            '--host', type=str,
            help='Host (binding address). Default: localhost')
        parser_run.add_argument(
            '--port', type=int,
            help='Port to listen on. Default: 8888')
        parser_run.set_defaults(func=_run)

        # This is a hack, as argparse itself does not
        # allow to parse only --version without any
        # of the other required arguments.
        if '--version' in sys.argv:
            print('CityTour', __version__)
            sys.exit(0)

        args = parser.parse_args()

        if args.debug:
            logger.setLevel(logging.DEBUG)

        if not hasattr(args, 'func'):
            parser.print_usage()
            sys.exit(2)
        try:
            args.func(args)
        except KeyboardInterrupt:
            logger.error("Interrupted.")
            if args.debug:
                raise
            sys.exit(1)
        except RuntimeWarning as warning:
            logger.warning("Warning: {}".format(warning))
            if args.debug:
                raise
            sys.exit(1)
        except Exception as error:
            logger.error('Error: {}'.format(error))
            if args.debug:
                raise
            sys.exit(1)
        else:
            sys.exit(0)
