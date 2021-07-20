document.addEventListener('DOMContentLoaded', function() { 
    document.querySelectorAll(".conf").forEach(button => {
        button.addEventListener('click', async function () {
            if (!confirm('Are you sure you want to confirm/unconfirm this user?')) {
                return false;
            }
            msg = document.querySelector(".json");
            msg.style.display = 'none';
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

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
                    } else if (btn.classList.contains('btn-success')) {
                        btn.classList.remove('btn-success');
                        btn.classList.add('btn-warning');
                        btn.innerHTML = "Unconfirm";
                        row.removeAttribute('class', 'table-danger');
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
    })

    document.querySelector('#toggleTblBtn').addEventListener('click', function() {
        if (this.classList.contains('active')) {
            document.querySelector('#activeUsers').style.display = 'none';
            document.querySelector('#deActiveUsers').style.display = 'block';
            this.classList.remove('active');
            this.value = "Show active users";
        } else {
            document.querySelector('#activeUsers').style.display = 'block';
            document.querySelector('#deActiveUsers').style.display = 'none';
            this.classList.add('active');
            this.value = "Show unactive users";
        }
    })
    
})

