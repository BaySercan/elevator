document.addEventListener('DOMContentLoaded', function() { 
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    building_id = document.querySelector('#editBuilding').dataset.bid;

    alertDiv = document.querySelector('.alert');

    bName = document.querySelector('#bName');
    bAddress = document.querySelector('#bAddress');
    bManager = document.querySelector('#bManager');
    bPhone = document.querySelector('#bPhone');
    bEmail = document.querySelector('#bEmail');
    bFloors = document.querySelector('#bFloors');
    bElevator = document.querySelector('#bElevator');
    bStatus = document.querySelector('#bStatus');

    iName = document.querySelector('#iName');
    iAddress = document.querySelector('#iAddress');
    iManager = document.querySelector('#iManager');
    iPhone = document.querySelector('#iPhone');
    iEmail = document.querySelector('#iEmail');
    iFloors = document.querySelector('#iFloors');
    iElevator = document.querySelector('#iElevator');
    iStatus = document.querySelector('#iStatus');

    btnGrpDiv = document.querySelector('#editBtnGroup');

    document.querySelector('#editBuilding').addEventListener('click', function() {
        
        btnGrpDiv.style.display = 'block';
        alertDiv.style.display = "none";
        
        document.querySelectorAll('.editB').forEach(inp => {
            iName.value = bName.innerHTML;
            iAddress.value = bAddress.innerHTML;
            iManager.value = bManager.innerHTML;
            iPhone.value = bPhone.innerHTML;
            iEmail.value = bEmail.innerHTML;
            iFloors.value = bFloors.innerHTML;
            iElevator.value = bElevator.innerHTML;
            iStatus.value = document.querySelector('#hiddenBstatus').value;

            inp.style.display = "block";
        })

        document.querySelectorAll('.bInfo').forEach(p => {
            p.style.display = 'none';
        })

        
    });

    document.querySelector('#cancelEdit').addEventListener('click', function() {
        alertDiv.style.display = "none";

        document.querySelectorAll('.editB').forEach(inp => {    
            inp.style.display = "none";
        })

        document.querySelectorAll('.bInfo').forEach(p => {
            p.style.display = 'block';
        })

        btnGrpDiv.style.display = 'none';
    });

    document.querySelector('#doEdit').addEventListener('click', async function() {
        alertDiv.style.display = "none";

        await fetch(`/editBuilding/${building_id}`, {
            method: 'PUT',
            headers: {ignoreCache: false, 'X-CSRFToken': csrftoken},
            body: JSON.stringify({
                name: iName.value,
                address: iAddress.value,
                manager: iManager.value,
                phone: iPhone.value,
                email: iEmail.value,
                floors: iFloors.value,
                elevator_type: iElevator.value,
                status: iStatus.value,
            })
          })
          .then(response => response.json())
          .then(result => { 
            if(result.result == true) { 
                bName.innerHTML = iName.value;
                bAddress.innerHTML = iAddress.value;
                bManager.innerHTML = iManager.value;
                bPhone.innerHTML = iPhone.value;
                bEmail.innerHTML = iEmail.value;
                bFloors.innerHTML = iFloors.value;
                bElevator.innerHTML = iElevator.value;
                bStatus.innerHTML = iStatus.options[iStatus.selectedIndex].text;

                document.querySelectorAll('.editB').forEach(inp => {    
                    inp.style.display = "none";
                })
        
                document.querySelectorAll('.bInfo').forEach(p => {
                    p.style.display = 'block';
                })
        
                btnGrpDiv.style.display = 'none';

                alertDiv.innerHTML = result.message;
                alertDiv.classList.remove('alert-warning');
                alertDiv.classList.add('alert-success');
                alertDiv.style.display = "block";

            } else {
                alertDiv.innerHTML = result.message;
                alertDiv.classList.add('alert-warning');
                alertDiv.classList.remove('alert-success');
                alertDiv.style.display = "block";
            }


          })
    });

})