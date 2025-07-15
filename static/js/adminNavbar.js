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