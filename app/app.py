from flask import Flask, flash, render_template, redirect, request, session, url_for
import os
import configparser
import mysql.connector
import pymysql

app = Flask(__name__)
app.secret_key = os.urandom(24)

config = configparser.ConfigParser()
config.read('config.ini')

DB_HOST = config['database']['host']
DB_PORT = int(config['database']['port'])
DB_USER = config['database']['user']
DB_PASS = config['database']['password']
DB_NAME = config['database']['name']

def is_database_connected():
    # Return True if connected, False otherwise
    try:
        # Create a connection object
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )

        # Check if the connection is successful
        if conn.is_connected():
            conn.close()
            return True
        else:
            return False

    except ImportError:
        return False
    except Exception as e:
        print(f"Error connecting to the database: {str(e)}")
        return False


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if is_database_connected():
        # If the database is connected, flash a message and redirect to home
        flash('The master database is already set up.')
        return redirect(url_for('home'))
    # Initialize setup stage if database not setup yet
    if 'setup_stage' not in session:
        session['setup_stage'] = 1
    
    if request.method == 'POST':
        if session['setup_stage'] == 1:
            # Process and validate database info, then test connection
            session['db_info'] = request.form
            debug_message = 'DB Info: ' + ', '.join(f'{key}: {value}' for key, value in session['db_info'].items())
            flash(debug_message, 'debug')
            # use mysql.connector python library to test the connection with the user supplied data.

            # If successful, move to next stage
            session['setup_stage'] = 2
            return redirect(url_for('setup'))

        elif session['setup_stage'] == 2:
            # process IMAP server info
            session['imap_info'] = request.form
            debug_message = 'IMAP Info: ' + ', '.join(f'{key}: {value}' for key, value in session['imap_info'].items())
            flash(debug_message, 'debug')
            session['setup_stage'] = 3
            return redirect(url_for('setup'))

        elif session['setup_stage'] == 3:
            # Process user account creation
            session['account_info'] = request.form
            debug_message = 'Account Info: ' + ', '.join(f'{key}: {value}' for key, value in session['account_info'].items())
            flash(debug_message, 'debug')
            return redirect(url_for('setup_complete'))

    return render_template('setup.html', header_title=f"Setup: IMAP Monitor Stage {session['setup_stage']}", stage=session['setup_stage'])

@app.route('/setup_complete')
def setup_complete():
    # Process final stage data and complete setup
    # Optionally, clear the session here
    return 'Setup Complete!'


@app.route('/')
def home():
    return render_template('index.html', header_title='Main Menu: IMAP Monitor')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8082)
