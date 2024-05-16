document.getElementById('registration-form').addEventListener('submit', function(event) {
    var email = document.getElementById('email').value;
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    var confirmPassword = document.getElementById('confirm-password').value;
    var otp = document.getElementById('otp').value;

    // Email validation
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert('Please enter a valid email address');
        event.preventDefault();
        return;
    }

    // Password match validation
    if (password !== confirmPassword) {
        alert('Passwords do not match');
        event.preventDefault();
        return;
    }

    fetch('/otp_verification', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'otp=' + encodeURIComponent(otp),
    })
    .then(response => {
        if (response.ok) {
            // Redirect to login page after successful OTP verification
            window.location.href = '/login';
        } else {
            // Display error message if OTP verification fails
            return response.text().then(errorMessage => {
                alert(errorMessage);
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while verifying OTP');
    });

    event.preventDefault();

    fetch('/verify_otp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'otp=' + encodeURIComponent(otp),
    })
    .then(response => {
        if (response.ok) {
            // Redirect to login page after successful OTP verification
            window.location.href = '/login';
        } else {
            // Display error message if OTP verification fails
            return response.text().then(errorMessage => {
                alert(errorMessage);
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while verifying OTP');
    });
});


