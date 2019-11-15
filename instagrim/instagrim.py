from flask import (Blueprint, g, redirect, render_template, session,
                   request, current_app, flash, url_for, send_from_directory)
from werkzeug import secure_filename

import os
import hashlib

from instagrim.db import get_db

bp = Blueprint('instagrim', __name__, url_prefix='')

@bp.route('/')
def show_entries():
    # TODO Get all posts from database
    # db = get_db()
    # c = db.execute("SELECT ...")
    # entries = c.fetchall()
    entries = []
    return(render_template('show_entries.html', entries=entries))

@bp.route('/show/<int:id>')
def show_entry(id):
    # TODO Get a single post from the database
    # db = get_db()
    # c = db.execute("SELECT ...")
    # entry = c.fetchone()
    entry = []
    return(render_template('show_entry.html', entry=entry))

@bp.route('/images/<path:filename>')
def image_file(filename):
    """ Serve user uploaded images during development. """
    return send_from_directory(current_app.config['STORAGE_DIR'], filename)
    

@bp.route('/add', methods=['POST', 'GET'])
def add_entry():

    if not session.get('logged_in'):
        # If the user is not logged in do not display the page
        # but redirect to the login page with an error
        flash("Login required.", "error")
        return(redirect(url_for('login')))

    if request.method == 'POST':

        if 'file' not in request.files:
            # If no file was posted redirect back with error
            flash("No file selected for upload.", "error")
            return redirect(url_for('add_entry'))

        file=request.files['file']
        if file.filename == '':
            # If filename is empty redirect back with an error
            flash("Invalid image file.", "error")
            return redirect(url_for('add_entry'))
        
        else:
            # Everthing is fine, make the post 

            # Save the uploaded to harddisk
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['STORAGE_DIR'], filename))

            # Save the message and filename to the database
            # TODO Create a database table for saving posts
            # TODO Maybe check whether the users message is empty
            # db = get_db()
            # db.execute("INSERT ...")
    
            flash('New post saved', 'info')
            # Redirect to show the new post
            return(redirect(url_for('instagrim.show_entries')))

    # If no data was posted show the form
    return(render_template('add_entry.html'))


@bp.route('/logout')
def logout():
    """Logs user out"""
    session.pop('logged_in', None)
    flash('You were logged out.','info')
    return redirect(url_for('show_entries'))


@bp.route('/register', methods=['POST', 'GET'])
def register():
    """Registers a new user"""
    # If we receive form data register new user
    if request.method == 'POST':

        # TODO Check if username is available
        #flash("Username '{}' already taken".format(request.form['username']), 'error')

        # TODO Check if the two passwords match
        # flash("Passwords do not match, try again.", 'error')

        # TODO Maybe check if the password is a good one?
        # flash("Password is too weak, try again.", 'error')

        # If all is well create the user
        # TODO See previous TODOs
        hashed_password = hashlib.sha256(request.form['password1'].encode()).hexdigest()
        db=get_db()
        db.execute("INSERT INTO users (username, password) VALUES (?,?)",
                   (request.form['username'], hashed_password))
        db.commit()
        flash("User '{}' registered, you can now log in.".format(request.form['username']), 'info')
        
        return redirect(url_for('instagrim.login'))


    # If we receive no data just show the registration form
    else:
        return render_template('register.html')




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

        # TODO: Check if the passwords match
        print(user['password'])
        # flash('Invalid password.', 'error')

        # If everything is okay, log in the user 
        # TODO: See the previoius TODOs
        session['logged_in'] = True
        session['username'] = user['username']
        session['user_id'] = user['id']
        flash('You were logged in.', 'info')

        return redirect(url_for('instagrim.show_entries'))

    return render_template('login.html')



