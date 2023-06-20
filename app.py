from flask import Flask, render_template, request, Response, redirect
from flask_mysqldb import MySQL
import cv2
import time
import torch
import functions as fns
import mysql.connector

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'     # MySQL host
app.config['MYSQL_USER'] = 'root' # MySQL username
app.config['MYSQL_PASSWORD'] = 'password' # MySQL password
app.config['MYSQL_DB'] = 'od'   # MySQL database name

mysql = MySQL(app)

def generate_frames():
    video_cap = cv2.VideoCapture(0)
    model_detection = torch.hub.load('ultralytics/yolov5', 'yolov5s')
    
    while True:
        success, frame = video_cap.read()

        if not success:
            break

        new_frame = fns.draw_anchor_box(frame, fct.detection(frame, model_detection))

        
        ret, buffer = cv2.imencode('.jpg', new_frame)
        frame_data = buffer.tobytes()

        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')

        
        time.sleep(0.1)

    video_cap.release()
    
    return redirect('/new-endpoint')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/new-endpoint')
def new_endpoint():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT label FROM detected_objects")
    objects = cursor.fetchall()
    cursor.close()
    return render_template('index.html', objects=objects)

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/search_objects', methods=['POST'])
def search_objects():
    search_label = request.form.get('search_label')
    search_date = request.form.get('search_date')
    
    cursor = mysql.connection.cursor()
    
    if search_label and search_date:
        query = "SELECT * FROM detected_objects WHERE label = %s AND DATE(timestamp) = %s"
        values = (search_label, search_date)
        cursor.execute(query, values)
    elif search_label:
        query = "SELECT * FROM detected_objects WHERE label = %s"
        values = (search_label,)
        cursor.execute(query, values)
    elif search_date:
        query = "SELECT * FROM detected_objects WHERE DATE(timestamp) = %s"
        values = (search_date,)
        cursor.execute(query, values)
    else:
        query = "SELECT * FROM detected_objects"
        cursor.execute(query)
    
    objects = cursor.fetchall()
    
    cursor.close()
    
    return render_template('search.html', objects=objects)


if __name__ == '__main__':
    app.run()