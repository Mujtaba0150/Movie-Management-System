function toggleDropdown(id) {
    const dropdown = document.getElementById(id);

    // Close any other open dropdowns
    const allDropdowns = document.querySelectorAll('.dropdown');
    allDropdowns.forEach(d => {
        if (d.id !== id) {
            d.style.display = 'none';
        }
    });

    // Toggle the clicked dropdown
    dropdown.style.display = (dropdown.style.display === 'block') ? 'none' : 'block';
}

// Close dropdown if clicked outside
document.addEventListener('click', function (event) {
    const filters = document.querySelector('.filters');
    if (!filters.contains(event.target)) {
        const allDropdowns = document.querySelectorAll('.dropdown');
        allDropdowns.forEach(d => d.style.display = 'none');
    }
});
