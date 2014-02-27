txsyncml
========

Limited SyncML 1.1 server.
Only implements the "Refresh sync from client only".

As per the docs (chapter 6.3)::

    The 'refresh sync from client only' is a synchronization type in
    which the client sends all its data from a database to the server
    (i.e., exports). The server is expected to replace all data in the
    target database with the data sent by the client. I.e., this means
    that the client overwrites all data in the server database.


|travis|_ |coveralls|_

::

    $ virtualenv ve
    (ve)$ pip install -e .
    (ve)$ twistd txsyncml --help

.. |travis| image:: https://travis-ci.org/smn/txsyncml.png?branch=develop
.. _travis: https://travis-ci.org/smn/txsyncml

.. |coveralls| image:: https://coveralls.io/repos/smn/txsyncml/badge.png?branch=develop
.. _coveralls: https://coveralls.io/r/smn/txsyncml

