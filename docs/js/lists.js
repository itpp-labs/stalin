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


    var PAGE_IMAGE_SELECTOR = '.page-image img[data-src]';
    $('.page-image').on('click', function() {
        var $page = $(this).parents('.register');
        $page.find('.page-image, .page-text').toggleClass('is-hidden');
        var $img = $page.find(PAGE_IMAGE_SELECTOR);
        load_image($img);
    });

    on_all_images_loaded(function(){
        // first, start loading images-spiski
        $(PAGE_IMAGE_SELECTOR).each(function(){
            load_image($(this));
        });
        on_all_images_loaded(function(){
            // now load the rest images in slider
            $('.pages img[data-src]').each(function(){
                load_image($(this));
            });
        });
    });
});

function load_image($img){
    $img.attr("src", $img.attr("data-src"));
}

// https://stackoverflow.com/a/11071687/222675
function on_all_images_loaded(callback){
    var imgs = document.images,
        len = imgs.length,
        counter = 0;

    [].forEach.call( imgs, function( img ) {
        if(img.complete)
            incrementCounter();
        else
            img.addEventListener( 'load', incrementCounter, false );
    } );

    function incrementCounter() {
        counter++;
        if ( counter === len ) {
            callback();
        }
    }
}

