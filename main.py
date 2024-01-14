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
trackerc=Tracker()
trackerb=Tracker()
trackert=Tracker()
cy1=260
cy2=156
offset=6
#car
upcar = {}
downcar={}
countercarup= [] 
countercardown = []
countercar_ovrspeeding = []
#bus
upbus = {}
downbus={}
counterbusup= [] 
counterbusdown = []
counterbus_ovrspeeding = []
#truck
uptruck = {}
downtruck={}
countertruckup= [] 
countertruckdown = []
countertruck_ovrspeeding = []
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
    listc=[]
    listb=[]
    listt=[]        
    
    for index,row in px.iterrows():
#        print(row)
        x1=int(row[0])
        y1=int(row[1])
        x2=int(row[2])
        y2=int(row[3])
        d=int(row[5])
        c=class_list[d]
        if 'car' in c:
            listc.append([x1,y1,x2,y2])
        elif 'bus' in c:
            listb.append([x1,y1,x2,y2])
        elif 'truck' in c:
            listt.append([x1,y1,x2,y2])
                    
    bbox_idc=trackerc.update(listc)

    for bbox in bbox_idc:
        x3,y3,x4,y4,id=bbox
        cx=int(x3+x4)//2
        cy=int(y3+y4)//2

        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)

        #for car going up
        if cy1 < (cy + offset) and cy1 > (cy - offset):
            upcar[id] = time.time() #to get the current time when the veh touches line1
        if id in upcar:
            if cy2 < (cy + offset) and cy2 > (cy - offset):
                #here time.time() is the current time when veh touches L2
                elapsed_time = time.time() - upcar[id] #to get the time in the area 
                if countercarup.count(id) == 0: #to resolve retative count
                    countercarup.append(id)
                    distance = 10
                    a_speed_ms = distance / elapsed_time
                    a_speed_kh = a_speed_ms * 3.6
                    cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                    if(a_speed_kh>40):
                        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
                        cv2.putText(frame,("Overspeeding"),(cx-50,cy-50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,255),2)
                        countercar_ovrspeeding.append(id)
                    else:
                        cv2.rectangle(frame,(x3,y3),(x4,y4),(205,120,0),2)
                cv2.putText(frame,str(id),(cx,cy),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1)
                cv2.putText(frame,str(int(a_speed_kh)) + 'Km/h',(x4, y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)
                
        #car going down      
        if cy2 < (cy + offset) and cy2 > (cy - offset):
            downcar[id] = time.time()
        if id in downcar:
            if cy1 < (cy + offset) and cy1 > (cy - offset):
                elapsed1_time = time.time() - downcar[id]
                if countercardown.count(id) == 0:
                    countercardown.append(id)
                    distance1 = 10 #metersl
                    a_speed_ms1 = distance1 / elapsed1_time
                    a_speed_kh1 = a_speed_ms1 * 3.6
                    cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                    if(a_speed_kh1>40):
                        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
                        cv2.putText(frame,("Overspeeding"),(cx-50,cy-50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,255),3)
                        countercar_ovrspeeding.append(id)
                    else:
                        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
                cv2.putText(frame,str(id),(cx,cy),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1) 
                cv2.putText(frame,str(int(a_speed_kh1)) + 'Km/h',(x4, y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)

    bbox_idb=trackerb.update(listb)
    bbox_idt=trackert.update(listt)
    
    
        #for bus going up
        if cy1 < (cy + offset) and cy1 > (cy - offset):
            upbus[id] = time.time() #to get the current time when the veh touches line1
        if id in upbus:
            if cy2 < (cy + offset) and cy2 > (cy - offset):
                #here time.time() is the current time when veh touches L2
                elapsed_time = time.time() - upbus[id] #to get the time in the area 
                if counterbusup.count(id) == 0: #to resolve retative count
                    counterbusup.append(id)
                    distance = 10
                    a_speed_ms = distance / elapsed_time
                    a_speed_kh = a_speed_ms * 3.6
                    cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                    if(a_speed_kh>40):
                        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
                        cv2.putText(frame,("Overspeeding"),(cx-50,cy-50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,255),2)
                        counterbus_ovrspeeding.append(id)
                    else:
                        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
                cv2.putText(frame,str(id),(cx,cy),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1)
                cv2.putText(frame,str(int(a_speed_kh)) + 'Km/h',(x4, y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)
                
        #bus going down      
        if cy2 < (cy + offset) and cy2 > (cy - offset):
            downbus[id] = time.time()
        if id in downbus:
            if cy1 < (cy + offset) and cy1 > (cy - offset):
                elapsed1_time = time.time() - downbus[id]
                if counterbusdown.count(id) == 0:
                    counterbusdown.append(id)
                    distance1 = 10 #metersl
                    a_speed_ms1 = distance1 / elapsed1_time
                    a_speed_kh1 = a_speed_ms1 * 3.6
                    cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                    if(a_speed_kh1>40):
                        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
                        cv2.putText(frame,("Overspeeding"),(cx-50,cy-50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,255),3)
                        counterbus_ovrspeeding.append(id)
                    else:
                        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
                cv2.putText(frame,str(id),(cx,cy),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1) 
                cv2.putText(frame,str(int(a_speed_kh1)) + 'Km/h',(x4, y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)

        #for truck going up
        if cy1 < (cy + offset) and cy1 > (cy - offset):
            uptruck[id] = time.time() #to get the current time when the veh touches line1
        if id in uptruck:
            if cy2 < (cy + offset) and cy2 > (cy - offset):
                #here time.time() is the current time when veh touches L2
                elapsed_time = time.time() - uptruck[id] #to get the time in the area 
                if countertruckup.count(id) == 0: #to resolve retative count
                    countertruckup.append(id)
                    distance = 10
                    a_speed_ms = distance / elapsed_time
                    a_speed_kh = a_speed_ms * 3.6
                    cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                    if(a_speed_kh>40):
                        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
                        cv2.putText(frame,("Overspeeding"),(cx-50,cy-50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,255),2)
                        countertruck_ovrspeeding.append(id)
                    else:
                        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
                cv2.putText(frame,str(id),(cx,cy),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1)
                cv2.putText(frame,str(int(a_speed_kh)) + 'Km/h',(x4, y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)
                
        #truck going down      
        if cy2 < (cy + offset) and cy2 > (cy - offset):
            downtruck[id] = time.time()
        if id in downtruck:
            if cy1 < (cy + offset) and cy1 > (cy - offset):
                elapsed1_time = time.time() - downtruck[id]
                if countertruckdown.count(id) == 0:
                    countertruckdown.append(id)
                    distance1 = 10 #metersl
                    a_speed_ms1 = distance1 / elapsed1_time
                    a_speed_kh1 = a_speed_ms1 * 3.6
                    cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                    if(a_speed_kh1>40):
                        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
                        cv2.putText(frame,("Overspeeding"),(cx-50,cy-50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,255),3)
                        countertruck_ovrspeeding.append(id)
                    else:
                        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
                cv2.putText(frame,str(id),(cx,cy),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1) 
                cv2.putText(frame,str(int(a_speed_kh1)) + 'Km/h',(x4, y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)                                
               
    cv2.line(frame,(100,cy1),(800,cy1),(255,0,0),3)
    cv2.line(frame,(167,cy2),(680,cy2),(255,0,0),3)
    d = (len(countercardown))
    cv2.putText(frame,('Going down:') + str(d),(60,40),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)

    #For going up
    u = (len(countercarup))
    cv2.putText(frame,('Going up:') + str(u),(60,130),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)

    os =len(countercar_ovrspeeding)
    cv2.putText(frame,'Overspeeding:' + str(os),(380,40),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)


    print(countercardown)

    d = (len(counterbusdown))
    cv2.putText(frame,('Going down:') + str(d),(60,40),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)

    #For going up
    u = (len(counterbusup))
    cv2.putText(frame,('Going up:') + str(u),(60,130),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)

    os =len(counterbus_ovrspeeding)
    cv2.putText(frame,'Overspeeding:' + str(os),(380,40),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)


    print(counterbusdown)
    
    d = (len(countertruckdown))
    cv2.putText(frame,('Going down:') + str(d),(60,40),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)

    #For going up
    u = (len(countertruckup))
    cv2.putText(frame,('Going up:') + str(u),(60,130),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)

    os =len(countertruck_ovrspeeding)
    cv2.putText(frame,'Overspeeding:' + str(os),(380,40),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),2)


    print(countertruckdown)

    cv2.imshow("RGB", frame)
    if cv2.waitKey(1)&0xFF==27:
        break
cap.release()
cv2.destroyAllWindows()

