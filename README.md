
# Project: URL shortener service

## Description
A full-stack project for URL shortener service.<br />
This service enables registering a “long URL”. e.g. www.somethingverylong.com/1234.html and receiving a “short URL” that will
redirect to it. e.g. localhost/sh54. <br />
This service is similar to the service offered by [tinyurl](https://tinyurl.com/) 
In addition, service's statics available at localhost/stats.


## The databases
Includes two collections:
+ urls: map "long URL"s to "short  URL" allocated suffix. e.g localhost/**suffix** 
+ requests: includes successful redirect requests details (time and long url). 
+ bad_requests: includes failed (bad) redirect requests details (time and url suffix). 
<br />
The databases will create once - at first application's run. 


## Running instructions
+ Add project files (form.py, myApp.py, run.txt, run-and-reset.txt, venv-init.txt, templates folder) to directory.
+ From terminal, enter this directory by `cd <directory path>`.
+ Install python3-venv package (if it's already exist - skip) by `sudo apt install python3-venv`.
+ Venv initialization: run [venv-init.txt](https://github.com/lmiz100/URL-shortening/blob/master/venv-init) script by `./venv-init`.
+ run application: use [run.txt](https://github.com/lmiz100/URL-shortening/blob/master/run) by `./run`.
+ If you want reset DBs, use `./run-and-reset`.
Now, when the app running, enter http://localhost:5000/ from some browser and enjoy the service!


