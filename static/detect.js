// elements
const s = document.getElementById('objDetect');

// attribs
const sourceVideo = s.getAttribute("data-source");  //the source video to use
const uploadWidth = s.getAttribute("data-uploadWidth") || 800; //the width of the upload file
const mirror =  false; //mirror the boundary boxes
const scoreThreshold = s.getAttribute("data-scoreThreshold") || 0.5;
const detectUrl = window.location.origin + '/detect';
const updateUrl = window.location.origin + '/train';

//Video element selector
v = document.getElementById(sourceVideo);

//for starting events
let isPlaying = false,
gotMetadata = false;
let isCaptureExample = false;
let examplesNum = 0;
let maxExamples = 10;
let exampleSize = 160;

//Canvas setup

//create a canvas to grab an image for upload
let imageCanvas = document.createElement('canvas');
let imageCtx = imageCanvas.getContext("2d");

//document.getElementById('examplesPic').appendChild(exCtx);

//create a canvas for drawing object boundaries
let drawCanvas = document.createElement('canvas');

var rect = v.getBoundingClientRect();
console.log("Video box:", rect.top, rect.right, rect.bottom, rect.left);

document.getElementById('videoDiv').appendChild(drawCanvas);
//document.getElementById('buttons').style.top = rect.bottom + 10;
let drawCtx = drawCanvas.getContext("2d");

function uploadScale() {
    return v.videoWidth > 0 ? uploadWidth / v.videoWidth : 0;
}


//draw boxes and labels on each detected object
function drawBoxes(objects) {
	
    //clear the previous drawings
    drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
	
    //filter out objects that contain a class_name and then draw boxes and labels on each
    objects.forEach(face => {
        let scale = 1;
        let _x = face.x / scale;
        let y = face.y / scale + rect.top;
        let width = face.w / scale;
        let height = face.h / scale;
        //flip the x axis if local video is mirrored
        if (mirror) {
            x = drawCanvas.width - (_x + width)
        } else {
            x = _x + rect.left;
        }

        //let rand_conf = face.confidence.toFixed(2);
        let title = "";
        if (face.name != "unknown") {
            drawCtx.strokeStyle = "magenta";
            drawCtx.fillStyle = "magenta";
            title += ' - ' + face.name
            
            title += "[" + face.predict_proba + "]";
            
        } else {
            drawCtx.strokeStyle = "cyan";
            drawCtx.fillStyle = "cyan";
        }
        drawCtx.fillText(title , x + 5, y - 5);
        drawCtx.strokeRect(x,y, width, height);


    });
}

//Add file blob to a form and post
function postFile(file) {

    //Set options as form data
    let formdata = new FormData();
    formdata.append("image", file);
    formdata.append("threshold", scoreThreshold);

    let xhr = new XMLHttpRequest();
    xhr.open('POST', detectUrl, true);
    xhr.onload = function () {
        if (this.status === 200) {
            let objects = JSON.parse(this.response);

            //draw the boxes
            drawBoxes(objects);

            //Save and send the next image
            imageCtx.drawImage(v, 0, 0, v.videoWidth, v.videoHeight, 0, 0, uploadWidth, uploadWidth * (v.videoHeight / v.videoWidth));
            imageCanvas.toBlob(postFile, 'image/jpeg');
        }
        else {
            console.error(xhr);
        }
    };
    xhr.send(formdata);
}


//Start object detection
function startObjectDetection() {

    console.log("starting object detection");

    //Set canvas sizes base don input video
    drawCanvas.width = v.videoWidth;
    drawCanvas.height = v.videoHeight;

    imageCanvas.width = uploadWidth;
    imageCanvas.height = uploadWidth * (v.videoHeight / v.videoWidth);

    //Some styles for the drawcanvas
    drawCtx.lineWidth = 4;
    drawCtx.strokeStyle = "cyan";
    drawCtx.font = "20px Verdana";
    drawCtx.fillStyle = "cyan";

    //Save and send the first image
    imageCtx.drawImage(v, 0, 0, v.videoWidth, v.videoHeight, 0, 0, uploadWidth, uploadWidth * (v.videoHeight / v.videoWidth));
    imageCanvas.toBlob(postFile, 'image/jpeg');

}


function updateModel() {
    console.log("updating model...")
    //Save and send the next image
    exCanvas.toBlob(postExamplesFile, 'image/jpeg');
}

// EVENTS

//check if metadata is ready - we need the video size
v.onloadedmetadata = () => {
    console.log("video metadata ready");
    gotMetadata = true;
    if (isPlaying)
        startObjectDetection();
};

//see if the video has started playing
v.onplaying = () => {
    console.log("video playing");
    isPlaying = true;
    if (gotMetadata) {
        startObjectDetection();
    }
};

function toggleFullScreen() {
  if (!document.fullscreenElement) {

    var elem = document.getElementById("myVideo");
    if (elem.requestFullscreen) {
      elem.requestFullscreen();
    } else if (elem.mozRequestFullScreen) {
      elem.mozRequestFullScreen();
    } else if (elem.webkitRequestFullscreen) {
      elem.webkitRequestFullscreen();
    } else if (elem.msRequestFullscreen) {
      elem.msRequestFullscreen();
    }

  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    }
  }
}



window.onload = () => {
    document.getElementById("full").onclick = () => {
        toggleFullScreen();
       };
    

};


