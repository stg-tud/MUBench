function addTag(url, misuseId, tagName){
        let misuseTagsDiv = document.getElementById('misuse-tags')
        if (isExistingTag(misuseTagsDiv, tagName)) {
            let data = {
                "tag_name": tagName,
                "misuse_id": misuseId
            };
            postJson(url, data, function(r){
                let tag = JSON.parse(r.srcElement.responseText);
                misuseTagsDiv.innerHTML += getTagTemplate(tagName, tag);
            });
        }
        event.target.value = "";
}

function isExistingTag(misuseTagsDiv, tagName){
    return misuseTagsDiv.querySelectorAll("span#" + tagName).length == 0;
}

function removeTag(url, button){
    postJson(url, {"misuse_id": misuseId}, (r) => {
        let misuseTagsDiv = document.getElementById('misuse-tags');
        misuseTagsDiv.removeChild(button.parentElement);
    });
}

function getTagTemplate(tagName, tag){
    let template = `
        <div class="misuse-tag" style="background-color:${tag.color};color:${tag.fontColor};">
            <span id="${tagName}">${tagName}</span>
            <button onclick="removeTag('${tag.removeUrl}', this)" style="border:none;outline:none;margin:0;padding:0;background-color:${tag.color}"><i class="fa fa-trash"></i></button>
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