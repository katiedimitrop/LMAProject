
function filterResults() {
    var input, filter, ul, li, a, i, txtValue;
    //get user input from search bar
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    //Get the list currently on html
    ul = document.getElementById("myUL");
    //get the particular string from the list
    li = ul.getElementsByTagName("li");
    for (i = 0; i < li.length; i++) {
        //element will be surrounded by <a> tags
        a = li[i].getElementsByTagName("a")[0];
        txtValue = a.textContent || a.innerText;
        //if what use has types does not correspond to substring
        //or entire string make it disappear from the list
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}
