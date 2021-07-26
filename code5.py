import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2
import time
import serial
ser = serial.Serial('/dev/ttyS0',115200)
ser.flushInput()


cap = cv2.VideoCapture(0)

# cap.set(3,1280)
# cap.set(4,720)

tpl = cv2.imread('/home/dji/Desktop/robot.jpg')
th, tw = tpl.shape[:2]
set = []
second_set1 = []
second_set2 = []

while True:
    f = 0
    set.clear()
    second_set1.clear()
    second_set2.clear()
    ret,frame = cap.read()
    frame = cv2.resize(frame,(320,180))

    hist = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    hist = cv2.equalizeHist(hist)

    canny = cv2.Canny(hist,200,220)
    cv2.imshow('canny', canny)

    # canny2 = cv2.Canny(frame,150,200)
    # cv2.imshow('canny2',canny2)

    contours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for i in range(0, len(contours)):
        epsilon = 0.05 * cv2.arcLength(contours[i], True)
        approx = cv2.approxPolyDP(contours[i], epsilon, True)
        # 分析几何形状
        corners = len(approx)
        if corners > 4 and corners <10 :
            x, y, w, h = cv2.boundingRect(contours[i])
            if w / h >1.5:
                continue
            if h / w >1.5:
                continue
            if h < 10 or h > 60:
                continue
            if w < 10 or w > 60:
                continue
            #print(w/h,h/w,h,w)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255, 0, 0), 5)

            set.append(cv2.boundingRect(contours[i]))
    set.sort()
    for i in range(len(set)-1):
        for j in range(i,len(set)):
            l_x = set[i][0]
            l_y = set[i][1]
            l_w = set[i][2]
            l_h = set[i][3]
            r_x = set[j][0]
            r_y = set[j][1]
            r_w = set[j][2]
            r_h = set[j][3]
            width = (r_w+l_w)/2
            height = (r_h+l_h)/2
            if abs(l_x - r_x) > 3.5 * width \
                    and abs(l_x-r_x) < 5.5 * width \
                    and abs(l_y-r_y) < 0.5 * height:
                cv2.circle(frame, (l_x, l_y), 3, (0, 255, 0), 3)

                # cv2.rectangle(frame,(l_x,l_y),(r_x+r_w,r_y+r_h+int(height)),(153,153,0),5)

                roi = hist[l_y:r_y+r_h+int(height),l_x:r_x+r_w]
                roi = cv2.resize(roi,(82,46))

                roi = cv2.cvtColor(roi,cv2.COLOR_GRAY2BGR)
                result = cv2.matchTemplate(roi, tpl, cv2.TM_CCOEFF_NORMED)
                #print(cv2.minMaxLoc(result)[1])
                if cv2.minMaxLoc(result)[1]>0.5:
                    cv2.imshow('roi',roi)
                    cv2.rectangle(frame, (l_x, l_y), (r_x + r_w, r_y + r_h + int(height)), (153, 153, 0), 5)
                    centre_x = int((l_x+r_x+r_w)/2)
                    print(centre_x-160)
                    dx = centre_x-160
                    f = 1
                    ser.write(f'{dx},'.encode('utf-8'))
                    time.sleep(0.001)
            # else:
            #     dx = 0
            #     ser.write(f'{dx},'.encode('utf-8'))
            #     print('None')
            #     time.sleep(0.001)

                second_set1.append(set[i])
                second_set2.append(set[j])

    # if len(second_set2):
    #     for i in range(0,len(second_set1)):
    #         cv2.rectangle(frame, (second_set1[i][0],second_set1[i][1]),
    #                       (second_set2[i][0] + second_set2[i][2], second_set2[i][1] + second_set2[i][3]), (153, 153, 0), 5)

    if f == 0:
        dx = 0
        ser.write(f'{dx},'.encode('utf-8'))
        print('None')
        time.sleep(0.001)
    cv2.imshow('frame',frame)
    cv2.imshow('hist', hist)
    k = cv2.waitKey(1)
    if k == 27:
        break
cap.release()
cv2.destroyAllWindows()
