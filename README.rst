Python Korbit
=============

``python-korbit`` is a Korbit API wrapper in Python.

.. image:: https://travis-ci.org/suminb/korbit.svg?branch=master
    :target: https://travis-ci.org/suminb/korbit

.. image:: https://coveralls.io/repos/suminb/korbit/badge.png?branch=master
   :target: https://coveralls.io/r/suminb/korbit?branch=master


Environment Variables
---------------------

You will need to set a few environment variables to make this library work
properly.  A skeleton code is provided in ``provision-dist.sh``. Make a copy
and fill in values. API keys can be issued in https://www.korbit.co.kr/my/api/.

.. code-block::

   cp provision-dist.sh provision.sh
   source provision.sh


API Call Examples
-----------------

This section illustrates how some of the API can be called.

.. code-block:: python

    from korbit.api import get_transactions
    get_transactions()

This will fetch all transactions from the server producing an output as following:

.. code-block::

    [
        {"timestamp":1389678052000,"tid":"22546","price":"569000","amount":"0.01000000"},
        {"timestamp":1389678017000,"tid":"22545","price":"580000","amount":"0.01000000"},
        {"timestamp":1389462921000,"tid":"22544","price":"569000","amount":"0.16348000"},
        {"timestamp":1389462921000,"tid":"22543","price":"570000","amount":"0.20000000"},
        {"timestamp":1389462920000,"tid":"22542","price":"578000","amount":"0.33652000"},
        ...
    ]

Other functions are available and the usage of each function will be gradually added on this documentation in the future.
