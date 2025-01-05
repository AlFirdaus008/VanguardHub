document.addEventListener("DOMContentLoaded", function () {
  const csvUrl = "/instance/members.csv";
  let groups = [
    [3, 7, 15],
    [7, 17, 4],
    [12, 13, 9],
    [11, 16, 18],
    [18, 14, 5],
    [6, 10, 2],
  ];

  fetch(csvUrl)
    .then((response) => response.text())
    .then((data) => {
      const csvData = parseCSV(data);
      populateTable(csvData, groups);
    })
    .catch((error) => console.error("Error loading CSV file:", error));

  document
    .getElementById("makeGroupBtn")
    .addEventListener("click", function () {
      document.getElementById("createGroupSection").style.display = "block";
    });

  document.getElementById("addGroupBtn").addEventListener("click", function () {
    const groupName = document.getElementById("newGroupName").value;
    if (groupName) {
      const newGroup = groups.length + 1;
      groups.push([]);
      alert(`New group '${groupName}' added successfully!`);
    }
    document.getElementById("createGroupSection").style.display = "none";
    document.getElementById("newGroupName").value = "";
  });

  document
    .getElementById("closeGroupBtn")
    .addEventListener("click", function () {
      document.getElementById("createGroupSection").style.display = "none";
    });
});

function parseCSV(data) {
  const rows = data.split("\n");
  return rows.map((row) => row.split(";"));
}

function populateTable(data, groups) {
  const tableBody = document.querySelector("#membersTable tbody");
  tableBody.innerHTML = "";

  groups.forEach((group, groupIndex) => {
    const groupHeader = document.createElement("tr");
    groupHeader.innerHTML = `
            <td colspan="5">
                <div class="group-header">Group ${groupIndex + 1}</div>
            </td>`;
    tableBody.appendChild(groupHeader);

    group.forEach((memberIndex) => {
      const row = data[memberIndex - 1];

      if (row && row.length > 1) {
        const tr = document.createElement("tr");

        const noCell = document.createElement("td");
        noCell.textContent = row[0];

        const nameCell = document.createElement("td");
        const gender = row[7].trim().toLowerCase();
        const imageSrc =
          gender === "male" ? "images/boy.jpg" : "images/girl.jpg";
        nameCell.innerHTML = `<img src="${imageSrc}" alt="${gender}"><a class="name-link" href="${row[5]}" target="_blank"><strong>${row[1]}</strong></a>`;

        const birthdayCell = document.createElement("td");
        birthdayCell.textContent = row[2];

        const nimCell = document.createElement("td");
        nimCell.textContent = row[3];

        const InstagramCell = document.createElement("td");
        InstagramCell.innerHTML = `<a class="Instagram username" href="${row[6]}" target="_blank">Follow</a>`;

        tr.appendChild(noCell);
        tr.appendChild(nameCell);
        tr.appendChild(birthdayCell);
        tr.appendChild(nimCell);
        tr.appendChild(InstagramCell);

        tableBody.appendChild(tr);
      }
    });
  });
}
