window.onclick = function (event) {
    var dropdown = document.getElementById("save-dropdown");
    if(event.target.id == "dropdown-button" || event.target.parentElement.id == "dropdown-button"){
        if(dropdown.style.display == "none" || dropdown.style.display == ""){
            dropdown.style.display = "block";
        }else{
            dropdown.style.display = "none";
        }
    }else{
        dropdown.style.display = "none";
    }
};


function show(b){
    var elem = document.getElementById("snippet_form");
    if(elem.style.display === "none"){
        elem.style.display = "block";
    }
    b.type = "hidden";
}

function comment(){
    var comment = document.getElementById("comment-area");
    if(comment.style.display == "none" || comment.style.display == ""){
        comment.style.display = "block";
    }else{
        comment.style.display = "none";
    }
}

function review(e){
    e.parentElement.style.display = "none";
    document.getElementById("review_area").style.visibility = "visible";
    document.getElementById("overlay").style.display = "none";
    document.getElementById("overlay-button").style.display = "none";
}

var simplemde = new SimpleMDE({
    element: document.getElementById("review_comment"),
    spellChecker: false,
    status: false
});

function saveReview(v){
    var form = document.getElementById("review_form");
    var input = document.createElement("input");
    input.type = "hidden";
    input.name = "origin";
    switch(v){
        case "save":
            input.name = "origin_param";
        case "return":
            input.value = origin;
            break;
        case "review":
            input.value = next_review;
            break;
    }
    form.appendChild(input);
    form.submit();
}

document.addEventListener("keypress", function(event){
    if(event.target.tagName == 'SELECT' || event.target.tagName == 'BODY'){
        if(next_reviewable == 1){
            saveReview('review');
        }else{
            saveReview('return');
        }
    }
});