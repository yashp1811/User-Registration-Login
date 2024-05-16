

# User Registration & Login System

This project implements a secure user registration and login system using Flask for the backend, PostgreSQL for the database, and HTML/CSS/JavaScript for the frontend.

## Features

- **Registration**: Users can register with their email, username, and password. An OTP is sent to their email for verification.
- **OTP Verification**: Users verify their email using the OTP sent during registration.
- **Login**: Registered users can log in with their email/username and password.
- **Session Management**: User sessions are managed securely, and session tokens are issued upon successful login.
- **Welcome Page**: Upon login, users are redirected to a welcome page displaying their username and email.
- **Logout**: Users can log out to end their session.

## Setup

1. **Clone the repository**:

```bash
git clone https://github.com/yourusername/user-registration-login.git
```

2. **Install dependencies**:

```bash
cd user-registration-login
pip install -r requirements.txt
```

3. **Database Setup**:

   - Install and configure PostgreSQL.
   - Create a database named `your_database_name`.
   - Update the database connection URI in `config.py`.

4. **Run the application**:

```bash
python app.py
```

The application will be running at [http://localhost:5000](http://localhost:5000).

## Configuration

- Update `config.py` with your database connection URI, email settings, and any other configuration parameters.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

