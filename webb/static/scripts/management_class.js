// Daftar nama siswa tetap
const students = [
  "Mylovia Mahesa Ayu",
  "Abdullah Al-Firdaus Nuzula",
  "Syafira Najema Putri Anisa",
  "Rizki Piji Fathoni",
  "Fio Ulaa Octariyanti",
  "Alfin Jayadi",
  "Dimas Rafi Izzulhaq",
  "Rizqi Aqilah Cahyani Y",
  "Muhammad Raffi Fahrezi",
  "Cyriani Neuman Rebo",
  "Ketut Shridhara",
  "Nazril Ravi Pratama",
  "Halilatunnisa",
  "Naura Kanaya Putri Masruri",
  "Daffa Ahmad Pangreksa",
  "Faishal Muflih Irfanu Tsaqib",
  "Elvira Tiara Suci Tambunan",
  "Illona Anindya",
];

let kasData = [];

// Inisialisasi data siswa
function initializeData() {
  const savedData = JSON.parse(localStorage.getItem("kasData"));
  if (savedData && Array.isArray(savedData)) {
    kasData = savedData;
  } else {
    kasData = students.map((Name) => ({
      Name,
      status: "Belum Bayar",
      nominal: 0,
    }));
    localStorage.setItem("kasData", JSON.stringify(kasData));
  }
}

// Tambahkan nama siswa ke tabel
function initializeTable() {
  const tableBody = document.querySelector("#kasTable tbody");
  tableBody.innerHTML = ""; // Kosongkan tabel sebelum menambahkan data baru

  kasData.forEach((student, index) => {
    const row = document.createElement("tr");
    row.innerHTML = `
            <td>${student.Name}</td>
            <td>
                <select id="status-${index}" class="status-select" onchange="updateStatus(${index})">
                    <option value="Belum Bayar" ${
                      student.status === "Belum Bayar" ? "selected" : ""
                    }>Belum Bayar</option>
                    <option value="Sudah Bayar" ${
                      student.status === "Sudah Bayar" ? "selected" : ""
                    }>Sudah Bayar</option>
                </select>
            </td>
            <td>
                <input 
                    type="number" 
                    id="nominal-${index}" 
                    value="${student.nominal}" 
                    oninput="updateNominal(${index})" 
                    ${student.status === "Belum Bayar" ? "disabled" : ""} 
                    style="text-align: center;">
            </td>
        `;
    tableBody.appendChild(row);
    updateRowColor(index); // Set warna awal berdasarkan status
  });
}

// Perbarui status pembayaran
function updateStatus(index) {
  const statusDropdown = document.getElementById(`status-${index}`);
  const nominalInput = document.getElementById(`nominal-${index}`);
  const status = statusDropdown.value;

  // Perbarui data status
  kasData[index].status = status;

  if (status === "Belum Bayar") {
    kasData[index].nominal = 0;
    nominalInput.value = 0;
    nominalInput.disabled = true; // Nonaktifkan input jika belum bayar
  } else if (status === "Sudah Bayar") {
    nominalInput.disabled = false; // Aktifkan input jika sudah bayar
  }

  updateRowColor(index);
  updateTotalKas();
  saveData();
}

// Perbarui nominal pembayaran
function updateNominal(index) {
  const nominalInput = document.getElementById(`nominal-${index}`);
  const nominal = parseInt(nominalInput.value) || 0;

  // Validasi nilai nominal
  if (nominal < 0) {
    alert("Nominal tidak boleh kurang dari 0!");
    nominalInput.value = 0;
    kasData[index].nominal = 0;
  } else {
    kasData[index].nominal = nominal;
  }

  updateTotalKas();
  saveData();
}

// Hitung total kas
function updateTotalKas() {
  const total = kasData.reduce((sum, student) => sum + student.nominal, 0);
  document.getElementById("totalKas").textContent = total;
}

// Perbarui warna kolom status pembayaran berdasarkan status
function updateRowColor(index) {
  const statusDropdown = document.getElementById(`status-${index}`);
  const status = kasData[index].status;

  if (status === "Sudah Bayar") {
    statusDropdown.classList.remove("status-belum");
    statusDropdown.classList.add("status-sudah");
  } else {
    statusDropdown.classList.remove("status-sudah");
    statusDropdown.classList.add("status-belum");
  }
}

// Cetak laporan dalam format PDF
function generatePDFReport() {
  const data = kasData.map((student) => [
    student.Name,
    student.status,
    `Rp ${student.nominal.toLocaleString("id-ID")}`,
  ]);

  const total = kasData.reduce((sum, student) => sum + student.nominal, 0);

  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  // Judul
  doc.setFontSize(14);
  doc.text("Laporan Kas Kelas", 105, 10, { align: "center" });

  // Tanggal
  const date = new Date().toLocaleDateString("id-ID", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
  doc.setFontSize(10);
  doc.text(`Tanggal: ${date}`, 14, 20);

  // Tabel
  doc.autoTable({
    startY: 30,
    head: [["Nama", "Status Pembayaran", "Nominal (Rp)"]],
    body: data,
    theme: "grid",
    styles: { halign: "center" },
  });

  // Total Pemasukan
  const finalY = doc.lastAutoTable.finalY;
  doc.setFontSize(12);
  doc.text(
    `Total Pemasukan: Rp ${total.toLocaleString("id-ID")}`,
    14,
    finalY + 10
  );

  doc.save("laporan_kas_kelas.pdf");
}

// Simpan data ke localStorage
function saveData() {
  localStorage.setItem("kasData", JSON.stringify(kasData));
}

// Inisialisasi tabel saat dokumen siap
document.addEventListener("DOMContentLoaded", () => {
  initializeData();
  initializeTable();
  updateTotalKas();
});
