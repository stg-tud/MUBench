let checkboxes = document.getElementById('filter-menu').querySelectorAll("input[type='checkbox']");

function isFilterActive(){
    let filter = false;
    for(let i = 0; i < checkboxes.length; ++i){
        filter = filter || checkboxes[i].checked;
    }
    return filter;
}

function filterRow(row){
    for(let i = 0; i < checkboxes.length; ++i){
        if(!checkboxes[i].checked){
            continue;
        }
        if(row.querySelectorAll(checkboxes[i].value).length > 0){
            return true;
        }
    }
    return false;
}

function changeStatsDisplay(row, visible, visibleProject){
    let stats = row.querySelectorAll("span[class^='stats']");
    let statsClassName = visible ? "stats" : "stats td-invisible";
    let startIndex = (visibleProject ? 0 : 1);
    for(let i = startIndex; i < stats.length; ++i){
        stats[i].className = statsClassName;
        if(visibleProject && visible && !stats[i].parentNode.className.includes("top")){
            stats[i].parentNode.className += " top";
        }else if(!visible){
            stats[i].parentNode.className = stats[i].parentNode.className.replace(" top", "")
        }
    }
}


function filter(){
    let rows = document.getElementById("detector_table").querySelectorAll("tr");
    let lastProject = "";
    let lastVersion = "";
    for(let i = 0; i < rows.length; ++i){
        let row = rows[i];

        // there are tables inside the main table and a header, ignore them
        if(row.parentNode.parentNode.id != "detector_table" || row.children[0].tagName == "TH"){
            continue;
        }

        let project = (row.childNodes[1].childNodes[1].childNodes[0].innerText); // project column
        let version = (row.childNodes[3].childNodes[1].childNodes[0].innerText); // version column
        if(!isFilterActive() || filterRow(row)) {
            row.style.display = "";
            if(lastProject != project || lastVersion != version){
                changeStatsDisplay(row, true, lastProject != project);
            }else{
                changeStatsDisplay(row, false, true);
            }
            lastProject = project;
            lastVersion = version;
        }else{
            row.style.display = "none";
        }
    }
}