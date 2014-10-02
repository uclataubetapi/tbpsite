.. tbpsite documentation master file, created by
   sphinx-quickstart on Fri May 23 16:34:17 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to tbpsite's documentation!
===================================

Contents
--------

Main Django directories:

.. toctree::
   :maxdepth: 2

   web
   main
   event
   tutoring

Other files:

.. toctree::
   :maxdepth: 2

   common
   constants
   points

Other directories:

* tbpsite: settings and url configuration

* templates: Django HTML template files

* static: CSS/JS and image files to display on the website

  - If static files aren't updating, run ./manage.py collectstatic

Documentation
-------------

This documentation uses sphinx to convert the .rst files to .html.

The commands to update the docs from the root directory of the project are:

.. code-block:: bash

   cd docs
   make html

The commands to generate the .rst files are:

.. code-block:: bash

   sphinx-quickstart
   sphinx-autodoc -o docs .

Tutorial
--------

Let's start from the top. Say the user wants to look at their profile and they click on the link https://tbp.seas.ucla.edu/profile/.
Django will receive the request and will pass it to a function that takes a request and returns HTML (a view). Django will look in the tbpsite/urls.py file to see what function to call.

tbpsite/urls.py:

.. literalinclude:: ../tbpsite/urls.py
   :emphasize-lines: 24, 39

Django will match the profile portion of the url with r'^profile/$' and will call the profile_view function in the main.views module.

View
^^^^

main/views.py:

.. literalinclude:: ../main/views.py
   :pyobject: profile_view

The view calls this helper function to inject tab information that is used to render the tabs on the profile page.

.. literalinclude:: ../main/views.py
   :pyobject: render_profile_page

This helper function calls a similar function to inject navbar information. This function should be called by every view.

common/views.py:

.. literalinclude:: ../common.py
   :pyobject: render

Which finally renders the template file.

Template
^^^^^^^^

The values of the variables are inserted into the template.
We use `Bootstrap <http://getbootstrap.com/>`_ to style the website.

.. literalinclude:: ../templates/profile.html

profile.html extends profile_base.html which inserts the HTML for the profile tabs.

.. literalinclude:: ../templates/profile_base.html

base.html is the base file that contains the Bootstrap files and layout.
The blocks are filled in by template files that extend this file.

.. literalinclude:: ../templates/base.html

Model
^^^^^

This is the Profile model that we have been using.

.. literalinclude:: ../main/models.py
   :pyobject: Profile

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

