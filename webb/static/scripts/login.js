// Fungsi untuk mengenkripsi password menggunakan Caesar cipher
function encryptPassword(password, shift = 3) {
  return password
    .split("")
    .map((char) => {
      // Hanya proses karakter alfabet
      if (char.match(/[a-z]/i)) {
        const code = char.charCodeAt(0);
        const isUpperCase = code >= 65 && code <= 90;
        const base = isUpperCase ? 65 : 97;

        // Aplikasikan pergeseran dan wrap around menggunakan modulo
        return String.fromCharCode(((code - base + shift) % 26) + base);
      }
      // Untuk karakter non-alfabet (angka, simbol), biarkan apa adanya
      return char;
    })
    .join("");
}

// Fungsi untuk mendekripsi password
function decryptPassword(encryptedPassword, shift = 3) {
  // Dekripsi adalah enkripsi dengan shift negatif
  return encryptPassword(encryptedPassword, 26 - shift);
}

// Modifikasi event handler form signup
document.getElementById("signup-form").onsubmit = function (e) {
  e.preventDefault();

  const password = document.getElementById("signup-password").value;
  const encryptedPassword = encryptPassword(password);

  // Sekarang password sudah terenkripsi, bisa dikirim ke server
  console.log("Password terenkripsi:", encryptedPassword);

  // Lakukan AJAX request untuk signup
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/signup", true);
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

  xhr.onload = function () {
    if (xhr.status === 200) {
      alert("Signup berhasil!");
      wrapper.classList.remove("active");
    } else {
      alert("Error: Signup gagal.");
    }
  };

  // Kirim data form termasuk password yang sudah dienkripsi
  const formData = new FormData(e.target);
  formData.set("password", encryptedPassword);
  xhr.send(new URLSearchParams(formData));
};

// Modifikasi event handler form login
document.getElementById("login-form").onsubmit = function (e) {
  e.preventDefault();

  const password = document.getElementById("login-password").value;
  const encryptedPassword = encryptPassword(password);

  // Lakukan AJAX request untuk login
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/login", true);
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

  xhr.onload = function () {
    if (xhr.status === 200) {
      alert("Login berhasil!");
    } else {
      alert("Error: Login gagal.");
    }
  };

  // Kirim data form termasuk password yang sudah dienkripsi
  const formData = new FormData(e.target);
  formData.set("password", encryptedPassword);
  xhr.send(new URLSearchParams(formData));
};

// Mempertahankan kode yang sudah ada untuk navigasi form
var wrapper = document.querySelector(".wrapper");
var signuplink = document.querySelector(".signup-link");
var loginlink = document.querySelector(".login-link");

signuplink.onclick = () => {
  wrapper.classList.add("active");
};

loginlink.onclick = () => {
  wrapper.classList.remove("active");
};

// Kode untuk forgot password tetap sama seperti sebelumnya
document.getElementById("forgot-password-link").onclick = function () {
  document.getElementById("forgot-password-modal").style.display = "block";
};

document.getElementById("close-modal").onclick = function () {
  document.getElementById("forgot-password-modal").style.display = "none";
};

document.getElementById("forgot-password-form").onsubmit = function (e) {
  e.preventDefault();

  var email = document.getElementById("email").value;

  var xhr = new XMLHttpRequest();
  xhr.open("POST", "{{ url_for('login.forgot_password') }}", true);
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

  xhr.onload = function () {
    if (xhr.status === 200) {
      alert("Password reset link has been sent to your email.");
      document.getElementById("forgot-password-modal").style.display = "none";
    } else {
      alert("Error: Could not send password reset link.");
    }
  };

  xhr.send("email=" + encodeURIComponent(email));
};
