import { MesaController } from './mesa_driver.js'

/*
 * Context menu for selected item
 */

var ContextMenu;
ContextMenu = function (blueprint3d, mesacontroller) {
    var mesacontroller = mesacontroller;
    var three = blueprint3d.three;
    var orbitControls = three.controls;
    var paintingFov = 400;
    var qrcode = new QRCode(document.getElementById("qrcode"), {
            text: "http://example.org",
            width: 64,
            height: 64,
            colorDark : "#000000",
            colorLight : "#ffffff",
            correctLevel : QRCode.CorrectLevel.H
    });

    function init() {
        three.itemSelectedCallbacks.add(itemSelected);
        three.itemUnselectedCallbacks.add(itemUnselected);
        // Trigger close item menu when close button is pressed
        $('#item-context-menu .close-wrapper').on('click', closeItemMenu);
    }
    /**
    * Select item if it is within the specified FoV
    */

    function itemSelected(item) {
        // We dont want to select doors
        if (item.metadata.itemName === "Open Door"){
            return;
        }

        const isPaintingSelectable = paintingWithinReach(item);
        if (isPaintingSelectable){
            qrcode.makeCode(item.uuid);
            $('#item-context-menu>div').scrollTop(0);
            showPaintingInfo(item);
            mesacontroller.watchPainting(item.metadata.itemName);

        }

        if( !isPaintingSelectable && $('.move-closer-message').is(':animated')){
                $('.move-closer-message').stop().animate({opacity:'100'});
        }
        if( !isPaintingSelectable){
            $('.move-closer-message').show();
            $('.move-closer-message').fadeOut(3000);
        }




    }

    function showPaintingInfo(item){
        $("#painting-title").text(item.metadata.itemName);
        $("#painting-author").text(item.metadata.author);
        $("#painting-description").text(item.metadata.description);

        $("#item-context-menu").addClass('st-effect-1 st-menu-open');
        $("#context-menu").show();
    }

    function paintingWithinReach(painting){
        const position = orbitControls.object.position;
        const paintingPosition = painting.position;
        const distance = position.distanceTo(paintingPosition);
        return (distance <= paintingFov);

    }

    /*
    * Triggered when we click away from the item information menu
    * without having to click the close item menu button.
    */
    function itemUnselected() {
        closeItemMenu();

    }

    function closeItemMenu(){
         $('#item-context-menu').removeClass('st-effect-1 st-menu-open');
    }

    init();
};

/*
 * Triggers loading modal while items are being loaded.
 */

var ModalEffects = function(blueprint3d) {

    var blueprint3d = blueprint3d;
    var itemsLoading = 0;

    function update() {
        if (itemsLoading > 0) {
            $("#loading-modal").show();
        } else {
            setTimeout(function(){
               $("#loading-modal").fadeOut();
            },5000);
        }
    }

    function init() {
        blueprint3d.model.scene.itemLoadingCallbacks.add(function() {
            itemsLoading += 1;
            update();
        });

        blueprint3d.model.scene.itemLoadedCallbacks.add(function() {
            itemsLoading -= 1;
            update();
        });

        $("#loading-modal2").hide();
        update();
    }

    init();
};


/*
 * Initialize!
 */


$('#toggle-fullscreen').on('click', function(){
    var elem = document.documentElement;

    if ($('#toggle-fullscreen').hasClass('fullscreen')){
         elem.requestFullscreen({ navigationUI: "hide" }).then(() => { $('#toggle-fullscreen').removeClass('fullscreen')}).catch(err => {
         });
    }
    else{
         elem.requestFullscreen({ navigationUI: "show" }).then(() => { $('#toggle-fullscreen').addClass('fullscreen')}).catch(err => {
         });
    }

});

$(document).ready(function() {

    // main setup
    var opts = {
        floorplannerElement: 'floorplanner-canvas',
        threeElement: '#viewer',
        threeCanvasElement: 'three-canvas',
        textureDir: "models/textures/",
        widget: false
    }
    var blueprint3d = new BP3D.Blueprint3d(opts);
    $("#viewer").show();
    $('#floorplanner').remove();
    blueprint3d.three.updateWindowSize();

    /* ModalEffects: used to show the loading modal while
    *  items are being added to the view.
    */
    var modalEffects = new ModalEffects(blueprint3d);

    /* MesaController: allows communicating RAMEN with Mesa to map
    *  movements.
    */
    var mesaController = new MesaController(blueprint3d);

    /* ContextMenu: used to control the menu that appears when a painting
    *  is selected
    */
    var contextMenu = new ContextMenu(blueprint3d, mesaController);

    // var cameraButtons = new CameraButtons(blueprint3d);


    // Load floorplan
    $.ajax('/static/floorplans/museum_floorplan.json', {
        async: false,
        dataType: 'text',
        success: function (data) {
            blueprint3d.model.loadSerialized(data);
        }
    });
    setTimeout(()=>window.stop(), 5000);

});
