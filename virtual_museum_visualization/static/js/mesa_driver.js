/********************************
*        Calls to Mesa
********************************/
export function MesaController(blueprint3d){
    var three = blueprint3d.three;
    var orbitControls = three.controls;
    var initialZ = 2300;
    var panSpeed = 100;
    var panUnit = 0; // Modulus of minimum movement vector
    var disableMESA = false;
    var endpointMESA = "http://localhost:1331"
    var tourTime = 0;
    var enableControls = false;

    /*
     * Set visitor's starting z position
    */
    const startOnZPosition = function(z){
        const v1x = orbitControls.object.position.x;
        const v1z = orbitControls.object.position.z;
        orbitControls.panXY(0, 1);
        const v2x = orbitControls.object.position.x;
        const v2z = orbitControls.object.position.z;
        const diffx = v2x - v1x;
        const diffz = v2z - v1z;
        panUnit = Math.sqrt(Math.pow(diffx,2) + Math.pow(diffz, 2));
        three.adjustZComponent(z, panUnit);

    }

    /*
     * Update tour time
    */
    const updateTime = function(){
        tourTime += 1;
        const hhmmss = new Date(tourTime * 1000).toISOString().slice(11, 19);
        $('#tour-time').text(hhmmss);
    }


    /* Handle Movement with Keys */
    const onKeyDown = async function (event){
        const modulusMultiplier = panUnit*panSpeed;
        let v1x, v1z, v2x, v2z, diffx, diffz = 0
        let canMove = false;

        // Before clicking on the "Start tour button" we must not be able
        // to advance
        if(!enableControls){
            return;
        }

        switch(event.key){
            case 'w':

                v1x = orbitControls.object.position.x;
                v1z = orbitControls.object.position.z;

                if(orbitControls.isRotatingCamera && !disableMESA){
                    setPosition(v1x, v1z);
                    orbitControls.isRotatingCamera = false;
                }

                // MOVEMENT
                if(!disableMESA){
                    canMove = await move('UP', orbitControls.accumulatedRotation, modulusMultiplier);
                    if (canMove){
                        orbitControls.panXY(0, panSpeed);
                    }
                }
                else{
                    orbitControls.panXY(0, panSpeed);
                }

                // AFTER
                v2x = orbitControls.object.position.x;
                v2z = orbitControls.object.position.z;

                // DIFFERENCE
                diffx = v2x - v1x;
                diffz = v2z - v1z;

                break;

            case 'a':

                v1x = orbitControls.object.position.x;
                v1z = orbitControls.object.position.z;

                if(orbitControls.isRotatingCamera && !disableMESA){
                    setPosition(v1x, v1z);
                    orbitControls.isRotatingCamera = false;
                }

                // MOVEMENT
                if(!disableMESA){
                    canMove = await move('LEFT', orbitControls.accumulatedRotation, modulusMultiplier);
                    if (canMove){
                        orbitControls.panXY(panSpeed, 0);
                    }
                }
                else{
                    orbitControls.panXY(panSpeed, 0);
                }

                // AFTER
                v2x = orbitControls.object.position.x;
                v2z = orbitControls.object.position.z;

                // DIFFERENCE
                diffx = v2x - v1x;
                diffz = v2z - v1z;


                break;

            case 's':

                v1x = orbitControls.object.position.x;
                v1z = orbitControls.object.position.z;

                if(orbitControls.isRotatingCamera && !disableMESA){
                    setPosition(v1x, v1z);
                    orbitControls.isRotatingCamera = false;
                }

                // MOVEMENT
                if(!disableMESA){
                    canMove = await move('DOWN', orbitControls.accumulatedRotation, modulusMultiplier);
                    if (canMove){
                        orbitControls.panXY(0, -panSpeed);
                    }
                }
                else{
                    orbitControls.panXY(0, -panSpeed);
                }

                // AFTER
                v2x = orbitControls.object.position.x;
                v2z = orbitControls.object.position.z;



                // DIFFERENCE
                diffx = v2x - v1x;
                diffz = v2z - v1z;


                break;

            case 'd':

                v1x = orbitControls.object.position.x;
                v1z = orbitControls.object.position.z;

                if(orbitControls.isRotatingCamera && !disableMESA){
                    setPosition(v1x, v1z);
                    orbitControls.isRotatingCamera = false;
                }

                // MOVEMENT
                if(!disableMESA){
                    canMove = await move('RIGHT', orbitControls.accumulatedRotation, modulusMultiplier);
                    if (canMove){
                        orbitControls.panXY(-panSpeed, 0);
                    }
                }
                else{
                    orbitControls.panXY(-panSpeed, 0);
                }

                // AFTER
                v2x = orbitControls.object.position.x;
                v2z = orbitControls.object.position.z;


                // DIFFERENCE
                diffx = v2x - v1x;
                diffz = v2z - v1z;


                break;

            default:
                break;

        }

    }
    const move = async function(direction, axisRotationAngle, modulusMultiplier) {

        const payload = {
            "instruction_type": "move_visitor",
            "data":{
                    "rotation": axisRotationAngle,
                    "direction": direction,
                    "modulus_multiplier":modulusMultiplier
                    }
        };

        try {
            const res = await postData(payload);
            const jsonResponse = JSON.parse(res);
            const canMove = jsonResponse["movement_allowed"];
            if (canMove){
                const travelScore = jsonResponse["travel_score"];
                $('#tour-points').text(travelScore);
}
            return canMove;
        } catch(err) {
            return false;
        }


    }

    const setPosition = function(posx, posy) {
        const pos_x = posx;
        const pos_y = posy;
        const payload = {
            "instruction_type": "set_position",
            "data":{
                "position": {
                  "x": pos_x,
                  "y": pos_y
                }
            }
        };

        try {
            postData(payload);
        } catch(err) {
            console.log(err);
        }


    }

    this.watchPainting = function(painting_name) {

        const payload = {
            "instruction_type": "watch_painting",
            "data":{
                    "painting_name": painting_name,
                    }
        };
        try {
            postData(payload).then((response) =>{
                const jsonResponse = JSON.parse(response);
                const travelScore = jsonResponse["travel_score"];
                $('#tour-points').text(travelScore);
            })
        } catch(err) {
            console.log(err);
        }
    }

    const postData = function(payload){
        return $.ajax(endpointMESA + '/api/v1', {
            type: 'POST',
            crossDomain: true,
            data: JSON.stringify(payload)
        });
    }

    const finishTour = function(){
        try {
            const username = $('#username').text();
            const payload = {
                "instruction_type": "finish_tour",
                "data":{"username": username}
            };
            $('#finish-tour-modal').show();
            postData(payload);
            setTimeout(() => {
                location.href = 'museum-reset-tour'},
                3000);

            } catch(err) {
                console.log(err);
            }
    }



    /**  Initialiser Function */
    const init = function(){
        console.log('Mesa Driver v1.0');

        // Add event listener to wasd movement keys.
        $(document).on('keydown',onKeyDown);

        /* Adjust z position after a few seconds to make sure RAMEN
         * has loaded everything else and the desired z position is
         * achieved.
        */
       
        setTimeout(() => startOnZPosition(initialZ) ,4000);
        $('#start-tour').click(() => {
            try {
                 const payload = {"instruction_type": "start_tour",
                     "data":{}};
                 postData(payload)
            } catch(err) {
                console.log(err);
            }
            setInterval(() => updateTime(), 1000);
            $('#welcome-modal').hide();
            // allow movement
            enableControls = true;
        });
        $('#museum-finish-tour').click(() => finishTour());

    }

    // Initialise
    init();
}


