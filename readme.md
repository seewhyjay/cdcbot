# Requirements

## Heroku

### Addons
- ClearDB MySQL

### Buildpacks
- heroku/python
- https://github.com/heroku/heroku-buildpack-google-chrome
- https://github.com/heroku/heroku-buildpack-chromedriver
- https://github.com/heroku/heroku-buildpack-python.git
- https://github.com/heroku/heroku-buildpack-apt.git

### Config Vars (First 2 have to be in order)
- BUILDPACK_URL : git://github.com/heroku/heroku-buildpack-python.git
- CHROMEDRIVER_PATH : /app/.chromedriver/bin/chromedriver
- CLEARDB_DATABASE_URL
- GOOGLE_CHROME_BIN : /app/.apt/usr/bin/google_chrome

# Setup
### conn.py
- Just update and add your credentials accordingly

### Uploading cookies
- Run uploadcookies.py
- Login and do the captcha within a minute, if you fail just rerun
    
### ClearDB Setup
- 'auth' table
![image](MySQLWorkbench_QIm3gX662q.png)
