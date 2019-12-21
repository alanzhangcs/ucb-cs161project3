from flask import *
import database, auth_helper

app = Flask(__name__)

@app.after_request
def disable_xss_protection(response):
    """
    This disables the XSS auditor in Google Chrome which prevents some
    exploits from working.

    DO NOT count this as a vulnerability, we only do it to make finding
    the vulnerabilities easier.
    """
    response.headers['X-XSS-Protection'] = '0'
    return response

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/')
@auth_helper.get_username
def index(username):
    return render_template('index.html', username=username)

@app.route('/login', methods=['GET', 'POST'])
@auth_helper.get_username
def login(username):
    if username:
        return render_template('index.html', username=username, error='Already logged in.')

    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']
    if not username.isalnum():
        return render_template('login.html', error='Bad username!')

    correct = auth_helper.check_login(username, password)
    if not correct:
        return render_template('login.html', error='Incorrect password.')

    session_id = auth_helper.generate_session_id()
    database.execute("INSERT INTO sessions VALUES ('{}', '{}');".format(session_id, username))

    resp = redirect(url_for('wall'))
    resp.set_cookie('SESSION_ID', session_id)
    return resp

@app.route('/logout')
@auth_helper.get_username
@auth_helper.csrf_protect
def logout(username):
    if not username:
        return render_template('index.html', error='Error')

    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('SESSION_ID', '')
    return resp

def make_escaper(replacements):
    def escaper(inp):
        for old, new in replacements.items():
            inp = inp.replace(old, new)
        return inp
    return escaper

escape_sql = make_escaper({
    "'": "''",
    '--': '&ndash;',
    '*': '&#42;',
    ';': ''
    })

escape_html = make_escaper({
    '<': '&lt;',
    '>': '&gt;'
    })

def get_user_info(username):
    pinfo = database.fetchone("SELECT avatar, age FROM users WHERE username='{}';".format(username))
    if not pinfo:
        return '', 0

    avatar = escape_html(pinfo[0])
    age = pinfo[1]
    return avatar, age

@app.route('/wall')
@app.route('/wall/<other_username>')
@auth_helper.get_username
@auth_helper.csrf_protect
def wall(username, other_username=None):
    other_username = other_username or auth_helper.get_username_from_session()
    if not other_username:
        return redirect(url_for('index'))

    other_username = escape_sql(other_username)
    if not auth_helper.is_valid_username(other_username):
        return render_template('no_wall.html', username=other_username)

    db_posts = database.fetchall("SELECT post FROM posts WHERE username='{}';".format(other_username))
    posts = [ post[0] for post in db_posts ]
    avatar, age = get_user_info(other_username)

    return render_template('wall.html', username=username, other_username=other_username, posts=posts, avatar=avatar, age=age)

@app.route('/profile', methods=['GET', 'POST'])
@auth_helper.get_username
@auth_helper.csrf_protect
def profile(username):
    if not username:
        return render_template('login.html', error='Please log in.')

    if request.method == 'GET':
        avatar, age = get_user_info(username)
        avatar = escape_html(escape_sql(avatar))
        age = escape_html(escape_sql(str(age)))
        return render_template('profile.html', username=username, avatar=avatar, age=age)

    username = escape_sql(request.form['username'])
    avatar = escape_html(escape_sql(request.form['avatar']))
    age = escape_html(escape_sql(request.form['age']))
    if avatar.startswith('http://') or avatar.startswith('https://'):
        database.execute("UPDATE users SET avatar='{}' WHERE username='{}';".format(avatar, username))
    database.execute("UPDATE users SET age={} WHERE username='{}';".format(age, username))

    return redirect(url_for('wall'))

@app.route('/post', methods=['GET', 'POST'])
@auth_helper.get_username
@auth_helper.csrf_protect
def post(username):
    if not username:
        return render_template('login.html', error='Please log in.')

    if request.method == 'GET':
        return render_template('post.html', username=username)

    post = escape_sql(request.form['post'])
    database.execute("INSERT INTO posts VALUES ('{}', '{}');".format(username, post))
    return redirect(url_for('wall'))
