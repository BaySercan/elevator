document.addEventListener('DOMContentLoaded', function() { 
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    msg = document.querySelector(".json");
    msg.style.display = 'none';

    document.querySelectorAll(".rm_user").forEach(rmBtn => {
        rmBtn.addEventListener('click', async function () {
            msg.style.display = 'none';
            pTag = rmBtn.parentNode;

            await fetch(`/removefromTeam`, {
                method: 'PUT',
                body: JSON.stringify({
                    team_id: parseInt(this.dataset.team),
                    user_id: parseInt(this.dataset.user_id),
                }),
                headers: {ignoreCache: false, 'X-CSRFToken': csrftoken},
              })
              .then(response => response.json())
              .then(result => { 
                    if(result.result == true) {
                        pTag.remove();
                        msg.innerHTML = result.message;
                        msg.classList.remove('alert-warning');
                        msg.classList.add('alert-success');
                        msg.style.display = 'block';

                    } else {
                        msg.innerHTML = result.message;
                        msg.classList.remove('alert-success');
                        msg.classList.add('alert-warning');
                        msg.style.display = 'block';
                    }
              })

        })
    });
})