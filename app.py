import csv
import datetime
import cv2
import numpy as np
import base64
import io
import os
import time
from flask import Flask, render_template, request, jsonify, Response
from PIL import Image

app = Flask(__name__)

# Load Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/live_feed')
def live_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    # Initialize camera capture
    camera = cv2.VideoCapture(0)  # 0 represents the default camera (webcam)

    while True:
        success, frame = camera.read()  # Read a frame from the camera

        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces using the cascade classifier
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        _, img_encoded = cv2.imencode('.jpg', frame)
        img_base64 = base64.b64encode(img_encoded).decode('utf-8')

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img_encoded.tobytes() + b'\r\n')

# Recognize faces in real-time
@app.route('/recognize_realtime', methods=['POST'])
def recognize_realtime():
    (images, labels, names, id) = ([], [], {}, 0)

    # Prepare datasets for Training of Cascade Classifier
    datasets = 'static/face_registry'  # Update this with the actual path to your dataset

    # Check if there are available datasets
    if not os.path.exists(datasets) or not os.listdir(datasets):
        recognized_data = {
            'name': '',
            'time': '',
            'message': 'No Datasets available for training'
        }
        return jsonify(recognized_data)

    for (subdirs, dirs, files) in os.walk(datasets):
        for subdir in dirs:
            names[id] = format(subdir.replace('_', ' '))
            subjectpath = os.path.join(datasets, subdir)
            for filename in os.listdir(subjectpath):
                path = subjectpath + '/' + filename
                label = id
                images.append(cv2.imread(path, 0))
                labels.append(int(label))
            id += 1
    
    (width, height) = (1200, 700)
    (images, labels) = [np.array(lis) for lis in [images, labels]]

    model = cv2.face.LBPHFaceRecognizer_create() 
    model.train(images, labels)

    recognized_data = {
        'name': '',
        'time': '',
        'message': 'Student Not Recognized'
    }

    def main():
        webcam = cv2.VideoCapture(0)

        # Prepare file for storing data, what was used here was using a CSV file
        # But its your choice if you prefer to use Database such sa SQLite Database
        if os.path.isfile("data_files/Attendance.csv") == False:
            with open('data_files/Attendance.csv', "w", newline="") as f:
                wr = csv.writer(f)
                wr.writerow(["Name", "Attendance", "Date", "Time"])

        while True:
            
            (_, im) = webcam.read()
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for(x,y,w,h) in faces:
                cv2.rectangle(im, (x,y), (x+w, y+h), (0,51,255), 3)
                face = gray[y:y+h, x:x+w]
                face_resize = cv2.resize(face, (width, height))

                prediction = model.predict(face_resize)
                cv2.rectangle(im, (x,y), (x+w, y+h), (0,255,0), 3)

                cPredictions = prediction[1]
                if prediction[1] < 100:
                    # Open teh CSV file for reading
                    # On this sport also were you can prepare the data for saving in database other than CSV
                    with open('data_files/Attendance.csv', "r", newline="") as f:
                        con = csv.reader(f)
                        for i in con:
                            if (i[0] == names[prediction[0]]) and (i[2] == str(datetime.date.today())):
                                cv2.putText(im, '%s -Marked Present at %s'%(names[prediction[0]], i[-1]), (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0,51,255))

                                recognized_data['name'] = names[prediction[0]]
                                recognized_data['time'] = datetime.datetime.now().strftime("%I:%M %p")
                                recognized_data['message'] = 'Student Recognized and Marked Present'
                                break
                        else:
                            with open('data_files/Attendance.csv', "a", newline="") as f:  # Use append mode
                                wr = csv.writer(f)
                                wr.writerow([names[prediction[0]], "Present", datetime.date.today(), datetime.datetime.now().strftime("%I:%M %p")])
                                cv2.putText(im, '%s - Marked Present'%(names[prediction[0]]), (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0,51,255))
                                
                                recognized_data['name'] = names[prediction[0]]
                                recognized_data['time'] = datetime.datetime.now().strftime("%I:%M %p")
                                recognized_data['message'] = 'Student Recognized and Marked Present'
                                break

                    # Close the camera view when attendance is recorded
                    cv2.destroyAllWindows()
                    return jsonify(recognized_data)

                else:
                    cv2.putText(im, 'Student Not Recognised', (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0,51,255))

            cv2.namedWindow("Face Capturing & Attendance", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Face Capturing & Attendance", 800, 650)
            cv2.imshow('Face Capturing & Attendance', im)
            cv2.setWindowProperty('Face Capturing & Attendance', cv2.WND_PROP_TOPMOST, 1)

            key = cv2.waitKey(10)
            if key == 27: # press esc key to stop
                cv2.destroyAllWindows()
                break

    main()

    return jsonify(recognized_data)

@app.route('/register_face', methods=['GET', 'POST'])
def register_face():
    alert_message = ""

    if request.method == 'POST':
        name = request.form['name']
        sub_data = format(name.replace(' ', '_'))
        path = os.path.join('static/face_registry', sub_data)

        if os.path.isdir(path):
            count = len([sub_data for sub_data in os.listdir(path) if os.path.isfile(sub_data)]) + 1
        else:
            os.mkdir(path)
            count = 1

        webcam = cv2.VideoCapture(0)

        while True:
            success, im = webcam.read()
            if not success:
                break

            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)
                face = gray[y:y + h, x:x + w]
                face_resize = cv2.resize(face, (130, 100))
                cv2.imwrite(os.path.join(path, f"{count}.png"), face_resize)
                count += 1

                if count == 101:
                    alert_message = "Registration completed!"
                    break

            cv2.imshow('Taking Samples', im)
            key = cv2.waitKey(10)
            if key == 27 or count == 101:
                cv2.destroyAllWindows()
                break

    return render_template('register.html', alert_message=alert_message)

if __name__ == '__main__':
    app.run(debug=True)
