//Get camera video
const constraints = {
    audio: false,
    video: {
		facingMode: "environment" ,
//        width: {min: 640, ideal: 1280, max: 1920},
//        height: {min: 480, ideal: 720, max: 1080}
        width: {min: 800, ideal: 800, max: 800},

        height: {min: 600, ideal: 600, max: 600}
//        width: {min: 640, ideal: 1280, max: 1920},
//        height: {min: 480, ideal: 720, max: 1080}
    }
};

navigator.mediaDevices.getUserMedia(constraints)
    .then(stream => {
        document.getElementById("myVideo").srcObject = stream;
        console.log("Got local user video");

    })
    .catch(err => {
        console.log('navigator.getUserMedia error: ', err)
    });
