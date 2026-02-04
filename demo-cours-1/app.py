from datetime import timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-in-production'
app.permanent_session_lifetime = timedelta(minutes=5)

# Hardcoded user for demo purposes
DEMO_USER = {'username': 'admin', 'password': 'admin'}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Vous devez vous connecter pour acceder a cette page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == DEMO_USER['username'] and password == DEMO_USER['password']:
            session.permanent = True
            session['username'] = username
            flash('Connexion reussie!')
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiants invalides.')

    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session['username'])


@app.post('/logout')
@login_required
def logout():
    session.clear()
    flash('Vous avez ete deconnecte.')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
