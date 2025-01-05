var wrapper = document.querySelector('.wrapper');
var signuplink = document.querySelector('.signup-link');
var loginlink = document.querySelector('.login-link');
signuplink.onclick = () =>{
wrapper.classList.add("active");
}
loginlink.onclick = () =>{
wrapper.classList.remove("active");
}
    // Show modal when 'Forgot Password' is clicked
document.getElementById("forgot-password-link").onclick = function() {
document.getElementById("forgot-password-modal").style.display = "block";
};

// Close modal when 'X' is clicked
document.getElementById("close-modal").onclick = function() {
document.getElementById("forgot-password-modal").style.display = "none";
};

// AJAX form submission for forgot password
document.getElementById("forgot-password-form").onsubmit = function(e) {
e.preventDefault();  // Prevent page reload

// Gather form data
var email = document.getElementById("email").value;

// Make an AJAX POST request to submit the email
var xhr = new XMLHttpRequest();
xhr.open("POST", "{{ url_for('login.forgot_password') }}", true);
xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

xhr.onload = function() {
    if (xhr.status === 200) {
        alert("Password reset link has been sent to your email.");
        document.getElementById("forgot-password-modal").style.display = "none";  // Close modal
    } else {
        alert("Error: Could not send password reset link.");
    }
};

xhr.send("email=" + encodeURIComponent(email));
};
