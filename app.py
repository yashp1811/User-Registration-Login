from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import bcrypt
import re
from datetime import datetime, timedelta
import string

app = Flask(__name__)
app.secret_key = '2696ddbe71cb7b47a5eb694086d397da'

conn = psycopg2.connect(
    dbname="registration",
    user="your_username",
    password="your_password",
    host="localhost"
)

otp_data = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        

        if password != confirm_password:
            return "Passwords do not match", 400

        if not validate_email(email):
            return "Invalid email format", 400

        if user_exists(email, username):
            return "User with same email or username already exists", 400

        hashed_password = hash_password(password)
        
        otp = generate_otp()

        cur = conn.cursor()
        cur.execute("INSERT INTO userstest (email, username, password, email_verified, otp) VALUES (%s, %s, %s, %s, %s)", (email, username, hashed_password, False, otp))
        conn.commit()
        cur.close()

        session['email'] = email  # Store email in session for OTP verification
        send_otp(email, otp)  # Pass the generated OTP to send_otp function

        return redirect(url_for('otp_verification'))

    return render_template('register.html')


# Assuming the OTP validity period is 1 minute
OTP_VALIDITY_PERIOD = timedelta(minutes=1)

@app.route('/otp_verification', methods=['GET', 'POST'])
def otp_verification():
    if request.method == 'POST':
        email = session.get('email')
        if not email:
            return redirect(url_for('register'))  # Redirect to registration page if email is not in session

        otp_entered = request.form['otp']

        # Fetch the OTP and its creation time from the database for the user's email
        cur = conn.cursor()
        cur.execute("SELECT otp, created_at, email_verified FROM userstest WHERE LOWER(email) = LOWER(%s)", (email,))
        result = cur.fetchone()

        if result:
            stored_otp, created_at, email_verified = result
            current_time = datetime.now()

            # Check if OTP is within validity period
            if current_time - created_at > OTP_VALIDITY_PERIOD:
                return "OTP expired, please request a new one", 400

            if not email_verified:
                if otp_entered == stored_otp:
                    # Mark email as verified in the database
                    cur.execute("UPDATE userstest SET email_verified = %s, otp = NULL WHERE LOWER(email) = LOWER(%s)", (True, email))
                    conn.commit()
                    cur.close()

                    return redirect(url_for('login'))  # Redirect to login page after successful verification
                else:
                    return "Invalid OTP", 400
            else:
                return "Email already verified", 400
        else:
            return "OTP not found or user not registered", 400

    return render_template('otp_verification.html')



@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    otp_entered = request.form['otp']
    email = session.get('email')

    # Fetch the OTP from the database for the provided email (case-insensitive)
    cur = conn.cursor()
    cur.execute("SELECT otp, email_verified FROM userstest WHERE LOWER(email) = LOWER(%s)", (email,))

    result = cur.fetchone()
    cur.close()

    if result:
        stored_otp, email_verified = result
        
        if not email_verified:
            if otp_entered == stored_otp:
                # Mark email as verified in the database
                cur = conn.cursor()
                cur.execute("UPDATE userstest SET email_verified = %s, otp = NULL WHERE LOWER(email) = LOWER(%s)", (True, email))
                conn.commit()
                cur.close()
                
                return redirect(url_for('login'))
            else:
                return "Invalid OTP", 400
        else:
            return "Email already verified", 400
    else:
        return "OTP not found or user not registred", 400
    
                        

@app.route('/resend_otp', methods=['GET', 'POST'])
def resend_otp():
    email = session.get('email')

    if email:
        # Check if the user has requested OTP too frequently (e.g., once every 30 seconds)
        last_otp_request_time = otp_data.get(email)
        if last_otp_request_time and datetime.now() - last_otp_request_time < timedelta(seconds=30):
            return jsonify({'error': 'Please wait before requesting a new OTP'}), 400

        # Generate a new OTP
        new_otp = generate_otp()

        # Update the OTP and its creation time in the database
        cur = conn.cursor()
        cur.execute("UPDATE userstest SET otp = %s, created_at = %s WHERE LOWER(email) = LOWER(%s)", (new_otp, datetime.now(), email))
        conn.commit()
        cur.close()

        # Update last OTP request time
        otp_data[email] = datetime.now()

        # Send the new OTP to the user's email
        send_otp(email, new_otp)
        print("hello")
        

        return jsonify({'message': 'OTP resent successfully'}), 200
    
    else:
        
        return jsonify({'error': 'Email not found in session'}), 400



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form['email']
        password = request.form['password']

        if validate_login(email_or_username, password):
            session['email'] = email_or_username
            return redirect(url_for('welcome'))
        else:
            return "Invalid credentials", 400

    return render_template('login.html')

@app.route('/welcome')
def welcome():
    if 'email' in session:
        user_info = get_user_info()
        return render_template('welcome.html', username=user_info['username'], email=user_info['email'])
    else:
        return redirect(url_for('login'))

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('email', None)
    return render_template('login.html')

@app.route('/user_info')
def user_info():
    if 'email' in session:
        user_info = get_user_info()
        if user_info:
            return jsonify({'username': user_info['username'], 'email': user_info['email']})
    return jsonify({'message': 'User not logged in'}), 401

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def user_exists(email, username):
    cur = conn.cursor()
    cur.execute("SELECT * FROM userstest WHERE email = %s OR username = %s", (email, username))
    result = cur.fetchone()
    cur.close()
    return result is not None

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def generate_otp():
    # Generate a random 6-digit OTP
    return ''.join(random.choices(string.digits, k=6))

def send_otp(email, otp):
    from_email = 'rootyash@outlook.com'
    to_email = email
    subject = 'Your OTP for Registration'
    body = f'Your OTP for registration is: {otp}'

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
 
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.office365.com', 587)
    server.starttls()
    server.login(from_email, 'root@1234567890')
    text = msg.as_string()
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

def validate_login(email_or_username, password):
    cur = conn.cursor()
    cur.execute("SELECT * FROM userstest WHERE email = %s OR username = %s", (email_or_username, email_or_username))
    user = cur.fetchone()
    cur.close()

    if user:
        hashed_password = user[2]
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            return True
    return False

def get_user_info():
    if 'email' in session:
        cur = conn.cursor()
        cur.execute("SELECT username, email FROM userstest WHERE email = %s", (session['email'],))
        user_info = cur.fetchone()
        cur.close()
        if user_info:
            return {'username': user_info[0], 'email': user_info[1]}
    return None

if __name__ == '__main__':
    app.run(debug=True)
