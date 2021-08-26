import cv2,time,serial
import numpy as np
#100 100 130
#ser = serial.Serial("/dev/ttyUSB0", 9600)
ser = serial.Serial("COM20", 9600)
ser.flushInput()

cap = cv2.VideoCapture(0)
#print(cap.get(10))
cap.set(10, 50 )      #亮度
#print(cap.get(11))
cap.set(11, 100)     #对比度
#print(cap.get(12))
cap.set(12, 100)     #饱和度
#print(cap.get(13))
cap.set(13, 0)     #色调
lower_blue  = np.array([100,0  ,0  ])
upper_blue  = np.array([255,200,50])

lower_red   = np.array([0  ,0  ,100])
upper_red   = np.array([50,50,255])

#lower_green = np.array([50 ,50 ,0  ])
#upper_green = np.array([100,120,20 ])

lower_green = np.array([10 ,30 ,0  ])
upper_green = np.array([200,255,10 ])

lower = np.array([100 , 100 , 100])
upper = np.array([255, 255, 255])

lanqiu_lower = np.array([3 , 50 , 20])
lanqiu_upper = np.array([50, 240, 120])
    # 15 220 70

zuqiu_lower = np.array([20 , 10 , 30])
zuqiu_upper = np.array([120, 70, 120])
    # 100 23 143
'''
paiqiu_lower1 = np.array([0 , 20 , 150])
paiqiu_upper1 = np.array([30, 150, 255])

paiqiu_lower2 = np.array([0 , 200 , 130])
paiqiu_upper2 = np.array([30, 255, 230])

paiqiu_lower3 = np.array([80 , 0 , 150])
paiqiu_upper3 = np.array([150, 40, 255])
    # 20 255 150
'''

paiqiu_lower1 = np.array([0 , 200 , 100])
paiqiu_upper1 = np.array([30, 255, 200])

paiqiu_lower2 = np.array([80 , 100 , 50])
paiqiu_upper2 = np.array([120, 200, 100])

paiqiu_lower3 = np.array([80 , 160 , 20])
paiqiu_upper3 = np.array([150, 200, 70])


kernel_15 = np.ones((15,15),np.uint8)#15x15的卷积核
kernel_50 = np.ones((50,50),np.uint8)#50x50的卷积核
kernel_30 = np.ones((30,30),np.uint8)#30x30的卷积核
kernel_15 = np.ones((15,15),np.uint8)#15x15的卷积核
kernel_10 = np.ones((10,10),np.uint8)#10x10的卷积核
kernel_5  = np.ones(( 5, 5),np.uint8)# 5x 5的卷积核

template_1 = cv2.imread("rectangle.png" ,0)
template_2 = cv2.imread("star.png"      ,0)
template_3 = cv2.imread("circle.png"    ,0)

def length_math(D,S):
    if(S == "R"):
        return D/1.414
    elif(S == "S"):
        return D/2*1.73205
    elif(S == "C"):
        return D*0.8

def xuanzhuan(img,tangle):
    #cv2.imshow("input", img)
    (h, w) = img.shape[:2] #10
    center = (w // 2, h // 2) #11
    M = cv2.getRotationMatrix2D(center, tangle, 1.0) #12
    rotated = cv2.warpAffine(img, M, (w, h)) #13
    #cv2.imshow("output", rotated) #14
    return rotated

def match(frame,template):
    if frame.shape[0]<template.shape[0] or frame.shape[1]<template.shape[1]:
        return 1
    res = cv2.matchTemplate(frame,template,cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    #top_left = min_loc
    #print("min_val",min_val)
    return min_val


def turn_match(frame,template,tangle,number):
    target = match(frame,template)
    for i in range(number):
        template_turn = xuanzhuan(template,tangle*(i+1))
        t = match(frame,template_turn)
        if t < target:
            target = t
    for i in range(number):
        template_turn = xuanzhuan(template,-tangle*(i+1))
        t = match(frame,template_turn)
        if t < target:
            target = t
    return target

def judge(frame,xishu):
    #template_1 = cv2.imread("rectangle.png"     ,0)
    #print("template_1",template_1.shape[0:2])
    #template_2 = cv2.imread("star.png" ,0)
    #print("template_2",template_2.shape[0:2])
    #template_3 = cv2.imread("circle.png"    ,0)


    #cv2.imshow("frame_judge",frame)
    #print("circle")
    number_1 = turn_match(frame,template_1,6,3)
    #print("rectangle",number_1)
    #print("circle_big")
    number_2 = turn_match(frame,template_2,6,3)
    #print("star",number_2)
    number_3 = turn_match(frame,template_3,6,3)
    #print("circle",number_3)
    #print("liubian_big")

    if number_1 < number_2:
        number = number_1
        target = "R"
    else:
        number = number_2
        target = "S"
    if number_3 < number:
        number = number_3
        target = "C"
    #print("number",number)
    if number < xishu:
        return target,number
    else:
        return "ER",number

data     = [[0] * 2 for i in range(1000)]
data_num = 0
#点击获取目标HSV值
def getposBGR(event, x, y, flags, param):
    if event==cv2.EVENT_LBUTTONDOWN:
        print("BGR is", frame[y, x])
#cv2.setMouseCallback("img", getposBGR)


def find_blue(frame):
    img1  = cv2.inRange(frame.copy(), lower_blue, upper_blue)
    cv2.imwrite('blue_out2.png'  , img1 )
    erosion  = cv2.erode (img1,kernel_5,iterations = 1)
    dilation = cv2.dilate(erosion  ,kernel_5,iterations = 1)
    cv2.imwrite('blue_out1.png'  , dilation )
    canny = cv2.Canny(dilation, 50, 150)
    #cv2.imshow("blue_canny", canny)
    cv2.imwrite('blue_canny.png'  , canny )
    _, cnts, _ = cv2.findContours(canny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    length = len(cnts)

    if length >0:
        for i in range(length):
            #c = sorted(cnts, key=cv2.contourArea, reverse=True)[i]
            x, y, w, h  = cv2.boundingRect(cnts[i]) # 得到最小外接矩形的（中心(x,y), (宽,高), 旋转角度）
            
            if w*h > 1500:
                (x1, y1), radius = cv2.minEnclosingCircle(cnts[i])
                a1 = max(x-40,2)
                a2 = min(x+w+40,638)
                b1 = max(y-40,2)
                b2 = min(y+h+40,478)
                #print(w,h)
                #print(a1,a2,b1,b2)
                T=frame.copy()
                T=np.zeros(T.shape[0:2], np.uint8)
                cv2.drawContours(T, cnts, i,(255),-1)
                #cv2.imshow("T"+str(i), T)
                    
                target = T[b1:b2,a1:a2]
                x,y = target.shape[0:2]
                target = cv2.resize(target,(int(x/w*55),int(y/h*55)))
                #print(target.shape[0:2])
                cv2.imwrite('blue_out.png'  , target )
                #cv2.imshow("blue_target", target)
                return 1,target,x1,y1,radius
    return 0,0,0,0,0


def find_red(frame):
    img1  = cv2.inRange(frame.copy(), lower_red, upper_red)
    erosion  = cv2.erode (img1,kernel_5,iterations = 1)
    dilation = cv2.dilate(erosion  ,kernel_5,iterations = 1)
    canny = cv2.Canny(dilation, 50, 150)
    #cv2.imshow("red_canny", canny)
    cv2.imwrite('red_out.png'  , canny )
    _, cnts, _ = cv2.findContours(canny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    length = len(cnts)

    if length >0:
        for i in range(length):
            #c = sorted(cnts, key=cv2.contourArea, reverse=True)[i]
            x, y, w, h  = cv2.boundingRect(cnts[i]) # 得到最小外接矩形的（中心(x,y), (宽,高), 旋转角度）
            if w*h > 1500:
                (x1, y1), radius = cv2.minEnclosingCircle(cnts[i])
                a1 = max(x-40,2)
                a2 = min(x+w+40,638)
                b1 = max(y-40,2)
                b2 = min(y+h+40,478)
                #print(w,h)
                #print(a1,a2,b1,b2)
                T=frame.copy()
                T=np.zeros(T.shape[0:2], np.uint8)
                cv2.drawContours(T, cnts, i,(255),-1)
                
                #cv2.imshow("T"+str(i), T)
                    
                target = T[b1:b2,a1:a2]
                x,y = target.shape[0:2]
                target = cv2.resize(target,(int(x/w*55),int(y/h*55)))
                #print(target.shape[0:2])
                cv2.imwrite('red_out1.png'  , target )
                #cv2.imshow("red_target", target)
                
                return 1,target,x1,y1,radius
    return 0,0,0,0,0

def find_green(frame):
    img1  = cv2.inRange(frame.copy(), lower_green, upper_green)
    erosion  = cv2.erode (img1,kernel_5,iterations = 1)
    dilation = cv2.dilate(erosion  ,kernel_5,iterations = 1)
    canny = cv2.Canny(dilation, 50, 150)
    #cv2.imshow("green_canny", canny)
    cv2.imwrite('green_out.png'  , canny )
    _, cnts, _ = cv2.findContours(canny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    length = len(cnts)

    if length >0:
        for i in range(length):
            #c = sorted(cnts, key=cv2.contourArea, reverse=True)[i]
            x, y, w, h  = cv2.boundingRect(cnts[i]) # 得到最小外接矩形的（中心(x,y), (宽,高), 旋转角度）
            if w*h > 1500:
                (x1, y1), radius = cv2.minEnclosingCircle(cnts[i])
                a1 = max(x-40,2)
                a2 = min(x+w+40,638)
                b1 = max(y-40,2)
                b2 = min(y+h+40,478)
                #print(w,h)
                #print(a1,a2,b1,b2)
                T=frame.copy()
                T=np.zeros(T.shape[0:2], np.uint8)
                cv2.drawContours(T, cnts, i,(255),-1)
                #cv2.imshow("T"+str(i), T)
                    
                target = T[b1:b2,a1:a2]
                x,y = target.shape[0:2]
                target = cv2.resize(target,(int(x/w*55),int(y/h*55)))
                #print(target.shape[0:2])

                #cv2.imshow("green_target", target)
                
                return 1,target,x1,y1,radius
    return 0,0,0,0,0

def change(txt_in):
    if txt_in == "ER":
        return 0
    if txt_in == "E":
        return 1
    if txt_in == "S":
        return 2
    if txt_in == "C":
        return 3

def find_1():
    green_n     = 0
    red_n       = 0
    blue_n      = 0
    rectangle_n = 0
    star_n      = 0
    circle_n    = 0
    target      = [0,0,0,0]
    xt_blue     = 0
    xd_blue     = 0
    yt_blue     = 0
    yd_blue     = 0
    rt_blue     = 0
    rd_blue     = 0
    xt_red     = 0
    xd_red     = 0
    yt_red     = 0
    yd_red     = 0
    rt_red     = 0
    rd_red     = 0
    xt_green     = 0
    xd_green     = 0
    yt_green     = 0
    yd_green     = 0
    rt_green     = 0
    rd_green     = 0
    for i in range(10):
        ret,frame = cap.read()
        #frame   = frame[180:300,280:380]
        frame   = frame[180:330,280:410]
        #cv2.imshow('frame', frame)
        cv2.setMouseCallback("frame", getposBGR)
        judge_blue,target_blue,x_blue,y_blue,radius_blue = find_blue(frame)
        judge_red ,target_red,x_red,y_red,radius_red  = find_red (frame)
        judge_green ,target_green,x_green,y_green,radius_green  = find_green (frame)
        blue_number = 1
        red_number  = 1
        green_number = 1
        if(judge_blue == 1):
            blue_result,blue_number = judge(target_blue,0.20)
            xt_blue = xt_blue + 1
            xd_blue = xd_blue + x_blue
            yt_blue = yt_blue + 1
            yd_blue = yd_blue + y_blue
            rt_blue = rt_blue + 1
            rd_blue = rd_blue + radius_blue
        if(judge_red  == 1):
            red_result,red_number = judge(target_red,0.20)
            xt_red = xt_red + 1
            xd_red = xd_red + x_red
            yt_red = yt_red + 1
            yd_red = yd_red + y_red
            rt_red = rt_red + 1
            rd_red = rd_red + radius_red
        if(judge_green  == 1):
            green_result,green_number = judge(target_green,0.20)
            xt_green = xt_green + 1
            xd_green = xd_green + x_green
            yt_green = yt_green + 1
            yd_green = yd_green + y_green
            rt_green = rt_green + 1
            rd_green = rd_green + radius_green
        min_number = min(blue_number,red_number,green_number)
        if (min_number > 0.3):
            pass
        elif (min_number == blue_number):
            #print("blue",blue_result,min_number)
            blue_n = blue_n + 1
            if blue_result == "R":
                rectangle_n = rectangle_n + 1
            if blue_result == "S":
                star_n = star_n + 1
            if blue_result == "C":
                circle_n = circle_n + 1

        elif(min_number == red_number):
            #print("red",red_result,min_number)
            red_n = red_n + 1
            if red_result == "R":
                rectangle_n = rectangle_n + 1
            if red_result == "S":
                star_n = star_n + 1
            if red_result == "C":
                circle_n = circle_n + 1
        elif(min_number == green_number):
            #print("green",green_result,min_number)
            green_n = green_n + 1
            if green_result == "R":
                rectangle_n = rectangle_n + 1
            if green_result == "S":
                star_n = star_n + 1
            if green_result == "C":
                circle_n = circle_n + 1
    #print(blue_n,red_n,green_n)
    if blue_n < 3:
        blue_n = -1
    if red_n < 3:
        red_n = -1
    if green_n < 3:
        green_n = -1
    if blue_n > target[0]:
        target[1] = 1
        target[0] = blue_n
    if red_n > target[0]:
        target[1] = 2
        target[0] = red_n
    if green_n > target[0]:
        target[1] = 3
        target[0] = green_n
        
    if rectangle_n < 3:
        rectangle_n = -1
    if star_n < 3:
        star_n = -1
    if circle_n < 3:
        circle_n = -1
    if rectangle_n > target[2]:
        target[3] = 1
        target[2] = rectangle_n
    if star_n > target[2]:
        target[3] = 2
        target[2] = star_n
    if circle_n > target[2]:
        target[3] = 3
        target[2] = circle_n
    if(target[1] == 1):
        return target[1],target[3],xd_blue/xt_blue,yd_blue/yt_blue,rd_blue/rt_blue
    elif(target[1] == 2):
        return target[1],target[3],xd_red/xt_red,yd_red/yt_red,rd_red/rt_red
    elif(target[1] == 3):
        return target[1],target[3],xd_green/xt_green,yd_green/yt_green,rd_green/rt_green
    return target[1],target[3],0,0,0

def find_2():
    green_n     = 0
    red_n       = 0
    blue_n      = 0
    rectangle_n = 0
    star_n      = 0
    circle_n    = 0
    target      = [0,0,0,0]
    xt_blue     = 0
    xd_blue     = 0
    yt_blue     = 0
    yd_blue     = 0
    rt_blue     = 0
    rd_blue     = 0
    xt_red     = 0
    xd_red     = 0
    yt_red     = 0
    yd_red     = 0
    rt_red     = 0
    rd_red     = 0
    xt_green     = 0
    xd_green     = 0
    yt_green     = 0
    yd_green     = 0
    rt_green     = 0
    rd_green     = 0
    for i in range(10):
        ret,frame = cap.read()
        #frame   = frame[180:300,280:380]
        #cv2.imshow('frame', frame)
        cv2.setMouseCallback("frame", getposBGR)
        judge_blue,target_blue,x_blue,y_blue,radius_blue = find_blue(frame)
        judge_red ,target_red,x_red,y_red,radius_red  = find_red (frame)
        judge_green ,target_green,x_green,y_green,radius_green  = find_green (frame)
        blue_number = 1
        red_number  = 1
        green_number = 1
        if(judge_blue == 1):
            blue_result,blue_number = judge(target_blue,0.20)
            xt_blue = xt_blue + 1
            xd_blue = xd_blue + x_blue
            yt_blue = yt_blue + 1
            yd_blue = yd_blue + y_blue
            rt_blue = rt_blue + 1
            rd_blue = rd_blue + radius_blue
        if(judge_red  == 1):
            red_result,red_number = judge(target_red,0.20)
            xt_red = xt_red + 1
            xd_red = xd_red + x_red
            yt_red = yt_red + 1
            yd_red = yd_red + y_red
            rt_red = rt_red + 1
            rd_red = rd_red + radius_red
        if(judge_green  == 1):
            green_result,green_number = judge(target_green,0.20)
            xt_green = xt_green + 1
            xd_green = xd_green + x_green
            yt_green = yt_green + 1
            yd_green = yd_green + y_green
            rt_green = rt_green + 1
            rd_green = rd_green + radius_green
        min_number = min(blue_number,red_number,green_number)
        if (min_number > 0.3):
            pass
        elif (min_number == blue_number):
            #print("blue",blue_result,min_number)
            blue_n = blue_n + 1
            if blue_result == "R":
                rectangle_n = rectangle_n + 1
            if blue_result == "S":
                star_n = star_n + 1
            if blue_result == "C":
                circle_n = circle_n + 1

        elif(min_number == red_number):
            #print("red",red_result,min_number)
            red_n = red_n + 1
            if red_result == "R":
                rectangle_n = rectangle_n + 1
            if red_result == "S":
                star_n = star_n + 1
            if red_result == "C":
                circle_n = circle_n + 1
        elif(min_number == green_number):
            #print("green",green_result,min_number)
            green_n = green_n + 1
            if green_result == "R":
                rectangle_n = rectangle_n + 1
            if green_result == "S":
                star_n = star_n + 1
            if green_result == "C":
                circle_n = circle_n + 1
    #print(blue_n,red_n,green_n)
    if blue_n < 3:
        blue_n = -1
    if red_n < 3:
        red_n = -1
    if green_n < 3:
        green_n = -1
    if blue_n > target[0]:
        target[1] = 1
        target[0] = blue_n
    if red_n > target[0]:
        target[1] = 2
        target[0] = red_n
    if green_n > target[0]:
        target[1] = 3
        target[0] = green_n
        
    if rectangle_n < 3:
        rectangle_n = -1
    if star_n < 3:
        star_n = -1
    if circle_n < 3:
        circle_n = -1
    if rectangle_n > target[2]:
        target[3] = 1
        target[2] = rectangle_n
    if star_n > target[2]:
        target[3] = 2
        target[2] = star_n
    if circle_n > target[2]:
        target[3] = 3
        target[2] = circle_n
    if(target[1] == 1):
        return target[1],target[3],xd_blue/xt_blue,yd_blue/yt_blue,rd_blue/rt_blue
    elif(target[1] == 2):
        return target[1],target[3],xd_red/xt_red,yd_red/yt_red,rd_red/rt_red
    elif(target[1] == 3):
        return target[1],target[3],xd_green/xt_green,yd_green/yt_green,rd_green/rt_green
    return target[1],target[3],0,0,0

def find_3():
    P = 0
    L = 0
    Z = 0
    k = 0
    ax = 0
    bx = 0
    ay = 0
    by = 0
    for i in range(20):
        ret,frame = cap.read()
        #frame=cv2.medianBlur(frame,3)
        #frame = cv2.imread("lanqiu32.png") # 定片位置
        #frame = cv2.imread("zuqiu32.png") # 定片位置
        #frame = cv2.imread("paiqiu12.png") # 定片位置
        #frame   = frame[160:300,280:400]
        frame   = frame[180:330,280:410]

        img   = frame
        #cv2.imshow("frame", frame)

        try:
        

            
            #img = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
            baidi = cv2.inRange(img.copy(), lower, upper)
            #cv2.imshow("baidi", baidi)
            cv2.imwrite("baidi.png", baidi)
            #print(1)

            _, cnts, _ = cv2.findContours(baidi,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            
            length = len(cnts)
            #print(length)
            max_i = 0
            max_n = 0
            if length >0:
                for i in range(length):
                    x, y, w, h  = cv2.boundingRect(cnts[i]) 
                    if w*h > max_n:
                        max_i = i
                        max_n = w*h
                
                T=np.zeros(img.shape, np.uint8)
                cv2.drawContours(T, cnts, max_i,(255,255,255),-1)
                #cv2.imshow("T", T)
                part    = cv2.bitwise_and(T,img)
                #cv2.imshow("part", part)

                part[baidi != 0] = [0,0,0]
                
                #cv2.imshow("part2", part)
                cv2.imwrite("part2.png", part)
                part = cv2.cvtColor(part,cv2.COLOR_BGR2HSV)
            #cv2.imshow("img", img)
            #点击获取目标HSV值
            '''
            lanqiu_lower = np.array([10 , 130 , 20])
            lanqiu_upper = np.array([30, 240, 120])
            # 15 220 70

            zuqiu_lower = np.array([60 , 40 , 80])
            zuqiu_upper = np.array([120, 70, 180])
            # 100 23 143

            paiqiu_lower1 = np.array([0 , 20 , 150])
            paiqiu_upper1 = np.array([30, 150, 255])

            paiqiu_lower2 = np.array([0 , 200 , 130])
            paiqiu_upper2 = np.array([30, 255, 230])

            paiqiu_lower3 = np.array([80 , 0 , 150])
            paiqiu_upper3 = np.array([150, 40, 255])
        # 20 255 150
            # 20 255 150
            '''
            x1 = 0
            x2 = 0
            x3 = 0
            y1 = 0
            y2 = 0
            y3 = 0
            lanqiu = cv2.inRange(part.copy(), lanqiu_lower, lanqiu_upper)
            #cv2.imshow("lanqiu", lanqiu)
            #cv2.imwrite("lanqiu.png",lanqiu)
            erosion  = cv2.erode (lanqiu,kernel_5,iterations = 1)
            dilation = cv2.dilate(erosion  ,kernel_5,iterations = 1)
            _, cnts, _ = cv2.findContours(dilation,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            max_i = 0
            max_n = 0
            length = len(cnts)
            if length:
                for i in range(length):
                    (x, y), radius = cv2.minEnclosingCircle(cnts[i])
                    if radius > max_n:
                        max_i = i
                        max_n = radius
                (x1, y1), radius1 = cv2.minEnclosingCircle(cnts[max_i])
            
            cv2.imwrite("lanqiu.png",dilation)


            zuqiu = cv2.inRange(part.copy(), zuqiu_lower, zuqiu_upper)
            erosion  = cv2.erode (zuqiu,kernel_5,iterations = 1)
            dilation = cv2.dilate(erosion  ,kernel_5,iterations = 1)
            _, cnts, _ = cv2.findContours(dilation,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            max_i = 0
            max_n = 0
            length = len(cnts)
            if length:
                for i in range(length):
                    (x, y), radius = cv2.minEnclosingCircle(cnts[i])
                    if radius > max_n:
                        max_i = i
                        max_n = radius
                (x2, y2), radius2 = cv2.minEnclosingCircle(cnts[max_i])
            cv2.imwrite("zuqiu.png",zuqiu)
            #cv2.imshow("zuqiu", zuqiu)

            paiqiu = (cv2.inRange(part.copy(), paiqiu_lower1, paiqiu_upper1)
                  +cv2.inRange(part.copy(), paiqiu_lower2, paiqiu_upper2)
                  +cv2.inRange(part.copy(), paiqiu_lower3, paiqiu_upper3))
            erosion  = cv2.erode (paiqiu,kernel_5,iterations = 1)
            dilation = cv2.dilate(erosion  ,kernel_5,iterations = 1)
            _, cnts, _ = cv2.findContours(dilation,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            max_i = 0
            max_n = 0
            length = len(cnts)
            if length:
                for i in range(length):
                    (x, y), radius = cv2.minEnclosingCircle(cnts[i])
                    if radius > max_n:
                        max_i = i
                        max_n = radius
                (x3, y3), radius3 = cv2.minEnclosingCircle(cnts[max_i])
            cv2.imwrite("paiqiu.png",paiqiu)
            
            #cv2.imshow("paiqiu", paiqiu)
            
            num_lanqiu = 0
            for a in range(lanqiu.shape[0]):
                for b in range(lanqiu.shape[1]):
                    if lanqiu[a][b] != 0:
                        num_lanqiu = num_lanqiu + 1

            num_zuqiu = 0
            for a in range(zuqiu.shape[0]):
                for b in range(zuqiu.shape[1]):
                    if zuqiu[a][b] != 0:
                        num_zuqiu = num_zuqiu + 1

            num_paiqiu = 0
            for a in range(paiqiu.shape[0]):
                for b in range(paiqiu.shape[1]):
                    if paiqiu[a][b] != 0:
                        num_paiqiu = num_paiqiu + 1
            
            #print("num_lanqiu",num_lanqiu)
            #print("num_zuqiu",num_zuqiu)
            #print("num_paiqiu",num_paiqiu)

            if num_paiqiu > 200 :
                #print("排球")
                P = P + 1
                k = k + 2
                ax = ax + x3 + 280
                bx = bx + 1
                ay = ay + y3 + 180
                by = by + 1

            else:
                if num_lanqiu > num_zuqiu and num_lanqiu >50:
                    #print("篮球")
                    L = L + 1
                    k = k + 2
                    ax = ax + x1 + 280 
                    bx = bx + 1
                    ay = ay + y1 + 180
                    by = by + 1

                elif num_zuqiu > num_lanqiu and num_zuqiu >100:
                    #print("足球")
                    Z = Z + 1
                    k = k + 2
                    ax = ax + x2 + 280
                    bx = bx + 1
                    ay = ay + y2 + 180
                    by = by + 1

                else:
                    k = k + 1

        except:
            print("error")
            k = k + 1
        if k > 20 :
            break
    n = 0
    if bx :
        xz = ax / bx
    else:
        xz = 0
    if by :
        yz = ay / by
    else:
        yz = 0
    if P > L:
        result = P
        name   = "排球"
    else:
        result = L
        name   = "篮球"
    if Z > result:
        name   = "足球"
    return name,xz,yz

def find_4():
    P = 0
    L = 0
    Z = 0
    k = 0
    ax = 0
    bx = 0
    ay = 0
    by = 0
    for i in range(20):
        ret,frame = cap.read()
        #frame=cv2.medianBlur(frame,3)
        #frame = cv2.imread("lanqiu32.png") # 定片位置
        #frame = cv2.imread("zuqiu32.png") # 定片位置
        #frame = cv2.imread("paiqiu12.png") # 定片位置
        #frame   = frame[160:300,280:400]
        frame   = frame[180:330,280:410]

        img   = frame
        #cv2.imshow("frame", frame)

        try:
        

            
            #img = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
            baidi = cv2.inRange(img.copy(), lower, upper)
            #cv2.imshow("baidi", baidi)
            cv2.imwrite("baidi.png", baidi)
            #print(1)

            _, cnts, _ = cv2.findContours(baidi,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            
            length = len(cnts)
            #print(length)
            max_i = 0
            max_n = 0
            if length >0:
                for i in range(length):
                    x, y, w, h  = cv2.boundingRect(cnts[i]) 
                    if w*h > max_n:
                        max_i = i
                        max_n = w*h
                
                T=np.zeros(img.shape, np.uint8)
                cv2.drawContours(T, cnts, max_i,(255,255,255),-1)
                #cv2.imshow("T", T)
                part    = cv2.bitwise_and(T,img)
                #cv2.imshow("part", part)

                part[baidi != 0] = [0,0,0]
                
                #cv2.imshow("part2", part)
                cv2.imwrite("part2.png", part)
                qiu = cv2.inRange(part.copy(), np.array([2,2,2]),np.array([255, 255 , 255]))
                cv2.imwrite("part3.png", qiu)
                _, cnts, _ = cv2.findContours(qiu,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                length = len(cnts)
                #print(length)
                max_i = 0
                max_n = 0
                if length >0:
                    for i in range(length):
                        x, y, w, h  = cv2.boundingRect(cnts[i]) 
                        if w*h > max_n:
                            max_i = i
                            max_n = w*h
                (x, y), radius = cv2.minEnclosingCircle(cnts[max_i])
                T=np.zeros(img.shape, np.uint8)
                T=cv2.drawContours(T, cnts, max_i,(255,255,255),-1)
                cv2.imwrite("part4.png", T)
                ax = ax + x + 280
                bx = bx + 1
                ay = ay + y + 180
                by = by + 1
                k  = k + 1
        except:
            k = k + 1
        if k > 10 :
            break
    if bx :
        xz = ax / bx
    else:
        xz = 0
    if by :
        yz = ay / by
    else:
        yz = 0
    
    return xz,yz
        

def math_L(dis,length):
    return dis*length/180*40



def math(D,dis,S):
    length = length_math(D,S)
    if length == 0:
        length = 57
    return math_L(dis,length)

def uart_send(txt):
    ser.write(txt.encode("utf-8"))
    print(txt)

def uart_collect():
    count = ser.inWaiting()  # 位置4
    if count != 0:
        recv = ser.read(count)  # 位置5
        print(recv)
        ser.flushInput()
        return 1,recv
    return 0,0

def uart_judge(txt):
    try:
        txt = str(txt)[2::]
        if(txt[0] == "A"):
            return 1,0
        elif(txt[0] == "C"):
            return 2,int(txt[1:5])
        elif(txt[0] == "E"):
            return 3,0
        elif(txt[0] == "G"):
            return 4,int(txt[1:5])
        elif(txt[0] == "L"):
            return 5,0
        elif(txt[0] == "Q"):
            return 6,int(txt[1:5])
        elif(txt[0] == "H"):
            return 7,0
        return 0,0
    except:
        print("通讯错误",txt)
        return 0,0

def uart():
    while(True):
        if_collect,txt_collect = uart_collect()
        if if_collect :
            mode,result = uart_judge(txt_collect)
            #print(result)


def case_1():
    result_c,result_x,x,y,radius = find_1()
    #print("radius",radius)
    uart_send("B")
    b_out = 0
    t1 = time.time()
    while(True):
        if_collect,recv = uart_collect()
        if if_collect:
            if_collect,dis = uart_judge(recv)
            if if_collect == 2:
                dis = int(dis)/1000
                break
        time.sleep(0.1)
        if time.time()-t1 > 1:
            b_out = 1
            break
    if b_out:
        print("通讯失败")
        return
    result_txt = ""
    if result_c == 1:
        result_txt = result_txt + "blue "
    elif result_c == 2:
        result_txt = result_txt + "red "
    elif result_c == 3:
        result_txt = result_txt + "green "
    else:
        result_txt = result_txt + "Green "
    if result_x == 1:
        length = math(radius*2,dis,"R")
        result_txt = result_txt + "rectangle " + str(length) + "cm " + str(dis) + "m"
        #print(radius)
    elif result_x == 2:
        length = math(radius*2,dis,"S")
        result_txt = result_txt + "star " + str(length) + "cm " + str(dis) + "m"
        #print(radius)
    elif result_x == 3:
        length = math(radius*2,dis,"C")
        result_txt = result_txt + "circle " + str(length) + "cm " + str(dis) + "m"
        #print(radius)
    else:
        length = math(radius*2,dis,"R")
        result_txt = result_txt + "Rectangle " + str(length) + "cm " + str(dis) + "m"
    print(result_txt)

    uart_send("D")

def case_2():
    result_c,result_x,x,y,radius = find_2()
    uart_send("F"+str(int(x/100))+str(int((x%100)/10))+str(int(x%10))
                 +str(int(y/100))+str(int((y%100)/10))+str(int(y%10)))

def case_3(dis):
    result_c,result_x,x,y,radius = find_2()
    result_txt = ""
    if result_c == 1:
        result_txt = result_txt + "blue "
    elif result_c == 2:
        result_txt = result_txt + "red "
    elif result_c == 3:
        result_txt = result_txt + "green "
    else:
        result_txt = result_txt + "Green "
    if result_x == 1:
        length = math(radius*2,dis,"R")
        result_txt = result_txt + "rectangle " + str(length) + "cm " + str(dis) + "cm"
    elif result_x == 2:
        length = math(radius*2,dis,"S")
        result_txt = result_txt + "star " + str(length) + "cm " + str(dis) + "m"
    elif result_x == 3:
        length = math(radius*2,dis,"C")
        result_txt = result_txt + "circle " + str(length) + "cm " + str(dis) + "m"
    else:
        length = math(radius*2,dis,"R")
        result_txt = result_txt + "Rectangle " + str(length) + "cm " + str(dis) + "m"
    print(result_txt)
    uart_send("D")

def case_4():
    x,y = find_4()
    uart_send("L"+str(int(x/100))+str(int((x%100)/10))+str(int(x%10))
                 +str(int(y/100))+str(int((y%100)/10))+str(int(y%10)))
    #print(name)

def case_5(dis):
    name,x,y = find_3()
    #uart_send("D")
    print(name+" "+str(dis)+"m")

def case_6():
    result_c,result_x,x,y,radius = find_1()
    #print("radius",radius)
    result_txt  = ""
    result_data = "H" + str(int(radius/100))+str(int((radius%100)/10))+str(int(radius%10))
    if result_c == 1:
        result_txt = result_txt + "blue "
    elif result_c == 2:
        result_txt = result_txt + "red "
    elif result_c == 3:
        result_txt = result_txt + "green "
    else:
        result_txt = result_txt + "Green "
    if result_x == 1:
        
        result_txt = result_txt + "rectangle "
        result_data = result_data + "1"
        #print(radius)
    elif result_x == 2:
        
        result_txt = result_txt + "star " 
        result_data = result_data + "2"
        #print(radius)
    elif result_x == 3:
        
        result_txt = result_txt + "circle " 
        result_data = result_data + "3"
        #print(radius)
    else:
        
        result_txt = result_txt + "Rectangle "
        result_data = result_data + "1"
    print(result_txt)

    uart_send(result_data)



if __name__ == "__main__":
    print("系统启动")
    while(True):
        time.sleep(0.1)
        a1,a2 = uart_collect()
        if a1:
            b1,b2 = uart_judge(a2)
            if b1 == 1:
                print("开始识别")

                for i in range(10):
                    ret,frame = cap.read()
                    #time.sleep(0.1)
                case_1()
            elif b1 == 3:
                print("追踪进行中")
                for i in range(10):
                    ret,frame = cap.read()
                    #time.sleep(0.1)
                case_2()
            elif b1 == 4:
                print("开始识别")
                for i in range(10):
                    ret,frame = cap.read()
                    #time.sleep(0.1)
                case_3(int(b2)/1000)
            elif b1 == 5:
                print("追踪进行中")
                for i in range(10):
                    ret,frame = cap.read()
                    #time.sleep(0.1)
                case_4()
            elif b1 == 6:
                print("开始识别")
                for i in range(10):
                    ret,frame = cap.read()
                    #time.sleep(0.1)
                case_5(int(b2)/1000)
            elif b1 == 7:
                print("开始测绘")
                for i in range(10):
                    ret,frame = cap.read()
                    #time.sleep(0.1)
                case_6()
