var tags = document.getElementsByClassName('misuse-tag');
for(var i = 0; i < tags.length; i++){
    tags[i].style.color = getContrastYIQ(tags[i].style.backgroundColor);
}

// https://stackoverflow.com/questions/11867545/change-text-color-based-on-brightness-of-the-covered-background-area
function getContrastYIQ(rgb){
    var color = rgb.substring(4, rgb.length-1)
        .replace(/ /g, '')
        .split(',');
    var yiq = ((color[0]*299)+(color[1]*587)+(color[2]*114))/1000;
    return (yiq >= 128) ? 'black' : 'white';
}