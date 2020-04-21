"""
This program will detect object.
The program uses YOLO weight, config and to detect object 
"""

import cv2
import numpy as np
import time

# load Yolo and COCO
net = cv2.dnn.readNet("Weights/yolov3-tiny.weights", "config/yolov3-tiny.cfg")
classes = []
with open("Dataset/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

# Assigning basic variables 
starting_time = time.time()
CameraFeed = None
VideoPath = "Videos/DrivingVideo.mp4"
frame_id = 0
font = cv2.FONT_HERSHEY_PLAIN

# Loading video
#cap = cv2.VideoCapture(CameraFeed) #<---- For webcam 
cap = cv2.VideoCapture(VideoPath) #<---- For mp4 video

# While loop = workflow of program 
while True:
    _, frame = cap.read()
    frame_id += 1
    height, width, channels = frame.shape

    # Creates 4-dimensional blob from image.
    blob = cv2.dnn.blobFromImage(frame, 0.03092, (316, 316), (0,0,0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Showing informations on the screen
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            # The confidence for objects
            if confidence > 0.5:
                # Obejct detected 
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                    
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    
    # Performs non maximum suppression given boxes and corresponding scores.
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.5)
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = confidences[i]
            color = colors[class_ids[i]] 
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            confidence_percent = round(confidence * 100)
            cv2.putText(frame, label + " " + str(round(confidence_percent, 2)) + "%", (x, y + 20), font, 2, (0,0,0), 2)
            print(label + ": " + str(confidence_percent) + " Procent")
    
    # Calculating execution timne
    execution_time = time.time() - starting_time
    # Calculating FPS
    fps = frame_id / execution_time
    # Drawing FPS to screen
    cv2.putText(frame, "FPS: " + str(round(fps, 2)), (10, 50), font, 4, (0, 0, 0), 3)
    # Showing object detection video
    cv2.imshow("Video", frame)
    # Break program if ESC(27) is pressed
    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release() 
cv2.destroyAllWindows()