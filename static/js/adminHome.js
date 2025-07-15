function approveRequest(button) {
    const requestId = button.getAttribute('data-request-id');
    document.getElementById('approveRequestId').value = requestId;
    document.getElementById('actorOverlay').style.display = 'flex';
}

function closeActorOverlay() {
    document.getElementById('actorOverlay').style.display = 'none';
}

// function submitActorSelection() {
//     const selectedActors = Array.from(document.getElementById('actorSelect').selectedOptions)
//         .map(opt => opt.value);
//     const newActors = document.getElementById('newActors').value
//         .split(',')
//         .map(actor => actor.trim())
//         .filter(actor => actor.length > 0);
//     const requestId = document.getElementById('approveRequestId').value;

//     // Send to backend (example using fetch)
//     fetch('/approveRequest', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({
//             requestId: requestId,
//             selectedActorIds: selectedActors,
//             newActors: newActors
//         })
//     }).then(res => {
//         if (res.ok) {
//             alert('Request approved with actors');
//             closeActorOverlay();
//             location.reload();
//         } else {
//             alert('Failed to approve request');
//         }
//     });
// }

function submitActorSelection() {
    const formData = new FormData();

    const checkedBoxes = document.querySelectorAll('#existingActorsList input[name="existingActor"]:checked');
    const selectedActors = Array.from(checkedBoxes).map(cb => cb.value);
    const newActors = document.getElementById('newActors').value
        .split(',')
        .map(actor => actor.trim())
        .filter(actor => actor.length > 0);

    const requestId = document.getElementById('approveRequestId').value;
    const posterInput = document.getElementById('moviePoster');
    const posterFile = posterInput.files[0];

    if (!posterFile) {
        alert("Please upload a movie poster.");
        return;
    }

    if (!posterFile.type.startsWith('image/')) {
        alert("Only image files are allowed.");
        return;
    }

    formData.append('poster', posterFile);
    formData.append('requestId', requestId);
    formData.append('selectedActorIds', JSON.stringify(selectedActors));
    formData.append('newActors', JSON.stringify(newActors));

    fetch('/approveRequest', {
        method: 'POST',
        body: formData
    }).then(res => {
        if (res.ok) {
            alert('Request approved with actors and poster');
            closeActorOverlay();
            location.reload();
        } else {
            alert('Failed to approve request');
        }
    });
}


function updateRequest(button) {
    const requestId = button.dataset.requestId;

    fetch('/editRequest', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ requestId: requestId })
    })
        .then(res => res.text())
        .then(html => {
            // Replace current page content with the edit form HTML
            document.open();
            document.write(html);
            document.close();
        });
}


function rejectRequest(button) {
    const requestId = button.dataset.requestId;

    if (confirm(`Reject request ID ${requestId}?`)) {
        fetch('/rejectRequest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ requestId: requestId })
        }).then(res => {
            if (res.ok) {
                location.reload();
            } else {
                alert("Failed to reject request.");
            }
        });
    }
}


function toggleDescription(button) {
    const container = button.parentElement;
    const shortDesc = container.querySelector('.short-desc');
    const fullDesc = container.querySelector('.full-desc');

    if (fullDesc.style.display === 'none') {
        shortDesc.style.display = 'none';
        fullDesc.style.display = 'block';
        container.style.maxHeight = 'none';
        container.style.maxWidth = '20em';
        button.textContent = 'less';
    } else {
        shortDesc.style.display = 'block';
        fullDesc.style.display = 'none';
        container.style.maxHeight = '3.6em';
        container.style.maxWidth = '10em';
        button.textContent = 'more';
    }
}

window.addEventListener('DOMContentLoaded', checkOverflowAndShowButtons);
