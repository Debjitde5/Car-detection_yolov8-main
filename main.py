import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import*
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import api
from math import dist

model = YOLO('yolov8s.pt')

def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE :  
        colorsBGR = [x, y]
        print(colorsBGR)
        
cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', RGB)
path='video6.mp4'
cap=cv2.VideoCapture(path)
my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n") 
#print(class_list)
trackerc=Tracker()
trackerb=Tracker()
trackert=Tracker()
cy1=260
cy2=156
offset=6
distance=15
spd_lim=40
car_down=0
car_up=0
car_spd=0
bus_down=0
bus_up=0
bus_spd=0
truck_down=0
truck_up=0
truck_spd=0
a_speed_kh=0

def mail(c_up,c_dwn,c_spd,b_up,b_dwn,b_spd,t_up,t_dwn,t_spd):
    # Email configuration
    sender_email = "palshubho2020@gmail.com"
    sender_password = api.mailpasskey
    receiver_email = "shubhodippal01@gmail.com"
    subject = "Traffic Details"
    car = "Total number of car:"+str(c_up+c_dwn)+"\nUpwards Car:"+str(c_up)+"\nDownwards Car:"+str(c_dwn)+"\nOver Speeding car:"+str(c_spd)
    bus = "\nTotal number of bus:"+str(b_up+b_dwn)+"\nUpwards Car:"+str(b_up)+"\nDownwards Car:"+str(b_dwn)+"\nOver Speeding car:"+str(b_spd)
    truck = "\nTotal number of truck:"+str(t_up+t_dwn)+"\nUpwards Car:"+str(t_up)+"\nDownwards Car:"+str(t_dwn)+"\nOver Speeding car:"+str(t_spd)
    content = car+bus+truck
    # Create a MIME object
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    # Attach the concatenated string
    body = MIMEText(content)
    message.attach(body)
    # Connect to the SMTP server (in this case, Gmail's SMTP server)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        # Send the email
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.close()

def detect():
    count=0
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
        bbox_idb=trackerb.update(listb)
        bbox_idt=trackert.update(listt)
        #car
        for bbox in bbox_idc:
            x3,y3,x4,y4,id=bbox
            cx=int(x3+x4)//2
            cy=int(y3+y4)//2
            cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
            cv2.putText(frame,"car",(x3,y3),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1)
            #for car going up
            if cy1 < (cy + offset) and cy1 > (cy - offset):
                upcar[id] = time.time() #to get the current time when the veh touches line1
            if id in upcar:
                if cy2 < (cy + offset) and cy2 > (cy - offset):
                    #here time.time() is the current time when veh touches L2
                    elapsed_time = time.time() - upcar[id] #to get the time in the area 
                    if countercarup.count(id) == 0: #to resolve retative count
                        countercarup.append(id)
                        a_speed_ms = distance / elapsed_time
                        a_speed_kh = a_speed_ms * 3.6
                        cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                        if(a_speed_kh>spd_lim):
                            cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
                            cv2.putText(frame,("Overspeeding"),(cx-50,cy-50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,255),2)
                            countercar_ovrspeeding.append(id)
                        else:
                            cv2.rectangle(frame,(x3,y3),(x4,y4),(205,120,0),2)
                    #cv2.putText(frame,str(id),(cx,cy),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1)
                    cv2.putText(frame,str(int(a_speed_kh)) + 'Km/h',(x4, y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)      
            #car going down      
            if cy2 < (cy + offset) and cy2 > (cy - offset):
                downcar[id] = time.time()
            if id in downcar:
                if cy1 < (cy + offset) and cy1 > (cy - offset):
                    elapsed1_time = time.time() - downcar[id]
                    if countercardown.count(id) == 0:
                        countercardown.append(id)
                        a_speed_ms1 = distance / elapsed1_time
                        a_speed_kh1 = a_speed_ms1 * 3.6
                        cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                        if(a_speed_kh1>spd_lim):
                            cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
                            cv2.putText(frame,("Overspeeding"),(cx-50,cy-50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,255),3)
                            countercar_ovrspeeding.append(id)
                        else:
                            cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
                    #cv2.putText(frame,str(id),(cx,cy),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1) 
                    cv2.putText(frame,str(int(a_speed_kh1)) + 'Km/h',(x4, y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)
        #bus
        for bbox in bbox_idb:
            x3,y3,x4,y4,id=bbox
            cx=int(x3+x4)//2
            cy=int(y3+y4)//2
            cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
            cv2.putText(frame,"bus",(x3,y3),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1)
            #for bus going up
            if cy1 < (cy + offset) and cy1 > (cy - offset):
                upbus[id] = time.time() #to get the current time when the veh touches line1
            if id in upbus:
                if cy2 < (cy + offset) and cy2 > (cy - offset):
                    #here time.time() is the current time when veh touches L2
                    elapsed_time = time.time() - upbus[id] #to get the time in the area 
                    if counterbusup.count(id) == 0: #to resolve retative count
                        counterbusup.append(id)
                        a_speed_ms = distance / elapsed_time
                        a_speed_kh = a_speed_ms * 3.6
                        cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                        if(a_speed_kh>spd_lim):
                            cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
                            cv2.putText(frame,("Overspeeding"),(cx-50,cy-50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,255),2)
                            counterbus_ovrspeeding.append(id)
                        else:
                            cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
                    #cv2.putText(frame,str(id),(cx,cy),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1)
                    cv2.putText(frame,str(int(a_speed_kh)) + 'Km/h',(x4, y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)        
            #bus going down      
            if cy2 < (cy + offset) and cy2 > (cy - offset):
                downbus[id] = time.time()
            if id in downbus:
                if cy1 < (cy + offset) and cy1 > (cy - offset):
                    elapsed1_time = time.time() - downbus[id]
                    if counterbusdown.count(id) == 0:
                        counterbusdown.append(id)
                        a_speed_ms1 = distance / elapsed1_time
                        a_speed_kh1 = a_speed_ms1 * 3.6
                        cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                        if(a_speed_kh1>spd_lim):
                            cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
                            cv2.putText(frame,("Overspeeding"),(cx-50,cy-50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,255),3)
                            counterbus_ovrspeeding.append(id)
                        else:
                            cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
                    #cv2.putText(frame,str(id),(cx,cy),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1) 
                    cv2.putText(frame,str(int(a_speed_kh1)) + 'Km/h',(x4, y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)
        #truck
        for bbox in bbox_idt:
            x3,y3,x4,y4,id=bbox
            cx=int(x3+x4)//2
            cy=int(y3+y4)//2
            cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
            cv2.putText(frame,"truck",(x3,y3),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1)
            #for truck going up
            if cy1 < (cy + offset) and cy1 > (cy - offset):
                uptruck[id] = time.time() #to get the current time when the veh touches line1
            if id in uptruck:
                if cy2 < (cy + offset) and cy2 > (cy - offset):
                    #here time.time() is the current time when veh touches L2
                    elapsed_time = time.time() - uptruck[id] #to get the time in the area 
                    if countertruckup.count(id) == 0: #to resolve retative count
                        countertruckup.append(id)
                        a_speed_ms = distance / elapsed_time
                        a_speed_kh = a_speed_ms * 3.6
                        cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                        if(a_speed_kh>spd_lim):
                            cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
                            cv2.putText(frame,("Overspeeding"),(cx-50,cy-50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,255),2)
                            countertruck_ovrspeeding.append(id)
                        else:
                            cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
                    #cv2.putText(frame,str(id),(cx,cy),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1)
                    cv2.putText(frame,str(int(a_speed_kh)) + 'Km/h',(x4, y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)       
            #truck going down      
            if cy2 < (cy + offset) and cy2 > (cy - offset):
                downtruck[id] = time.time()
            if id in downtruck:
                if cy1 < (cy + offset) and cy1 > (cy - offset):
                    elapsed1_time = time.time() - downtruck[id]
                    if countertruckdown.count(id) == 0:
                        countertruckdown.append(id)
                        a_speed_ms1 = distance / elapsed1_time
                        a_speed_kh1 = a_speed_ms1 * 3.6
                        cv2.circle(frame,(cx,cy),4,(0,0,255),-1)
                        if(a_speed_kh1>spd_lim):
                            cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
                            cv2.putText(frame,("Overspeeding"),(cx-50,cy-50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,255),3)
                            countertruck_ovrspeeding.append(id)
                        else:
                            cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
                    #cv2.putText(frame,str(id),(cx,cy),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,255,255),1) 
                    cv2.putText(frame,str(int(a_speed_kh1)) + 'Km/h',(x4, y4),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,255,255),2)                                
            
        cv2.line(frame,(100,cy1),(800,cy1),(255,0,0),3)
        cv2.line(frame,(167,cy2),(680,cy2),(255,0,0),3)
        #car
        #going down
        car_down = (len(countercardown))
        cv2.putText(frame,('Car Going down:') + str(car_down),(745,40),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,255,255),2)
        #For going up
        car_up = (len(countercarup))
        cv2.putText(frame,('Car Going up :') + str(car_up),(745,70),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,255,255),2)
        #over speeding
        car_spd =len(countercar_ovrspeeding)
        cv2.putText(frame,'Car Overspeeding:' + str(car_spd),(10,40),cv2.FONT_HERSHEY_COMPLEX,0.7,(0,0,255),2)
        #bus
        #going down
        bus_down = (len(counterbusdown))
        cv2.putText(frame,('Bus Going down:') + str(bus_down),(745,100),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,255,255),2)
        #For going up
        bus_up = (len(counterbusup))
        cv2.putText(frame,('Bus Going up:') + str(bus_up),(745,130),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,255,255),2)
        #over speeding
        bus_spd =len(counterbus_ovrspeeding)
        cv2.putText(frame,'Bus Overspeeding:' + str(bus_spd),(10,65),cv2.FONT_HERSHEY_COMPLEX,0.7,(0,0,255),2)
        #truck
        #going down
        truck_down = (len(countertruckdown))
        cv2.putText(frame,('Truck Going down:') + str(truck_down),(745,160),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,255,255),2)
        #For going up
        truck_up = (len(countertruckup))
        cv2.putText(frame,('Truck Going up:') + str(truck_up),(745,190),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,255,255),2)
        #overspeeding
        truck_spd =len(countertruck_ovrspeeding)
        cv2.putText(frame,'Truck Overspeeding:' + str(truck_spd),(10,90),cv2.FONT_HERSHEY_COMPLEX,0.7,(0,0,255),2)

        cv2.imshow("RGB", frame)
        cv2.waitKey(1)#&0xFF==27:
            #break
        if path==0:
            #live footage
            start_time = time.time()
            end_time = time.time()
            t_time = (end_time - start_time)/60
            if elapsed_time == 60:
                mail(c_up=car_up,c_dwn=car_down,c_spd=car_spd,b_up=bus_up,b_dwn=bus_down,b_spd=bus_spd,t_up=truck_up,t_dwn=truck_down,t_spd=truck_spd)
                start_time=0
                end_time=0
                t_time=0

if __name__ == "__main__":
    detect()
    mail(c_up=car_up,c_dwn=car_down,c_spd=car_spd,b_up=bus_up,b_dwn=bus_down,b_spd=bus_spd,t_up=truck_up,t_dwn=truck_down,t_spd=truck_spd)

    cap.release()
    cv2.destroyAllWindows()