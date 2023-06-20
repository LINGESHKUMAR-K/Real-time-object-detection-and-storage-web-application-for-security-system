import math
import cv2
import mysql.connector

def detection(image, detector):

    imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    result = detector(imgRGB)    

    return result

def HsvToBgr(h, s, v):

    i = math.floor(h*6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f*s)
    t = v * (1 - (1 - f)*s)

    if i % 6 == 0:r, g, b = v, t, p
    elif i % 6 == 1:r, g, b = q, v, p
    elif i % 6 == 2:r, g, b = p, v, t
    elif i % 6 == 3:r, g, b = p, q, v
    elif i % 6 == 4:r, g, b = t, p, v
    else:r, g, b = v, p, q

    return [int(b*255), int(g*255), int(r*255)]

def draw_anchor_box(image, detection_object, thickness_=2):

    new_img = image

    if detection_object:
        if len(detection_object.pred[0]) > 0:
            for i in range(len(detection_object.pred[0])):
                
                x1 = int(detection_object.pred[0][i][0])
                y1 = int(detection_object.pred[0][i][1])
                x2 = int(detection_object.pred[0][i][2])
                y2 = int(detection_object.pred[0][i][3])
                conf = detection_object.pred[0][i][-2]
                classe = detection_object.names[int(detection_object.pred[0][i][-1])]

                hue = 180 * int(detection_object.pred[0][i][-1]) / len(detection_object.names)
                color = HsvToBgr(hue, 1, 1)

                cv2.rectangle(new_img, (x1, y1), (x2, y2), color, thickness_)

                cv2.putText(new_img,f"{classe} - {conf:.2f}",(x1, y1-10),cv2.FONT_HERSHEY_PLAIN,2,color,2)
                
                store_detected_objects([(classe,x1,y1,x2,y2)])

    return new_img

def store_detected_objects(detected_objects):
    
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="6234488lINGESH",
        database="od"
    )

    cursor = connection.cursor()

    for obj in detected_objects:
        label = obj[0]
        x1 = obj[1]
        y1 = obj[2]
        x2 = obj[3]
        y2 = obj[4]

        query = "INSERT INTO detected_objects (label, x1, y1, x2, y2) VALUES (%s, %s, %s, %s, %s)"
        values = (label, x1, y1, x2, y2)

        cursor.execute(query, values)

    
    connection.commit()

 
    cursor.close()
    connection.close()
   