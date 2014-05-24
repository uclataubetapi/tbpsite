.. tbpsite documentation master file, created by
   sphinx-quickstart on Fri May 23 16:34:17 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to tbpsite's documentation!
===================================

Tutorial:

Let's start from the top. Say the user wants to look at their profile and they click on the link https://tbp.seas.ucla.edu/profile/.
Django will receive the request and will pass it to a function that takes a request and returns HTML (a view). Django will look in the tbpsite/urls.py file to see what function to call.

tbpsite/urls.py:

.. literalinclude:: ../tbpsite/urls.py
   :emphasize-lines: 24, 39

Django will match the profile portion of the url with r'^profile/$' and will call the profile_view function in the main.views module.

main/views.py:

.. literalinclude:: ../main/views.py
   :pyobject: profile_view

The view calls this helper function to inject tab information that is used to render the tabs on the profile page.

.. literalinclude:: ../main/views.py
   :pyobject: render_profile_page

This helper function calls a similar function to inject navbar information. This function should be called by every view.

.. literalinclude:: ../common.py
   :pyobject: render

Which finally renders the template file.

.. literalinclude:: ../templates/profile.html

profile.html extends profile_base.html which inserts the HTML for the profile tabs.

.. literalinclude:: ../templates/profile_base.html

base.html is the base file that contains the Bootstrap files and layout.

.. literalinclude:: ../templates/base.html

This is the Profile model that we have been using.

.. literalinclude:: ../main/models.py
   :pyobject: Profile

Contents:

.. toctree::
   :maxdepth: 2

   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

