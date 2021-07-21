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

    document.querySelectorAll(`#editTeamBtn`).forEach(e=> {
        e.addEventListener('click', function() {

            team_id = e.dataset.tid;
            btnGrpDiv = document.querySelector(`#editBtnGroup-${ team_id }`);
            upperBtns = document.querySelectorAll(`.upperBtns`);
    
            iName = document.querySelector(`#iName-${team_id}`);
            iLeader = document.querySelector(`#iLeader-${team_id}`);
            iDescription = document.querySelector(`#iDescription-${team_id}`);
    
            tName = document.querySelector(`#tName-${team_id}`);
            tLeader = document.querySelector(`#tLeader-${team_id}`);
            tDescription = document.querySelector(`#tDescription-${team_id}`);
    
            iName.value = tName.innerHTML;
            iLeader.value = tLeader.dataset.leaderid;
            iDescription.value = tDescription.innerHTML;

            upperBtns.forEach(up=>{
                up.style.display = 'none';
            })
            
            btnGrpDiv.style.display = 'block';
    
            document.querySelectorAll(`.tEdit-${ team_id }`).forEach(p => {
                p.style.display = 'none';
            })
    
            document.querySelectorAll(`.iEdit-${ team_id }`).forEach(i => {
                i.style.display = 'block';
            })
    
            document.querySelector(`#cancelEdit-${team_id}`).addEventListener('click', function() {
                btnGrpDiv.style.display = 'none';
    
                document.querySelectorAll(`.tEdit-${ team_id }`).forEach(p => {
                    p.style.display = 'block';
                })
    
                upperBtns.forEach(up=>{
                    up.style.display = 'block';
                })
    
                document.querySelectorAll(`.iEdit-${ team_id }`).forEach(i => {
                    i.style.display = 'none';
                })
            });
    
            document.querySelector(`#doEdit-${team_id}`).addEventListener('click', async function() {

                await fetch(`/editTeam/${team_id}`, {
                    method: 'PUT',
                    headers: {ignoreCache: false, 'X-CSRFToken': csrftoken},
                    body: JSON.stringify({
                        name: iName.value,
                        leader: iLeader.value,
                        description: iDescription.value,
                    })
                  })
                  .then(response => response.json())
                  .then(result => { 
                    if(result.result == true) { 
                        tName.innerHTML = iName.value;
                        tLeader.innerHTML = iLeader.options[iLeader.selectedIndex].text;
                        tDescription.innerHTML = iDescription.value;
                
                        btnGrpDiv.style.display = 'none';
    
                        document.querySelectorAll(`.tEdit-${ team_id }`).forEach(p => {
                            p.style.display = 'block';
                        })
            
                        upperBtns.forEach(up=>{
                            up.style.display = 'block';
                        })
            
                        document.querySelectorAll(`.iEdit-${ team_id }`).forEach(i => {
                            i.style.display = 'none';
                        })

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
            });



        }); 

    });

})