function addTag(tagName){
        let misuseTagsDiv = document.getElementById('misuse-tags-comment');
        if (isExistingTag(misuseTagsDiv, tagName)) {
            misuseTagsDiv.innerHTML += getTagTemplate(tagName);
        }
        event.target.value = "";
}

function isExistingTag(misuseTagsDiv, tagName){
    return misuseTagsDiv.querySelectorAll("span#" + tagName).length == 0;
}

function removeTag(tagElement){
    let misuseTagsDivComment = document.getElementById('misuse-tags-comment');
    misuseTagsDivComment.removeChild(tagElement);
    return false;
}

function getTagTemplate(tagName){
    let template = `
        <div class="misuse-tag" style="color:white">
            <span id="${tagName}">${tagName}</span>
            <button class="remove-tag-button" onclick="removeTag(this.parentElement)"><i class="fa fa-trash"></i></button>
        </div>`;
    return template;
}
