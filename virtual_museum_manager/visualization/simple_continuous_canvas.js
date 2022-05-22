
var ContinuousVisualization = function(width, height, context) {
	var height = height;
	var width = width;
	var context = context;

	this.draw = function(model_render_data) {

	    var objects = model_render_data[0];
	    var rooms = model_render_data[1];

	    for (var i in objects) {
			var p = objects[i];
			if (p.Shape == "rect")
				this.drawRectange(p.x, p.y, p.w, p.h, p.Color, p.Filled);
			if (p.type == "exhibit")
				this.drawCircle(p.x, p.y, p.r, p.Color, p.Filled, p.Opacity);
			if (p.Shape == "image")
			    this.drawCustomImage(p.source, p.x, p.y, p.scale, p.text,p.text_color);
            if (p.type == "visitor"){
			    this.drawPacman(p.x, p.y, p.r, p.Color);
			    this.drawPath(p.path,p.path_color);
			}
		};

		rooms.forEach( room => {

		    vertices = room.vertices;
		    doors = room.doors;

		    wall_color = '#3477eb';
		    wall_thickness = 3;
		    door_color = '#ffffff';
		    door_thickness = 4;

		    doors.forEach(door => {
		        // Change the globalCompositeOperation to destination-over so that anything
                // that is drawn on to the canvas from this point on is drawn at the back
                // of what's already on the canvas
		        context.globalCompositeOperation = 'destination-over';
		        var [start_point,end_point] = door;

		        this.drawLine(start_point[0], start_point[1], end_point[0], end_point[1], door_color, door_thickness, "butt"); //door line
		    });

		    //draw the room's walls.
		    vertices.forEach((vertex, idx) => {
		        start = vertex
		        end = []

		        // if index is less than or equal to the penultimate one
		        if( idx < (vertices.length - 1) ){
		            // get the next point in the array as end point of the line
		            end = vertices[idx+1];
		        }
		        else{
		            // if we are at the last point of the array, we need to join it to the first one to close the shape
		            end = vertices[0]
		        }

		        //Start x and y values of the line
		        x_start = start[0];
		        y_start = start[1];

		         //End x and y values of the line
		        x_end = end[0];
		        y_end = end[1];

		        this.drawLine(x_start, y_start, x_end , y_end , wall_color, wall_thickness, "butt");

		    });
		});

		//return to normal
		context.globalCompositeOperation = 'source-over';

	};

	this.drawCircle = function(x, y, radius, color, fill, opacity) {

	    //Adjust opacity
	    context.globalAlpha = opacity;

		var cx = x * width;
		var cy = y * height;
		var r = radius;
		context.beginPath();
		context.arc(cx, cy, r, 0, Math.PI * 2, false);
		context.closePath();

		context.strokeStyle = color;
		context.stroke();

		if (fill) {
			context.fillStyle = color;
			context.fill();
		}

		//Return opacity to its default value
		context.globalAlpha = 1.0;

	};

	this.drawLine = function(x1, y1, x2, y2, color, thickness, linecap) {

		//denormalize
		var dx1 = Math.round(x1 * width);
		var dy1 = Math.round(y1 * height);
		var dx2 = Math.round(x2 * width);
		var dy2 = Math.round(y2 * height);

		context.beginPath();
		ctx.lineCap = linecap;
		context.moveTo(dx1, dy1);
		context.lineTo(dx2, dy2);
		context.lineWidth = thickness;
		context.strokeStyle = color;
		context.stroke();

	};

	this.drawPacman = function(x, y, radius, color) {
	    //this.resetCanvas();
		var cx = x * width;
		var cy = y * height;
		var r = radius;
		ctx = context;

		context.beginPath();
		ctx.arc(cx, cy, r, 0.2 * Math.PI, 1.8 * Math.PI, false);

		// Visual parameters
		context.lineWidth = 1;
		context.strokeStyle = 'Black';
		ctx.fillStyle = "yellow";

        // The mouth
        // A line from the end of the arc to the centre
        ctx.lineTo(cx, cy);

        // A line from the centre of the arc to the start
        ctx.closePath();

        // Fill the pacman shape
        ctx.fill();

        // Draw the outline
        ctx.stroke();


	};

	this.drawRectangle = function(x, y, w, h, color, fill) {
		context.beginPath();
		var dx = 5;
		var dy = 5;

		// Keep the drawing centered:
		var x0 = (x*width) - 0.5*dx;
		var y0 = (y*height) - 0.5*dy;

		context.strokeStyle = color;
		context.fillStyle = color;
		if (fill)
			context.fillRect(x0, y0, dx, dy);
		else
			context.strokeRect(x0, y0, dx, dy);
	};

	this.drawCustomImage = function (source, x, y, scale, text, text_color_) {
                var img = new Image();
                        img.src = "local/".concat(source);
                if (scale === undefined) {
                        var scale = 1
                }
                // Calculate coordinates so the image is always centered
                var dWidth = width * scale;
                var dHeight = width * scale;
                var cx = x * width + width / 2 - dWidth / 2;
                var cy = y * height + height / 2 - dHeight / 2;

                // Coordinates for the text
                var tx = (x + 0.5) * width;
                var ty = (y + 0.5) * height;


                img.onload = function() {
                        context.drawImage(img, cx, cy, dWidth, dHeight);
                        // This part draws the text on the image
                        if (text !== undefined) {
                                // ToDo: Fix fillStyle
                                // context.fillStyle = text_color;
                                context.textAlign = 'center';
                                context.textBaseline= 'middle';
                                context.fillText(text, tx, ty);
                        }
                }
    }

    this.drawPath = function (path,path_color){

        var past_path = path.slice(0,path.length - 1); //I dont want to paint the current position
        var trail_thickness = 1;
        var linecap = "round";

        for (var j = 0; j < past_path.length - 1; j++){

            var step = past_path[j];
            var x0 = step[0];
            var y0 = step[1];
            var x1 = step[0];
            var y1 = step[1];

            if(past_path.length > 1){
                next_step = past_path[j+1];
                x1 = next_step[0];
                y1 = next_step[1];
            }

            this.drawLine(x0,y0,x1,y1,path_color,trail_thickness, linecap);
        }
    }
	this.resetCanvas = function() {
	    context.resetTransform();
		context.clearRect(0, 0, width, height);
		context.beginPath();
	};
};

var Simple_Continuous_Module = function(canvas_width, canvas_height) {
    var rotateAngle = 0;
	var loadingAnimation = function(context,canvas){
	     canvas.width = canvas.width;
	     canvas.height = canvas.height;
	     center = [canvas.width/2, canvas.height/2]
	     loadingDrawing(context,center);
	     rotateAngle += 5;
	     if (rotateAngle > 360) {
            rotateAngle = 5;
         }
    }
    var loadingDrawing = function(context,center){
	    context.save();
	    x_center = center[0];
	    y_center = center [1];
        context.translate(x_center, y_center);
        context.rotate(rotateAngle * Math.PI/180);
        context.translate(-x_center, -y_center);

        context.beginPath();
        context.strokeStyle = "white";
        context.lineWidth = 15;
        context.lineCap = "round";

        context.fillStyle = "rgba(0, 131, 255,1)";
        context.moveTo(x_center, y_center - 30);
        context.lineTo(x_center, y_center - 100);
        context.stroke();

        context.strokeStyle = "rgba(0, 131, 255,0.8)";
        context.moveTo(x_center - 20 , y_center - 20);
        context.lineTo(x_center - 70, y_center - 70);
        context.stroke();

        context.strokeStyle = "rgba(0, 131, 255,0.5)";
        context.moveTo(x_center - 30, y_center);
        context.lineTo(x_center - 100, y_center);
        context.stroke();

        context.strokeStyle = "rgba(0, 131, 255,0.35)";
        context.moveTo(x_center - 20 , y_center + 20);
        context.lineTo(x_center - 70, y_center + 70);
        context.stroke();

        context.strokeStyle = "rgba(0, 131, 255,0.2)";
        context.moveTo(x_center, y_center + 30);
        context.lineTo(x_center, y_center + 100);
        context.stroke();

        context.closePath();

        context.save();

        context.restore();
	}
	// Create the canvas
	// ------------------

	// Create the tag:
	var canvas_tag = "<canvas width='" + canvas_width + "' height='" + canvas_height + "' ";
	canvas_tag += "style='border:1px solid #3477eb;'></canvas>";
	// border:1px solid #3477eb
	// Append it to body:
	var canvas = $(canvas_tag)[0];
	$('div.container').removeClass('container').addClass('container-fluid');
	$('#sidebar').removeClass('col-lg-4').addClass('col-lg-3');
	$('#elements').removeClass('col-lg-8').addClass('col-lg-9');
	$("#elements").append(canvas);

	// Create the context and the drawing controller:
	var context = canvas.getContext("2d");

	var loader_interval = setInterval(function(){
	    loadingAnimation(context,canvas);
    }, 100);

	var canvasDraw = new ContinuousVisualization(canvas_width, canvas_height, context);
	var loader_cleared = false;
	this.render = function(data) {
	    if(!loader_cleared){
	        clearInterval(loader_interval);
	        console.log("clear");
	        loader_cleared = true;
	    }
		canvasDraw.resetCanvas();
		canvasDraw.draw(data);
	};

	this.reset = function() {
		canvasDraw.resetCanvas();
	};


};
