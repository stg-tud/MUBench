function addTag(tagName){
        let misuseTagsDiv = document.getElementById('misuse-tags');
        if (isExistingTag(misuseTagsDiv, tagName)) {
            misuseTagsDiv.innerHTML += getTagTemplate(tagName);
        }
        event.target.value = "";
}

function isExistingTag(misuseTagsDiv, tagName){
    return misuseTagsDiv.querySelectorAll("span#" + tagName).length == 0;
}

function removeTag(tagElement){
    let misuseTagsDiv = document.getElementById('misuse-tags');
    misuseTagsDiv.removeChild(tagElement);
}

function getTagTemplate(tagName){
    let template = `
        <div class="misuse-tag" style="color:white">
            <span id="${tagName}">${tagName}</span>
            <button class="remove-tag-button" onclick="removeTag(this.parentElement)"><i class="fa fa-trash"></i></button>
        </div>`;
    return template;
}

function postJson(url, msg, callback){
    let request = new XMLHttpRequest();
    request.open('POST', url, true);
    request.setRequestHeader('Content-Type', 'application/json');
    request.addEventListener('load', (r) => {
        if(r.currentTarget.status == 200) {
            callback(r);
        }else{
            console.log(r);
        }
    });
    request.send(JSON.stringify(msg));
}