// Toggle Dropup Menu
const dropupButton = document.querySelector(".dropup-button");
const dropupMenu = document.querySelector(".dropup-content");
const dropup = document.querySelector(".dropup");

dropupButton.addEventListener("click", () => {
  dropup.classList.toggle("open");
});

// Tambahkan Mata Kuliah ke Card List
const cardList = document.querySelector(".card-list");
const dropupItems = document.querySelectorAll(".dropup-item");

dropupItems.forEach((item) => {
  item.addEventListener("click", () => {
    // Ambil data dari atribut tombol
    const title = item.dataset.title;
    const time = item.dataset.time;
    const description = item.dataset.description;
    const image = item.dataset.image;

    // Buat kartu baru
    const newCard = document.createElement("li");
    newCard.classList.add("card-item");

    newCard.innerHTML = `
        <a href="#" class="card-link">
          <img src="${image}" alt="${title}" class="card-image" />
          <p class="badge">${time}</p>
          <h2 class="card-title">${title}</h2>
          <p>${description}</p>
          <button class="card-button material-symbols-rounded">arrow_forward</button>
        </a>
      `;

    // Tambahkan kartu baru ke card list
    cardList.appendChild(newCard);

    // Tutup dropup menu setelah memilih
    dropup.classList.remove("open");
  });
});

// Klik di luar menu untuk menutup dropup
document.addEventListener("click", (event) => {
  if (!dropup.contains(event.target)) {
    dropup.classList.remove("open");
  }
});
