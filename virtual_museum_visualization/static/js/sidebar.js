/********************************
*        Helper functions
********************************/

/** Check whether current route and new route are the same */
function _goingToSameRoute(newRoute){
    var currentRoute = window.location.pathname;
    return newRoute === currentRoute;
}

/********************************
*        Functionalities
********************************/

/** To open and close sidebar */
function toggleMenu(){
    var menu = $('#sidebar-container');
    menu.toggleClass('st-effect-1 st-menu-open');
}

/** Handle sidebar navigation to set active links and avoid reloading if
 current page and next page are the same */
function navigate(route){
    var sameRoute = _goingToSameRoute(route);
    if (!sameRoute){
        location.href = route;
    }
}

function makeNavigatableLinks(){
    links = $('nav').find('a');
    links.each(function(index, link){
        var route = "/" + $(link).attr('id');
        $(link).on('click',function(){
            navigate(route)
         });
    });
}

function setActiveLink(){
    var currentRoute = window.location.pathname;
    var identifier = currentRoute.split("/")[1];
    $('#'+identifier).addClass("active");
}



/*
* Initialise Sidebar
*/
$(document).ready(function(){
    // Attach event listeners to open and close sidebar
    var userButton = $('#user');
    var closeMenu = $('span.close-sidebar');
    userButton.on('click',toggleMenu);
    closeMenu.on('click', toggleMenu);

    // Sets the active sidebar link
    makeNavigatableLinks();
    setActiveLink();

});