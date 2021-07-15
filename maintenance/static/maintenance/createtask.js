document.addEventListener('DOMContentLoaded', function() { 
    //show-hide div as user make selections on buildings and teams
    //show-hide next/back buttons as user goes forward
    //do controls before submit
    nextBtn = document.querySelector('#nextBtn');
    backBtn = document.querySelector('#backBtn');
    buildingsTbl = document.querySelector("#buildingsTbl");
    teamsTbl = document.querySelector("#teamsTbl");
    descArea = document.querySelector('#descriptionArea');
    submitBtn = document.querySelector('#submitBtn');
    hiddenBuilding = document.querySelector('#buildingInput');
    hiddenTeam = document.querySelector('#teamInput');
    taskDesc = document.getElementsByName('description');
    choosenDiv = document.querySelector('#choosen');
    choosenBld = document.querySelector('#choosenBuilding');
    choosenTeam = document.querySelector('#choosenTeam');
    building = "";
    team = "";

    document.querySelectorAll(".cbBuilding").forEach(cb => {
        cb.addEventListener('change', function() {
            div = this.parentNode;
            td = div.parentNode;
            tr= td.parentNode;
            if (this.checked) {
                this.classList.remove("cbBuilding");
                tr.classList.add('table-success');
                document.querySelectorAll(".cbBuilding").forEach(ucb => {
                    ucb.setAttribute("disabled", true);
                });
                //show next button
                nextBtn.classList.add("nextTeam");
                nextBtn.style.display = "block";
                nextBtn.setAttribute("disabled", true);
                hiddenBuilding.value = this.dataset.building;
                building = tr.children[1].innerHTML + " " + tr.children[2].innerHTML + " (" + tr.children[3].innerHTML + ")";
                choosenBld.innerHTML = building;
                choosenDiv.style.display = "block";
                document.querySelector('.selectedTeam').checked = false;
                div = document.querySelector('.selectedTeam').parentNode
                cell = div.parentNode;
                row = cell.parentNode;
                row.classList.remove('table-success');
                document.querySelector('.selectedTeam').classList.add('cbTeam');
                document.querySelector('.selectedTeam').classList.remove('selectedTeam');
                document.querySelectorAll(".cbTeam").forEach(ucb => {
                    ucb.removeAttribute("disabled", false);
                });

            } else {
                document.querySelectorAll(".cbBuilding").forEach(ucb => {
                    ucb.removeAttribute("disabled", false);
                });
                this.classList.add("cbBuilding");
                tr.classList.remove('table-success');
                //hide next button
                nextBtn.style.display = "none";
                nextBtn.classList.remove("nextTeam");
                hiddenBuilding.value = "";
                choosenBld.innerHTML = "";
                choosenTeam.innerHTML = "";
                choosenDiv.style.display = 'none';
            }
        })
    })

    document.querySelector("#nextBtn").addEventListener('click', function () {
        if (this.classList.contains("nextTeam")) {
            buildingsTbl.style.display = 'none';
            teamsTbl.style.display = 'block';
            backBtn.classList.add("backBuild");
            backBtn.style.display = "block";
            nextBtn.classList.remove('nextTeam');
            nextBtn.classList.add('nextDesc');
            if (document.querySelectorAll('.selectedTeam').length > 0) {
                nextBtn.style.display = 'block';
            } else {
                nextBtn.style.display = 'none';
            }
            
        } else if (this.classList.contains('nextDesc')) {
            teamsTbl.style.display = 'none';
            descArea.style.display = 'block';
            backBtn.classList.remove("backBuild");
            backBtn.classList.add("backTeam");
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'block';

        }

    });

    document.querySelector("#backBtn").addEventListener('click', function () {
        if (this.classList.contains("backBuild")) {
            buildingsTbl.style.display = 'block';
            backBtn.style.display = "none";
            backBtn.classList.remove("backBuild");
            nextBtn.classList.remove('nextDesc');
            nextBtn.classList.add('nextTeam');
            teamsTbl.style.display = 'none';
            nextBtn.style.display = 'block';
        } else if (this.classList.contains('backTeam')) {
            teamsTbl.style.display = 'block';
            descArea.style.display = "none";
            nextBtn.style.display = 'block';
            submitBtn.style.display = 'none';
            backBtn.classList.remove("backTeam");
            backBtn.classList.add("backBuild");
        }

    });

    document.querySelectorAll('.cbTeam').forEach(cbt => {
        cbt.addEventListener('change', function () {
            div = this.parentNode;
            td = div.parentNode;
            tr= td.parentNode;

            if(this.checked) {
                this.classList.remove("cbTeam");
                this.classList.add('selectedTeam');
                tr.classList.add('table-success');
                document.querySelectorAll(".cbTeam").forEach(ucb => {
                    ucb.setAttribute("disabled", true);
                });
                //show next button
                nextBtn.classList.add("nextDesc");
                nextBtn.classList.remove("nextTeam")
                hiddenTeam.value = this.dataset.team;
                team = tr.children[1].innerHTML + " (" + tr.children[2].innerHTML + ")";
                choosenTeam.innerHTML = team;
                nextBtn.style.display = 'block';
            } else {
                document.querySelectorAll(".cbTeam").forEach(ucb => {
                    ucb.removeAttribute("disabled", false);
                });
                this.classList.add("cbBuilding");
                tr.classList.remove('table-success');
                hiddenTeam.value = "";
                choosenTeam.innerHTML = "";
                nextBtn.style.display = 'none';
            }
        })
    });

    document.querySelector('#taskForm').addEventListener('submit', function(e) {
        
        if (document.querySelector('#taskDate').value == "") {
            e.preventDefault();
            alert("Choose a valid date for your task.")
        }
     })

})