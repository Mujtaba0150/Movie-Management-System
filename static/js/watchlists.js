document.addEventListener('DOMContentLoaded', function () {
    const watchlistItems = document.querySelectorAll('.watchlist-item');
    const movieRows = document.querySelectorAll('tbody tr[data-watchlist-id]');
    const watchlistTitle = document.getElementById('watchlistTitle');
    const ellipses = document.querySelectorAll('.ellipsis');
    const removeButtons = document.querySelectorAll('.remove-movie-btn');

    watchlistItems.forEach(item => {
        item.addEventListener('click', function (e) {
            if (e.target.classList.contains('ellipsis')) return; // skip if ellipsis clicked
            watchlistItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');

            const selectedId = this.getAttribute('data-watchlist-id');
            const nameSpan = this.querySelector('.watchlist-name');
            const watchlistName = nameSpan ? nameSpan.textContent.trim() : '';

            watchlistTitle.textContent = selectedId === 'all' ? 'All Watchlists' : watchlistName;

            movieRows.forEach(row => {
                if (selectedId === 'all') {
                    row.style.display = '';
                } else {
                    const rowWatchlistName = row.getAttribute('data-watchlist-name');
                    row.style.display = (rowWatchlistName === watchlistName) ? '' : 'none';

                }
            });
        });
    });


    ellipses.forEach(icon => {
        icon.addEventListener('click', function (e) {
            e.stopPropagation();
            const id = this.getAttribute('data-watchlist-id');
            document.querySelectorAll('.watchlist-menu').forEach(menu => {
                menu.style.display = 'none';
            });
            const menu = document.querySelector(`.watchlist-menu[data-menu-id="${id}"]`);
            menu.style.display = 'block';
            menu.style.left = `${e.pageX - 100}px`;
            menu.style.top = `${e.pageY}px`;
        });
    });

    document.addEventListener('click', () => {
        document.querySelectorAll('.watchlist-menu').forEach(menu => menu.style.display = 'none');
    });

    document.querySelectorAll('.rename-btn').forEach(button => {
        button.addEventListener('click', function () {
            const menu = this.closest('.watchlist-menu');
            const watchlistId = menu.getAttribute('data-menu-id');
            const nameSpan = document.querySelector(`.watchlist-item[data-watchlist-id="${watchlistId}"] .watchlist-name`);
            const oldName = nameSpan.textContent;

            const newName = prompt("Enter new watchlist name:", oldName);
            if (newName && newName.trim() !== "") {
                fetch(`/renameWatchlist/${watchlistId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ newName: newName.trim() })
                }).then(res => {
                    if (res.ok) {
                        nameSpan.textContent = newName.trim();
                    } else {
                        alert("Failed to rename watchlist.");
                    }
                });
            }
        });
    });

    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function () {
            const menu = this.closest('.watchlist-menu');
            const watchlistId = menu.getAttribute('data-menu-id');

            // Capture currently active watchlist before deletion
            const currentActiveId = document.querySelector('.watchlist-item.active')?.getAttribute('data-watchlist-id');

            if (confirm("Are you sure you want to delete this watchlist?")) {
                fetch(`/deleteWatchlist/${watchlistId}`, {
                    method: 'POST'
                }).then(res => {
                    if (res.ok) {
                        // Remove the watchlist item
                        document.querySelector(`.watchlist-item[data-watchlist-id="${watchlistId}"]`)?.remove();

                        // Remove all rows for that watchlist
                        document.querySelectorAll(`tr[data-watchlist-id="${watchlistId}"]`).forEach(row => row.remove());

                        // If it was the active one, activate 'All Watchlists'
                        if (currentActiveId === watchlistId) {
                            document.querySelector('.watchlist-item[data-watchlist-id="all"]').click();
                        }
                    } else {
                        alert("Failed to delete watchlist.");
                    }
                });
            }
        });
    });


    document.querySelectorAll('.remove-movie-btn').forEach(button => {
        button.addEventListener('click', function () {
            const row = this.closest('tr');
            const movieId = row.getAttribute('data-movie-id');
            const watchlistId = row.getAttribute('data-watchlist-id');

            console.log(`Removing movie with ID ${movieId} from watchlist with ID ${watchlistId}`);

            if (confirm("Are you sure you want to remove this movie from the watchlist?")) {
                fetch('/removeMovieFromWatchlist', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ movieId: movieId, watchlistId: watchlistId })
                }).then(res => {
                    if (res.ok) {
                        row.remove();
                    } else {
                        alert("Failed to remove movie from watchlist.");
                    }
                });
            }
        });
    });

});
