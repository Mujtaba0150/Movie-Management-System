function toggleProfileDropdown() {
    const dropdown = document.getElementById("profileDropdown");
    dropdown.style.display = (dropdown.style.display === "block") ? "none" : "block";
}

document.addEventListener('click', function (event) {
    const profile = document.querySelector('.profile-menu');
    if (!profile.contains(event.target)) {
        document.getElementById("profileDropdown").style.display = "none";
    }
});

function logoutUser(button) {
    const logoutUrl = button.dataset.logoutUrl;

    fetch(logoutUrl, {
        method: "POST",
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                window.location.reload();
            }
        });
}

function checkCreateGenre(select) {
    if (select.value === '__create_new__') {
        select.value = ""; // reset selection
        document.getElementById('createGenreOverlay').style.display = 'flex';
    }
}

function closeGenreOverlay() {
    document.getElementById('createGenreOverlay').style.display = 'none';
}

function submitNewGenre() {
    const name = document.getElementById('newGenreName').value.trim();
    if (name === "") {
        alert("Genre name cannot be empty.");
        return;
    }

    // Optionally, send to backend to save permanently
    // For now, just add it to the dropdown
    const genreSelect = document.getElementById('genre');
    const newOption = document.createElement("option");
    newOption.value = name;
    newOption.textContent = name;
    genreSelect.appendChild(newOption);
    genreSelect.value = name;

    closeGenreOverlay();
}

function filterDropdown(inputElement, listId) {
    const filter = inputElement.value.toLowerCase();
    const dropdown = document.getElementById(listId);
    const items = dropdown.querySelectorAll('.dropdown-item');

    let hasMatch = false;
    items.forEach(item => {
        const match = item.textContent.toLowerCase().includes(filter);
        item.style.display = match ? 'block' : 'none';
        if (match) hasMatch = true;
    });

    dropdown.style.display = filter ? 'block' : 'none';

    // If no match, optionally show "add new" item
    if (!hasMatch) {
        dropdown.innerHTML = `<div class="dropdown-item" onclick="selectDropdownItem(this, '${inputElement.id}')">${inputElement.value} (new)</div>`;
        dropdown.style.display = 'block';
    }
}

function selectDropdownItem(item, inputId) {
    document.getElementById(inputId).value = item.textContent.replace(" (new)", "");
    document.getElementById(inputId).blur();
    item.parentElement.style.display = 'none';
}

// Optional: hide dropdown on outside click
document.addEventListener('click', function (event) {
    const dropdowns = document.querySelectorAll('.dropdown-list');
    dropdowns.forEach(dropdown => {
        if (!dropdown.parentElement.contains(event.target)) {
            dropdown.style.display = 'none';
        }
    });
});
