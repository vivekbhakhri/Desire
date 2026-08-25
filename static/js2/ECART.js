


$(document).ready(function () {
    $(".icon").click(function () {
        $(".new-menu-box").animate({
            width: "toggle"
        }, 200, "linear");
    });
});


$(document).ready(function () {
    $(".close").click(function () {
        $(".new-menu-box").animate({
            width: "toggle"
        }, 200, "linear");
    });
});


//   $(document).ready(function () {
//     $("body").click(function () {

//         var bdivIsVisible;
//         bdivIsVisible = $('.new-menu-box').is(':visible');
//     if (bdivIsVisible) {

//         $(".new-menu-box").animate({
//             width: "toggle"
//         }, 200, "linear");
//     }

//     });
// });

// ////////////
$(document).ready(function () {
    $(".icon").click(function () {
        $(".close").fadeToggle(300);
        $(".icon").fadeToggle(300);
    });
});


$(document).ready(function () {
    $(".close").click(function () {
        $(".close").fadeToggle(300);
        $(".icon").fadeToggle(300);


//         if ($(".new-sub-category").css("display", "block")) {
//         $(".c-u-aero").fadeToggle(100);
//         $(".c-d-aero").fadeToggle(100);
//          $(".new-sub-category").slideUp(200);
//         $(".new-sub-register").slideUp(200);
//         $(".new-sub-login").slideUp(200);
// }

 var cdivIsVisible;
  var rdivIsVisible;
   var ldivIsVisible;
    
    cdivIsVisible = $('.new-sub-category').is(':visible');
    if (cdivIsVisible) {
        
        $(".c-u-aero").fadeToggle(100);
        $(".c-d-aero").fadeToggle(100);
         $(".new-sub-category").slideUp(200);

    }

    rdivIsVisible = $('.new-sub-register').is(':visible');
    if (rdivIsVisible) {
        
        $(".r-u-aero").fadeToggle(100);
        $(".r-d-aero").fadeToggle(100);
        $(".new-sub-register").slideUp(200);

    }

    ldivIsVisible = $('.new-sub-login').is(':visible');
    if (ldivIsVisible) {
        
        $(".l-u-aero").fadeToggle(100);
        $(".l-d-aero").fadeToggle(100);
        $(".new-sub-login").slideUp(200);

    }


    });
});

// $(document).ready(function(){ 

//     if ($("new-sub-category").css("display", "none")) {
//         $("body").css("background", "green");
//     } 
//     else {
//         $("body").css("background", "orange");
//     }

// });


// ///////////
$(document).ready(function () {
    $(".new-category-dropdown").click(function () {
        $(".new-sub-category").slideToggle(200);
        $(".c-u-aero").fadeToggle(100);
        $(".c-d-aero").fadeToggle(100);

         var rdivIsVisible;
   var ldivIsVisible;

        rdivIsVisible = $('.new-sub-register').is(':visible');
    if (rdivIsVisible) {
        
        $(".r-u-aero").fadeToggle(100);
        $(".r-d-aero").fadeToggle(100);
        $(".new-sub-register").slideUp(200);

    }

    ldivIsVisible = $('.new-sub-login').is(':visible');
    if (ldivIsVisible) {
        
        $(".l-u-aero").fadeToggle(100);
        $(".l-d-aero").fadeToggle(100);
        $(".new-sub-login").slideUp(200);

    }

    });
});

$(document).ready(function () {
    $(".new-register-dropdown").click(function () {
        $(".new-sub-register").slideToggle(200);
        $(".r-u-aero").fadeToggle(100);
        $(".r-d-aero").fadeToggle(100);

         var cdivIsVisible;
  var rdivIsVisible;
   var ldivIsVisible;
    
    cdivIsVisible = $('.new-sub-category').is(':visible');
    if (cdivIsVisible) {
        
        $(".c-u-aero").fadeToggle(100);
        $(".c-d-aero").fadeToggle(100);
         $(".new-sub-category").slideUp(200);

    }

    ldivIsVisible = $('.new-sub-login').is(':visible');
    if (ldivIsVisible) {
        
        $(".l-u-aero").fadeToggle(100);
        $(".l-d-aero").fadeToggle(100);
        $(".new-sub-login").slideUp(200);

    }

    });
});


$(document).ready(function () {
    $(".new-login-dropdown").click(function () {
        $(".new-sub-login").slideToggle(200);
        $(".l-u-aero").fadeToggle(100);
        $(".l-d-aero").fadeToggle(100);

        var cdivIsVisible;
  var rdivIsVisible;
    
    cdivIsVisible = $('.new-sub-category').is(':visible');
    if (cdivIsVisible) {
        
        $(".c-u-aero").fadeToggle(100);
        $(".c-d-aero").fadeToggle(100);
         $(".new-sub-category").slideUp(200);
    }

    rdivIsVisible = $('.new-sub-register').is(':visible');
    if (rdivIsVisible) {
        
        $(".r-u-aero").fadeToggle(100);
        $(".r-d-aero").fadeToggle(100);
        $(".new-sub-register").slideUp(200);

    }

    });
});

