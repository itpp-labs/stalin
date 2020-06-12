$(document).ready(function(){
    $("#search_form input").on("input propertychange paste", function(){
        console.log($("#search_form").serializeArray() );
    })
})
