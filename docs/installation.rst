.. highlight:: bash

================
Installation
================

Stable Release
--------------

Install DevSeeker via pip:

.. code-block:: console

   $ python -m pip install devseeker

Development Installation
------------------------

Clone the repository and install dependencies:

.. code-block:: console

   $ git clone https://github.com/iBz-04/devseeker.git
   $ cd devseeker
   $ poetry install --extras doc
   $ poetry shell

Configuration
-------------

DevSeeker requires an OpenAI API key. Set it as follows:

.. code-block:: console

   $ export OPENAI_API_KEY=your_api_key

Or create a `.env` file in the project root with:

   OPENAI_API_KEY=your_api_key 