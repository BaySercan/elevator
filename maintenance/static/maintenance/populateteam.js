document.addEventListener('DOMContentLoaded', function() { 
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    msg = document.querySelector(".json");
    msg.style.display = 'none';

    document.querySelectorAll(".conf").forEach(button => {
        button.addEventListener('click', async function () {
            if (!confirm('Are you sure you want to confirm/unconfirm this user?')) {
                return false;
            }
           
            msg.style.display = 'none';
            user_id = parseInt(this.dataset.confirm);

            btn = document.querySelector(`[data-confirm="${user_id}"]`);
            cell = btn.parentNode;
            row = cell.parentNode;

            await fetch(`/confirmUser/${user_id}`, {
                method: 'PUT',
                headers: {ignoreCache: false, 'X-CSRFToken': csrftoken},
              })
              .then(response => response.json())
              .then(result => { 
                if(result.result == true) {
                    if (btn.classList.contains('btn-warning')) {
                        btn.classList.remove('btn-warning');
                        btn.classList.add('btn-success');
                        btn.innerHTML = "Confirm";
                        row.setAttribute('class', 'table-danger')
                        cell.nextElementSibling.innerHTML = "";
                        cell.nextElementSibling.innerHTML = "Not Confirmed";
                    } else if (btn.classList.contains('btn-success')) {
                        btn.classList.remove('btn-success');
                        btn.classList.add('btn-warning');
                        btn.innerHTML = "Unconfirm";
                        row.removeAttribute('class', 'table-danger');
                        cell.nextElementSibling.innerHTML = "";

                        aBTn = document.createElement('a');
                        aBTn.setAttribute("class", "btn btn-sm btn-info addTeam");
                        aBTn.setAttribute("data-addteam", `${user_id}`);
                        aBTn.setAttribute("href", "javascript:void(0)");
                        aBTn.innerHTML = "Add to team"
                        cell.nextElementSibling.append(aBTn);
                        aBTn.addEventListener('click', function(e) {
                            addToTeam(e);
                        })

                    }

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

    
    document.querySelectorAll('.addTeam').forEach(addBtn => {
        addBtn.addEventListener('click', function(e) {
            addToTeam(e);
        });
    });

})

async function addToTeam(e) {
    msg.style.display = 'none';
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    cell = e.target.parentNode;
    row = cell.parentNode;

    await fetch(`/addUserToTeam`, {
        method: 'PUT',
        body: JSON.stringify({
            team_id: parseInt(document.querySelector('#teamId').value),
            user_id: parseInt(e.target.dataset.addteam),
        }),
        headers: {ignoreCache: false, 'X-CSRFToken': csrftoken},
        })
        .then(response => response.json())
        .then(result => { 
        if(result.result == true) {
            row.remove();
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

}