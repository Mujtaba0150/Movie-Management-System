let selectedMovieId = null;
let selectedRating = null;
let currentMovieId = null;

function openRatingOverlay(movieId) {
    currentMovieId = movieId;
    selectedRating = null;

    // Remove previous selection
    document.querySelectorAll('#ratingButtons button').forEach(btn => {
        btn.classList.remove('selected');
    });

    document.getElementById('ratingOverlay').style.display = 'flex';
}

function closeRatingOverlay() {
    document.getElementById('ratingOverlay').style.display = 'none';
}

function selectRating(rating) {
    selectedRating = rating;
    document.querySelectorAll('#ratingButtons button').forEach(btn => {
        btn.classList.remove('selected');
    });
    document.querySelector(`#ratingButtons button:nth-child(${rating})`).classList.add('selected');
}

function submitRating() {
    if (!selectedRating || !currentMovieId) {
        alert("Please select a rating before submitting.");
        return;
    }
    console.log("Selected rating: " + selectedRating);
    updateRating(currentMovieId, selectedRating);
    closeRatingOverlay();
}

function updateRating(movieId, rating) {
    fetch('/rateMovie', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ movieId: movieId, rating: rating })
    })
        .then(res => {
            if (res.ok) {
                alert("Rating submitted successfully.");
                location.reload();
            } else {
                alert("Failed to submit rating.");
            }
        });
}

function openWatchlistOverlay(movieId) {
    selectedMovieId = parseInt(movieId);

    fetch(`/get_user_watchlists`)
        .then(response => response.json())
        .then(data => {
            const listContainer = document.getElementById('watchlistList');
            listContainer.innerHTML = '';

            data.watchlists.forEach(watchlist => {
                const li = document.createElement('li');
                li.textContent = watchlist.name;
                li.onclick = () => addMovieToWatchlist(watchlist.watchlistId);
                listContainer.appendChild(li);
            });

            document.getElementById('watchlistOverlay').style.display = 'flex';
        });
}

function closeWatchlistOverlay() {
    document.getElementById('watchlistOverlay').style.display = 'none';
    selectedMovieId = null;
    document.getElementById('newWatchlistName').value = '';
}

function addMovieToWatchlist(watchlistId) {
    fetch('/add_to_watchlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ movieId: selectedMovieId, watchlistId: watchlistId })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                closeWatchlistOverlay();
            } else {
                alert('Failed to add movie');
            }
        });
}

function createNewWatchlist() {
    const name = document.getElementById('newWatchlistName').value.trim();
    if (name === '') return;

    fetch('/create_watchlist_and_add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: name, movieId: selectedMovieId })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                closeWatchlistOverlay();
            } else if (data.error) {
                alert(data.error);
            }
            else {
                alert('Failed to create watchlist');
            }
        });
}

function toggleDescription(button) {
    const container = button.parentElement;
    const shortDesc = container.querySelector('.short-desc');
    const fullDesc = container.querySelector('.full-desc');

    if (fullDesc.style.display === 'none') {
        shortDesc.style.display = 'none';
        fullDesc.style.display = 'block';
        container.style.maxHeight = 'none';
        button.textContent = 'less';
    } else {
        shortDesc.style.display = 'block';
        fullDesc.style.display = 'none';
        container.style.maxHeight = '3.6em';
        button.textContent = 'more';
    }
}

function checkOverflowAndShowButtons() {
    document.querySelectorAll('.desc-container').forEach(container => {
        const shortDesc = container.querySelector('.short-desc');
        const button = container.querySelector('.toggle-desc-btn');

        if (shortDesc.scrollWidth > shortDesc.clientWidth) {
            button.style.display = 'inline';
        }
    });
}

window.addEventListener('DOMContentLoaded', checkOverflowAndShowButtons);
function positionOverlay(wrapper) {
    const overlay = wrapper.querySelector('.movie-overlay');
    const card = wrapper.querySelector('.movie-card');
    const cardRect = card.getBoundingClientRect();
    const overlayWidth = 300; // same as CSS
    const spacing = 12;

    // Determine left or right placement
    let left = cardRect.right + spacing;
    if (left + overlayWidth > window.innerWidth) {
        left = cardRect.left - overlayWidth - spacing;
    }

    // Clamp vertical position
    let top = cardRect.top;
    if (top + 200 > window.innerHeight) {
        top = window.innerHeight - 220;
    }
    if (top < 0) top = 10;

    overlay.style.left = `${left}px`;
    overlay.style.top = `${top}px`;
    overlay.style.display = 'block';
}

function hideOverlay(wrapper) {
    const overlay = wrapper.querySelector('.movie-overlay');
    overlay.style.display = 'none';
}
