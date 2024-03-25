# Author(s): Parth Patel

import datetime

from flask import Flask, render_template, redirect, url_for, session, request
import database
from routes import website

@website.route('/quiz_trends')
def quiz_trends():
    render_template('quiz_trends.html')
