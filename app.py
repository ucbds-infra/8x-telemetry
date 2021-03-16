import aiohttp
import asyncio
import async_timeout
import base64
import json
import os
import time
import sqlite3
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.escape
import tornado.options
import logging
import traceback
import pandas as pd
from time import gmtime, strftime
from hashlib import sha1
from jupyterhub.services.auth import HubAuthenticated
from lxml import etree
from oauthlib.oauth1.rfc5849 import signature, parameters
from sqlite3 import Error
from hash_dict import hash_dict

prefix = os.environ.get('JUPYTERHUB_SERVICE_PREFIX', '/')
ERROR_FILE = "tornado_errors.csv"
ERROR_PATH = "tornadoerrors"

def create_table(db_file, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return: conn: connection to db
    """
    global conn
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute(create_table_sql)
        print(sqlite3.version)
    except Error as e:
        print(e)

def write_info(grade_info, conn):
    sql_cmd = """
    INSERT INTO telemetry(user, question, answer, results, correct, assignment, section, timestamp)
    VALUES (?,?,?,?,?,?,?,?)
    """
    try:
        # context manager here takes care of conn.commit()
        with conn:
            conn.execute(sql_cmd, grade_info)
            conn.commit()
    except Error as e:
        print(e)
        print("Error inserting into database for the following record")
        print(grade_info)



class GoferHandler(HubAuthenticated, tornado.web.RequestHandler):

    async def get(self):
        print("Received request")
        self.write("This is a post only page. You probably shouldn't be here!")
        self.finish()

    async def post(self):
        """Accept notebook submissions, saves, then grades them"""
        user_model = self.get_current_user()
        try:
            user_id = hash_dict(user_model)
        except TypeError:
            user_id = 0    # handle issues with null user_models or edge cases
        print("Received submission from %s" % user)
        print(self.request.body.decode("utf-8"))
        req_data = tornado.escape.json_decode(self.request.body)

        question = req_data["question"]
        answer = str(req_data["answer"])
        results = str(req_data["results"])
        correct = bool(req_data["correct"])
        assignment = req_data["assignment"]
        section=req_data["section"]

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))

        # Let user know their submission was received
        self.write("User submission has been received. Grade will be posted to the gradebook once it's finished running!")
        self.finish()
        write_info((user_id, question, answer, results, correct, assignment, section, timestamp), conn)



if __name__ == '__main__':
    create_table_sql = """ CREATE TABLE IF NOT EXISTS telemetry (
        user text,
        question text NOT NULL,
        answer text NOT NULL,
        results text NOT NULL,
        correct boolean NOT NULL,
        assignment text NOT NULL,
        section text NOT NULL,
        timestamp text NOT NULL
    ); """
    create_table("/share/telemetry.db", create_table_sql)

    tornado.options.parse_command_line()
    app = tornado.web.Application([(r"/", GoferHandler)])

    port = 10101
    app.listen(port)
    print("listening on port {}".format(port))

    tornado.ioloop.IOLoop.current().start()
