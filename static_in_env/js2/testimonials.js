$(document).ready(function(){
  $('.owl-carousel').owlCarousel({
    nav: false,
	dots: true,
    loop: true,
    autoplay: true,
    autoplayTimeout: 5000,
	margin: 20,
	slideSpeed: 3000,
	animateIn: 'fadeIn',
    animateOut: 'fadeOut',
    responsive: {
        0:{
            items: 1
        },
        600:{
            items: 2
        },
		960: {
			items: 3
		}
    }
});
	
	
	

var setMinHeight = function(minheight = 0) {
  jQuery('.owl-carousel').each(function(i,e){
    var oldminheight = minheight;
    jQuery(e).find('.owl-item').each(function(i,e){
      minheight = jQuery(e).height() > minheight ? jQuery(e).height() : minheight;    
    });
    jQuery(e).find('.item').css("min-height",minheight + "px");
    minheight = oldminheight;
  });
};

	setMinHeight();
});

$(document).on('resize', function(){
		setMinHeight();
});