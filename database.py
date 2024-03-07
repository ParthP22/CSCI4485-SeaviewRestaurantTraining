# This file contains the database connection that will run all throughout user's session.

import sqlite3

conn = sqlite3.connect("./Seaview_DB.db", check_same_thread=False)
