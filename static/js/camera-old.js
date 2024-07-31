document.addEventListener("DOMContentLoaded", function () {
  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");
  const context = canvas.getContext("2d");
  const captureButton = document.getElementById("capture-button");
  const personNameInput = document.getElementById("person-name");
  const trainButton = document.getElementById("train-button");
  const cameraSelect = document.getElementById("camera-select");

  let currentStream = null;
  let boundary = null;

  // Load available cameras and populate the camera selection dropdown
  async function loadCameras() {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const cameraDevices = devices.filter((device) => device.kind === "videoinput");

      cameraSelect.innerHTML = '';//<option value="">Select Camera</option>';

      for (const device of cameraDevices) {
        const option = document.createElement("option");
        option.value = device.deviceId;
        option.text = device.label || `Camera ${cameraDevices.indexOf(device) + 1}`;
        cameraSelect.appendChild(option);
      }
      $('#camera-select').select2({
        placeholder: "Select Camera"
      });
    } catch (error) {
      console.error("Error loading cameras:", error);
    }
  }

  // Attach event listeners
  captureButton.addEventListener("click", captureImage);
  trainButton.addEventListener("click", updateClassifiers);

  $("#camera-select").on('select2:select', function (e) {
    if (currentStream) {
        currentStream.getTracks().forEach((track) => track.stop());
    }
    console.log(e);
    console.log(">>>> " + e.params.data.id);
    const selectedCameraId = e.params.data.id; // Get selected camera ID
    //startCamera(selectedCameraId);
    //recognizeRealtime(selectedCameraId); // Call the function for real-time recognition
  });

  // Initialize camera and camera selection
  loadCameras();//.then(() => startCamera());

  // Function to start the camera stream
  /*
  async function startCamera(cameraId) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { deviceId: cameraId ? { exact: cameraId } : undefined },
      });

      currentStream = stream;
      video.srcObject = stream;
      video.play();
    } catch (error) {
      console.error("Error accessing camera:", error);
    }
  }*/

// Function to start the camera stream
/*
async function startCamera(cameraId) {
  try {
    // Send selected camera ID to the server for initialization
    const response = await fetch("/recognize_realtime", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ camera_id: cameraId }),
    });

    const data = await response.json();

    if (data.success) {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { deviceId: cameraId ? { exact: cameraId } : undefined },
      });

      currentStream = stream;
      video.srcObject = stream;
      video.play();

      // Clear the canvas
      context.clearRect(0, 0, canvas.width, canvas.height);
    } else {
      console.error("Camera initialization failed:", data.message);
    }
  } catch (error) {
    console.error("Error accessing camera:", error);
  }
}

  async function startCamera(cameraId) {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { deviceId: cameraId ? { exact: cameraId } : undefined },
        });

        currentStream = stream;
        video.srcObject = stream;
        video.play();
    } catch (error) {
        console.error("Error accessing camera:", error);
    }
}

// Function to draw rectangles around detected faces
function drawFaceRectangles(faces) {
  // Clear previous rectangles
  context.clearRect(0, 0, canvas.width, canvas.height);

  // Draw new rectangles
  for (const [x, y, w, h] of faces) {
    context.strokeStyle = "green";
    context.lineWidth = 2;
    context.beginPath();
    context.rect(x, y, w, h);
    context.stroke();
  }
}*/

  // Function to capture an image and send it for registration
/*
  async function captureImage() {
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL("image/jpeg");

    // Send captured image and person name to server for registration
    const response = await fetch("/register_face", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        person_name: personNameInput.value,
        image_data: imageData,
      }),
    });

    const data = await response.json();
    alert(data.message);

    // Clear the canvas
    context.clearRect(0, 0, canvas.width, canvas.height);
  }*/

  // Function to capture an image and send it for registration
    async function captureImage() {
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const imageData = canvas.toDataURL("image/jpeg");

      // Send captured image and person name to server for registration
      const response = await fetch("/register_face", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          person_name: personNameInput.value,
          image_data: imageData,
        }),
      });

      const data = await response.json();
      alert(data.message);

      // Clear the canvas
      context.clearRect(0, 0, canvas.width, canvas.height);
    }


  // Function to update classifiers
  async function updateClassifiers() {
    const response = await fetch("/update_classifiers", { method: "POST" });
    const data = await response.json();
    alert(data.message);
  }

  // Function to render recognized faces on the canvas
  function renderRecognizedFaces(faces) {
    context.clearRect(0, 0, canvas.width, canvas.height);
    for (const [x, y, w, h] of faces) {
      context.strokeStyle = "green";
      context.lineWidth = 2;
      context.strokeRect(x, y, w, h);
    }
  }

  async function recognizeRealtime(cameraId) {
        try {
            // Continuously send image data for recognition
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { deviceId: cameraId },
            });

            const imageCapture = new ImageCapture(stream.getVideoTracks()[0]);
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');

            const interval = setInterval(async () => {
                try {
                    const photo = await imageCapture.takePhoto();
                    context.drawImage(photo, 0, 0, canvas.width, canvas.height);
                    const imageData = canvas.toDataURL("image/jpeg");

                    const response = await fetch("/recognize_realtime", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/x-www-form-urlencoded",
                        },
                        body: `camera_id=${encodeURIComponent(cameraId)}&image_data=${encodeURIComponent(imageData)}`,
                    });

                    const data = await response.json();
                    const message = data.message;
                    // Update message or other UI elements as needed
                    document.getElementById('message').textContent = message;
                } catch (error) {
                    console.error("Error sending image for recognition:", error);
                }
            }, 1000); // Adjust interval as needed

            // Stop the interval when needed
            // clearInterval(interval);

        } catch (error) {
            console.error("Error accessing camera for real-time recognition:", error);
        }
    }

});
