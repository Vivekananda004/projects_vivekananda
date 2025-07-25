from tkinter import messagebox
from tkinter import *
from tkinter import simpledialog
import tkinter
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
import numpy as np 
import matplotlib.pyplot as plt
from ultralytics import YOLO
import cv2

import imutils
from scipy.spatial import distance as dist
from imutils import perspective

global filename, model
labels = ['Pothole']
CONFIDENCE_THRESHOLD = 0.3
GREEN = (0, 255, 0)

main = tkinter.Tk()
main.title("Pothole Detection & Dimension Estimation") #designing main screen
main.geometry("1300x1200")

 
#fucntion to load YoloV8 model
def loadModel():
    global filename, model
    text.delete('1.0', END)
    model = YOLO("model/best.pt")
    text.insert(END,"Pothole Detection Model Loaded")

def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)    

def estimateDimension(x1, y1, w1, h1, image):
    w, h, c = image.shape
    temp = np.zeros((w, h, c))
    cv2.rectangle(temp, (x1, y1), (w1, h1), (255, 255, 255), 4)
    cv2.imwrite("aa.jpg", temp)
    img = cv2.imread("aa.jpg")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    corners = cv2.goodFeaturesToTrack(gray, 7, 0.01, 10)
    corners = np.int0(corners)
    points = []  
    for i in corners:
        x, y = i.ravel()
        cv2.circle(img, (x, y), 3, 255, -1)
        points.append([[x,y]])
    points = np.asarray(points)

    orig = image.copy()
    box = cv2.minAreaRect(points)
    (x, y), (width, height), angle = box
    print(str(x)+" == "+str(y)+" "+str(width)+" "+str(height))
    box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
    box = np.array(box, dtype="int")
    box = perspective.order_points(box)
    cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)
    for (x, y) in box:
        cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)
    pixelsPerMetric = None
    (tl, tr, br, bl) = box
    print(box)
    (tltrX, tltrY) = midpoint(tl, tr)
    (blbrX, blbrY) = midpoint(bl, br)
    # compute the midpoint between the top-left and top-right points,
    # followed by the midpoint between the top-righ and bottom-right
    (tlblX, tlblY) = midpoint(tl, bl)
    (trbrX, trbrY) = midpoint(tr, br)
    # draw the midpoints on the image
    cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
    cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
    cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
    cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)
    # draw lines between the midpoints
    cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)), (255, 0, 255), 2)
    cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)), (255, 0, 255), 2)
    # compute the Euclidean distance between the midpoints
    dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
    dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
    # if the pixels per metric has not been initialized, then
    #compute it as the ratio of pixels to supplied metric
    # (in this case, inches)
    if pixelsPerMetric is None:
        pixelsPerMetric = dB / 3.5
    # compute the size of the object
    dimA = dA / pixelsPerMetric
    dimB = dB / pixelsPerMetric
    print(str(dimA)+" == "+str(dimB)+" "+str(pixelsPerMetric)+" "+str(dB)+" "+str(dA)+" "+str(width)+" "+str(height))
    # draw the object sizes on the image
    cv2.putText(orig, str(round(dimA,2))+"in", (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)
    cv2.putText(orig, str(width)+" width", (int(tltrX - 15), int(tltrY - 30)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)
    cv2.putText(orig, str(round(dimB,2))+"in ", (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)
    cv2.putText(orig, str(height)+" height", (int(trbrX + 10), int(trbrY+30)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)
    text.insert(END,str(round(dimA,2))+"inches\n")
    text.insert(END,str(width)+" width\n")
    text.insert(END,str(round(dimB,2))+"inches\n")
    text.insert(END,str(height)+" height\n")
    text.update_idletasks()
    return orig
    
    
def imageDetection():
    global model
    text.delete('1.0', END)
    filename = filedialog.askopenfilename(initialdir="testImages") #upload dataset file
    text.insert(END,filename+" loaded\n\n")
    frame = cv2.imread(filename)
    #frame = cv2.resize(frame, (700, 600))
    detections = model(frame)[0]
    # loop over the detections
    for data in detections.boxes.data.tolist():
        # extract the confidence (i.e., probability) associated with the detection
        confidence = data[4]
        cls_id = data[5]
        
        # filter out weak detections by ensuring the 
        # confidence is greater than the minimum confidence
        if float(confidence) < CONFIDENCE_THRESHOLD:
            continue
        # if the confidence is greater than the minimum confidence,
        # draw the bounding box on the frame
        xmin, ymin, xmax, ymax = int(data[0]), int(data[1]), int(data[2]), int(data[3])
        cv2.rectangle(frame, (xmin, ymin) , (xmax, ymax), GREEN, 2)
        frame = estimateDimension(xmin, ymin, xmax, ymax, frame)
        #cv2.putText(frame, labels[int(cls_id)]+" "+str(confidence), (xmin, ymin-20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
    cv2.imshow("Pothole Detection & Estimation from Image", frame)
    cv2.waitKey(0)


font = ('times', 16, 'bold')
title = Label(main, text='Pothole Detection & Dimension Estimation')
title.config(bg='greenyellow', fg='dodger blue')  
title.config(font=font)           
title.config(height=3, width=120)       
title.place(x=0,y=5)

font1 = ('times', 12, 'bold')
text=Text(main,height=20,width=150)
scroll=Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=50,y=120)
text.config(font=font1)


font1 = ('times', 13, 'bold')
loadButton = Button(main, text="Generate & Load Pothole Detection Model", command=loadModel)
loadButton.place(x=50,y=550)
loadButton.config(font=font1)  

imageButton = Button(main, text="Upload Image & Estimate Dimension", command=imageDetection)
imageButton.place(x=400,y=550)
imageButton.config(font=font1) 


main.config(bg='LightSkyBlue')
main.mainloop()
