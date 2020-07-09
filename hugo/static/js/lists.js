$(document).ready(function(){
    if (!$(".pages").length){
        // we are on lists page
        return;
    }
    slider.events.on("indexChanged", function(event){
        var item = event.slideItems[event.index];
        var id = $(item).attr("id");
        if (id)
            history.pushState(null,null,'#' + id);
    });

    $('.pages img').on('click', function(e){
        var pos = (e.pageX - $(this).offset().left) / $(this).width();
        if (pos < 0.25)
            slider.goTo("prev");
        else
            slider.goTo("next");
    });


    $('.page-image').on('click', function() {
        $page = $(this).parent();
        $page.find('.page-image, .page-text').toggleClass('is-hidden');
    });

})
