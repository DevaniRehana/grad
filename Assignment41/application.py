# -*- coding: utf-8 -*-
"""
#Author Harish Kamuju
#UTA ID : 1001120930
#Section : 003 (6:00PM to 8:00PM)
#Assignment : 4
Created on Sat Jun 20 03:55:27 2015

"""
# Import the SDK

from __future__ import unicode_literals
import os
import pprint
import StringIO

from flask import Flask
from flask import request

app = Flask(__name__)


@app.route("/")
def echo():
    stream = StringIO.StringIO()
    indent = int(os.environ.get('PRINT_INDENT', 1))
    pprint.pprint(request.environ, indent=indent, stream=stream)
    return stream.getvalue()


def main():
    app.run(
        host=os.environ.get('HTTP_HOST', '0.0.0.0'),
        port=int(os.environ.get('HTTP_PORT', 80)),
        debug=int(os.environ.get('DEBUG', 0)),
    )

if __name__ == "__main__":
    main()