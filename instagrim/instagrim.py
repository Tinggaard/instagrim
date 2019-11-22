from flask import (Blueprint, g, redirect, render_template, session,
                   request, current_app, flash, url_for, send_from_directory)
from werkzeug import secure_filename
from datetime import datetime
from secrets import token_urlsafe
import os
import hashlib
import re

from instagrim.post import create_post
from instagrim.db import get_db

bp = Blueprint('instagrim', __name__, url_prefix='')



# If user not authenticated, redirect to all. Else show only followers posts
@bp.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('instagrim.show_entries'))

    return show_entries()



@bp.route('/all')
def show_entries():
    # TODO Get all posts from database
    db = get_db()
    c = db.cursor()
    c = db.execute('''SELECT * FROM posts ORDER BY date DESC''')
    entries = c.fetchall()
    entries = [create_post(entry) for entry in entries]


    return render_template('show_entries.html', entries=entries)

@bp.route('/p/<id>', methods=['POST', 'GET'])
def show_entry(id):

    if request.method == 'POST':

        if not session.get('logged_in'):
            # If the user is not logged in do not display the page
            # but redirect to the login page with an error
            flash("Login required.", "error")
            return redirect(url_for('instagrim.login'))


        # Add like to post
        db = get_db()
        c = db.cursor()

        #If already liked
        c.execute('''SELECT * FROM likes WHERE user_id=? AND post_id=?''',(session.get('user_id'),id))
        if c.fetchone() is not None:
            flash('Already liked post', 'error')
            return redirect(url_for('instagrim.show_entry', id=id))

        # Otherwise, like
        c.execute('''INSERT INTO likes (post_id, user_id) VALUES (?,?)''', (id, 1))
        db.commit()

        flash('Liked post!', 'info')
        return redirect(url_for('instagrim.show_entry', id=id))



    db = get_db()
    c = db.cursor()


    # c.execute('''SELECT posts.id, posts.user_id, posts.url, posts.message, posts.date,\
    #     likes.user_id FROM posts INNER JOIN likes ON likes.post_id=?''', (id, ))
    # c.execute('''SELECT likes.user_id FROM posts INNER JOIN likes ON likes.post_id = ?''', (id,))

    # Get post
    c.execute('''SELECT * FROM posts WHERE id=?''', (id, ))
    entry = c.fetchone()
    # Get likes
    c.execute('''SELECT * FROM likes WHERE post_id=?''', (id,))
    likes = len(c.fetchall())

    entry = create_post(entry, likes)


    return render_template('show_entry.html', entry=entry)


# Static file handler
@bp.route('/images/<path:filename>')
def image_file(filename):
    """ Serve user uploaded images during development. """
    return send_from_directory(current_app.config['STORAGE_DIR'], filename)


# Add entry
@bp.route('/add', methods=['POST', 'GET'])
def add_entry():

    if not session.get('logged_in'):
        # If the user is not logged in do not display the page
        # but redirect to the login page with an error
        flash("Login required.", "error")
        return redirect(url_for('instagrim.login'))

    if request.method == 'POST':


        #If no file selected
        if 'file' not in request.files:
            # If no file was posted redirect back with error
            flash("No file selected for upload.", "error")
            return redirect(url_for('instagrim.add_entry'))

        file = request.files['file']

        # current_app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

        #If no file selected
        if file.filename == '':
            # If filename is empty redirect back with an error
            flash("Invalid image file.", "error")
            return redirect(url_for('instagrim.add_entry'))


        # If not valid imagefile
        elif os.path.splitext(file.filename)[1] not in ['.jpg', '.jpeg', '.png', '.gif']:
            flash("Invalid image file.", "error")
            return redirect(url_for('instagrim.add_entry'))

        #Too long message
        elif len(request.form['message']) > 1000:
            flash('Message cannot exceed 1000 characters.', "error")
            return redirect(url_for('instagrim.add_entry'))



        # Everthing is fine, make the post
        else:

            # Save the uploaded to harddisk
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['STORAGE_DIR'], filename))

            # Rename file in case of dublicates
            os.chdir('instance\\images')
            url_id = token_urlsafe(8)
            ext = os.path.splitext(file.filename)[1]
            filename = os.rename(filename, url_id + ext)
            os.chdir('..\\..')

            filename = url_id + ext


            # Save the message and filename to the database
            db = get_db()
            c = db.cursor()

            c.execute('''INSERT INTO posts (id, user_id, url, message, date) VALUES (?,?,?,?,?)''',
                (url_id, session.get('user_id'), filename, request.form['message'], round(datetime.now().timestamp())))

            db.commit()

            flash('New post saved', 'info')
            # Redirect to show the new post
            return redirect(url_for('instagrim.show_entries'))

    # If no data was posted show the form
    return render_template('add_entry.html')

# Logout
@bp.route('/logout')
def logout():
    """Logs user out"""
    session.pop('logged_in', None)
    flash('You were logged out.','info')
    return redirect(url_for('instagrim.show_entries'))

# Register new user
@bp.route('/register', methods=['POST', 'GET'])
def register():
    """Registers a new user"""
    # If we receive form data register new user
    if request.method == 'POST':

        usr = request.form['username']
        pwd1 = request.form['password1']
        pwd2 = request.form['password2']

        db = get_db()
        c = db.cursor()

        # Check if username is available?
        # Should also return an error as username column is unique

        #Check if username not provided
        if not len(usr):
            flash('Username not provided', 'error')
            return render_template('register.html')

        # Check length of username
        if len(usr) > 20:
            flash('Username cannot exceed 20 characters', 'error')
            return render_template('register.html')

        #check if invalid characters
        if not re.fullmatch('[a-zA-Z0-9._]*', usr):
            flash('Username can only contain a-z, A-Z, 0-9 _ and .', 'error')
            return render_template('register.html')


        #check if username is taken
        c.execute('''SELECT * FROM users WHERE username=? COLLATE NOCASE''', (usr, ))
        if c.fetchone() is not None:
            flash("Username '{}' already taken".format(usr), 'error')
            return render_template('register.html')


        # Check if the two passwords match
        if pwd1 != pwd2:
            flash("Passwords do not match, try again.", 'error')
            return render_template('register.html')


        #TODO: Remember to enable this!
        # if len(pwd1) < 8:
        #     flash("Password is too weak, try again.", 'error')
        #     return render_template('register.html')


        # If all is well create the user
        hashed_password = hashlib.sha256(pwd1.encode()).hexdigest()

        c.execute("INSERT INTO users (username, password) VALUES (?,?)",
                   (request.form['username'], hashed_password))
        db.commit()
        flash("User '{}' registered, you can now log in.".format(request.form['username']), 'info')

        return redirect(url_for('instagrim.login'))


    # If we receive no data just show the registration form
    else:
        return render_template('register.html')



# Login
@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in"""

    # If we receive form data try to log the user in
    if request.method == 'POST':

        # Connect to the database
        db = get_db()

        # Retrieve the users password from database (and check if user exist)
        c = db.execute("SELECT * FROM users WHERE username=?", (request.form['username'],))
        user = c.fetchone()

        # Check if a user was found
        if user is None:
            flash('User not found.', 'error')
            return render_template('login.html')


        if user['password'] != hashlib.sha256(request.form['password'].encode()).hexdigest():
            flash('Invalid password.', 'error')
            return render_template('login.html')


        session['logged_in'] = True
        session['username'] = user['username']
        session['user_id'] = user['id']
        flash('You were logged in.', 'info')

        return redirect(url_for('instagrim.show_entries'))

    return render_template('login.html')

# Show users posts
@bp.route('/u/<user>')
def show_user(user):

    db = get_db()
    c = db.cursor()

    c.execute('''SELECT * FROM users WHERE username=? COLLATE NOCASE''', (user, ))
    id = c.fetchone()['id']


    c = db.execute('''SELECT * FROM posts WHERE user_id=? ORDER BY date DESC''', (id,))
    entries = c.fetchall()
    entries = [create_post(entry) for entry in entries]


    return render_template('show_user.html', entries=entries, username=user)





#Used to convert from EPOCH to the correct time format.
@bp.app_template_filter('ctime')
def ctime(s):
    now = round(datetime.now().timestamp())
    delta = now-s

    #Check time ago since post was made.
    if delta > 60*60*24*7:
        weeks = delta // (60*60*24*7)
        return str(weeks) + 'w'

    elif delta > 60*60*24:
        days = delta // (60*60*24)
        return str(days) + 'd'

    elif delta > 60*60:
        hours = delta // (60*60)
        return str(hours) + 'h'

    elif delta > 60:
        minutes = delta // 60
        return str(minutes) + 'm'

    else:
        return str(delta) + 's'
