import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import*
import time
from math import dist
model = YOLO('yolov8s.pt')

def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE :  
        colorsBGR = [x, y]
        print(colorsBGR)
        
cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', RGB)

cap=cv2.VideoCapture('video6.mp4')

my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n") 
#print(class_list)
count=0
tracker=Tracker()
cy1=260
cy2=156
offset=6
vh_down = {}
counter = [] 
counter1 = []
vh_up = {}
vh_overspeeding = []
a_speed_kh=0
while True:    
    ret,frame = cap.read()
    if not ret:
        break
    count += 1
    if count % 3 != 0:
        continue
    frame=cv2.resize(frame,(1020,500))

    results=model.predict(frame)
 #   print(results)
    a=results[0].boxes.data
    px=pd.DataFrame(a).astype("float")
#    print(px)
    list=[]        
    
    for index,row in px.iterrows():
#        print(row)
        x1=int(row[0])
        y1=int(row[1])
        x2=int(row[2])
        y2=int(row[3])
        d=int(row[5])
        c=class_list[d]
        if 'car' or 'truck' in c:
            list.append([x1,y1,x2,y2])
    bbox_id=tracker.update(list)
    
    for bbox in bbox_id:
        x3,y3,x4,y4,id=bbox
        cx=int(x3+x4)//2
        cy=int(y3+y4)//2

        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)

        #for going up
        if cy1 < (cy + offset) and cy1 > (cy - offset):
            vh_down[id] = time.time() #to get the current time when the veh touches line1
        if id in vh_down:
            if cy2 < (cy + offset) and cy2 > (cy - offset):
                #here time.time() is the current time when veh touches L2
                elapsed_time = time.time() - vh_down[id] #to get the time in the area 
                if counter.count(id) == 0: #to resolve retative count
                    counter.append(id)
                    distance = 10
                    a_speed_ms = distance / elapsed_time
                    a_speed_kh = a_speed_ms * 3.6
                    cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                    if(a_speed_kh>40):
                        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
                        cv2.putText(frame,("Overspeeding"),(cx-50,cy-50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,255),2)
                        vh_overspeeding.append(id)
                    else:
                        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
                cv2.putText(frame,str(id),(cx,cy),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1)
                cv2.putText(frame,str(int(a_speed_kh)) + 'Km/h',(x4, y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)
                
        #going down      
        if cy2 < (cy + offset) and cy2 > (cy - offset):
            vh_up[id] = time.time()
        if id in vh_up:
            if cy1 < (cy + offset) and cy1 > (cy - offset):
                elapsed1_time = time.time() - vh_up[id]
                if counter1.count(id) == 0:
                    counter1.append(id)
                    distance1 = 10 #metersl
                    a_speed_ms1 = distance1 / elapsed1_time
                    a_speed_kh1 = a_speed_ms1 * 3.6
                    cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                    if(a_speed_kh1>40):
                        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
                        cv2.putText(frame,("Overspeeding"),(cx-50,cy-50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,255),3)
                        vh_overspeeding.append(id)
                    else:
                        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
                cv2.putText(frame,str(id),(cx,cy),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1) 
                cv2.putText(frame,str(int(a_speed_kh1)) + 'Km/h',(x4, y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)
                    
    cv2.line(frame,(100,cy1),(800,cy1),(255,0,0),3)
    cv2.line(frame,(167,cy2),(680,cy2),(255,0,0),3)
    d = (len(counter))
    cv2.putText(frame,('Going up:') + str(d),(60,40),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,155,205),2)

    #For going up
    u = (len(counter1))
    cv2.putText(frame,('Going down:') + str(u),(60,130),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)

    os =len(vh_overspeeding)
    cv2.putText(frame,'Overspeeding:' + str(os),(380,40),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)

    print(counter)
    cv2.imshow("RGB", frame)
    if cv2.waitKey(1)&0xFF==27:
        break
cap.release()
cv2.destroyAllWindows()