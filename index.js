document.addEventListener('DOMContentLoaded', function() {
    var modal = document.getElementById("recomai-modal");
    var btn = document.getElementById("recomai-button");
    var span = document.getElementsByClassName("recomai-close")[0];
    var closeButton = document.getElementById("recomai-close");
    var likeButton = document.getElementById("recomai-like");
    var dislikeButton = document.getElementById("recomai-dislike");
    var contentDiv = document.getElementById("recomai-content");

    btn.onclick = function() {
        modal.style.display = "block";
        fetchRecomendaciones();
    }

    span.onclick = function() {
        modal.style.display = "none";
    }

    closeButton.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    likeButton.onclick = function() {
        alert("Gracias por tu feedback!");
        modal.style.display = "none";
    }

    dislikeButton.onclick = function() {
        alert("Gracias por tu feedback!");
        modal.style.display = "none";
    }

    function fetchRecomendaciones() {
        contentDiv.innerHTML = "<p>Cargando recomendaciones...</p>";
        
        fetch('http://127.0.0.1:8000/recomendaciones?industria=Minería&subtema=Seguridad en la mina', {
            method: 'GET',
            headers: {
                'X-API-KEY': 'api_key'
            }
        })
        .then(response => response.json())
        .then(data => {
            contentDiv.innerHTML = "<p>" + data.recomendaciones + "</p>";
        })
        .catch(error => {
            contentDiv.innerHTML = "<p>Ocurrió un error al obtener las recomendaciones.</p>";
            console.error('Error:', error);
        });
    }
});
