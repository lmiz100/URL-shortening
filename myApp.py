
from flask import Flask, render_template, redirect, request, url_for,flash, send_from_directory
from form import MyForm
import sqlite3 as sql
from itertools import product
import string
import functools 
import operator
import time
from datetime import datetime, timedelta
from argparse import ArgumentParser
import os     



app = Flask(__name__)
# create DBs
conn = sql.connect('urls_database.db')
conn.execute('CREATE TABLE IF NOT EXISTS urls (long_url TEXT PRIMARY KEY, url_suffix TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS requests (request_time TEXT, long_url TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS bad_requests (request_time TEXT, url_suffix TEXT)')
conn.close()

app.config['SECRET_KEY'] = '2</Z2{`k.Qr1t)b'


# convert chars tuple to string
def tuple2string(tup): 
    str = functools.reduce(operator.add, (tup)) 
    return str


chars = string.ascii_lowercase + string.digits
# create product generator for unique suffixes
suffix_gen = product(chars, repeat=1)
counter = 1


# reserved pages
server_suffix = ['home', 'stats']
first_enter = True
# app main page
@app.route('/', methods=['POST', 'GET'])
def home():
    global suffix_gen, counter, first_enter, server_suffix

    suffix = "uninitial"
    form = MyForm()

    # checks if url from form is legal
    if form.validate() == False:
        if not first_enter and form.long_url._value != '' :
            flash('Illegal URL, try again')
        first_enter = False
        return render_template('home.html', form = form)
    else:
        try:
            url = request.form['long_url']
         
            with sql.connect('urls_database.db') as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM urls WHERE long_url='{}'".format(url))
                rec = cur.fetchone()

                # for bonus task 1
                cur.execute("INSERT INTO requests (request_time, long_url) VALUES (datetime('now'),'{}')".format(url) )
 
                if rec is not None:     # long_url exists
                    suffix = rec[1]
                else:   # url doesn't in db yet
                    try:
                        while True:
                            suffix = tuple2string(next(suffix_gen))
                            # verify that suffix is unique
                            if suffix in server_suffix: continue
                            if cur.execute("SELECT * FROM urls WHERE url_suffix='{}'".format(suffix)).fetchone() is None:
                                break
                        
                    except StopIteration:
                        counter += 1
                        suffix_gen = product(chars, repeat= counter)
                        while True:
                            suffix = tuple2string(next(suffix_gen))
                            if suffix in server_suffix: continue
                            # verify that suffix is unique
                            if cur.execute("SELECT * FROM urls WHERE url_suffix='{}'".format(suffix)).fetchone() is None:
                                break
                    
                    cur.execute("INSERT INTO urls (long_url, url_suffix) VALUES ('{}','{}')".format(url, suffix) )
                    con.commit()

        except Exception as e:
            con.rollback()
            return "error: {}".format(e)
      
        finally:
            first_enter = True
            con.close()
            return redirect('http://localhost:5000/result={}'.format(suffix))

            

# page after a successful redirection request
@app.route('/result=<suffix>')
def result(suffix):
    global first_enter
    first_enter = True

    res = 'http://localhost:5000/' + suffix
    with sql.connect('urls_database.db') as con:
        cur = con.cursor()
        rec = cur.execute("SELECT * FROM urls WHERE url_suffix='{}'".format(suffix)).fetchone()
        # suffix didn't allocated - handle as bad request 
        if rec is None:
            return redirect('http://localhost:5000/{}'.format(suffix))

        url = rec[0]

    return render_template("result.html",new_link = res, old_link = url)



# handle favicon
@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')



@app.route('/<page>')
def redirect_page(page):
    global first_enter
    first_enter = True

    with sql.connect('urls_database.db') as con:
        cur = con.cursor()

        cur.execute("SELECT * FROM urls WHERE url_suffix='{}'".format(page))
        rec = cur.fetchone()

        if rec is not None: # if url doesnt exists in DB it return None
            url = rec[0]

            if url.find("http://") != 0 and url.find("https://") != 0:
                url = "http://" + url

            return redirect(url)
        else:
            # for bonus task 1
            cur.execute("INSERT INTO bad_requests (request_time, url_suffix) VALUES (datetime('now'),'{}')".format(page))

    return render_template("pageFault.html", url = 'http://localhost:5000/' + page)



# stats page for bonus 1
@app.route('/stats')
def statics():
    global first_enter
    first_enter = True
    req_min = req_hour = req_day = 0
    badReq_min = badReq_hour = badReq_day = 0

    with sql.connect('urls_database.db') as con:
        cur = con.cursor()
 
        total_urls = cur.execute("SELECT COUNT(*) FROM urls").fetchone()[0]
        total_requests = cur.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
        req_min = cur.execute('''SELECT COUNT(request_time) FROM requests
                     WHERE request_time between datetime('now','-1 minute') and datetime('now')''').fetchone()[0]
        req_hour = cur.execute('''SELECT COUNT(request_time) FROM requests
                     WHERE request_time between datetime('now','-1 hour') and datetime('now')''').fetchone()[0]
        req_day = cur.execute('''SELECT COUNT(request_time) FROM requests
                     WHERE request_time between datetime('now','start of day') and datetime('now')''').fetchone()[0]
        badReq_min = cur.execute('''SELECT COUNT(request_time) FROM bad_requests
                     WHERE request_time between datetime('now','-1 minute') and datetime('now')''').fetchone()[0]
        badReq_hour = cur.execute('''SELECT COUNT(request_time) FROM bad_requests
                     WHERE request_time between datetime('now','-1 hour') and datetime('now')''').fetchone()[0]
        badReq_day = cur.execute('''SELECT COUNT(request_time) FROM bad_requests
                     WHERE request_time between datetime('now','start of day') and datetime('now')''').fetchone()[0]    
     
    return render_template("stats.html", total_urls=total_urls, total_requests = total_requests,req_min=req_min,
        req_hour=req_hour, req_day=req_day, bad_min=badReq_min, bad_hour=badReq_hour, bad_day=badReq_day)



if __name__ == '__main__':
    parser = ArgumentParser(description = 'myApp parser')
    parser.add_argument('-resetDB', '--resetDB', type=int, required=False, default=0, help='1 if want reset (delete) exist DBs')
    args = parser.parse_args()
    exist_table = 0

    # reset DBs if exist
    if args.resetDB == 1:
        with sql.connect('urls_database.db') as con:
            cur = con.cursor()

            exist_table = cur.execute('''SELECT COUNT(*) FROM sqlite_master
			WHERE type='table' AND name='urls' ''').fetchone()[0]
            if exist_table == 1: cur.execute('DROP TABLE urls'); cur.execute('CREATE TABLE IF NOT EXISTS urls (long_url TEXT PRIMARY KEY, url_suffix TEXT)')
            exist_table = cur.execute('''SELECT COUNT(*) FROM sqlite_master
                    	WHERE type='table' AND name='requests' ''').fetchone()[0]
            if exist_table == 1: cur.execute('DROP TABLE requests'); cur.execute('CREATE TABLE IF NOT EXISTS requests (request_time TEXT, long_url TEXT)')
            exist_table = cur.execute('''SELECT COUNT(*) FROM sqlite_master
                    	WHERE type='table' AND name='bad_requests' ''').fetchone()[0]
            if exist_table == 1: cur.execute('DROP TABLE bad_requests'); cur.execute('CREATE TABLE IF NOT EXISTS bad_requests (request_time TEXT, url_suffix TEXT)')


    app.run(debug=True)

