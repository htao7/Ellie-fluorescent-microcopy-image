import cv2
import numpy as np
import os


def FindLabels(labels,r,c):
    
    bl_region = np.copy(labels[int(r / 2):r,0:int(c / 2)])
    br_region = np.copy(labels[int(r / 2):r,int(c / 2):c])
    tl_region = np.copy(labels[0:int(r / 2),0:int(c / 2)])

    #cv2.imshow('bl',bl_region)
    #cv2.imshow('br',br_region)
    #cv2.imshow('tl',tl_region)
    #cv2.waitKey(0)
    
    bl_well = cv2.HoughCircles(bl_region, cv2.HOUGH_GRADIENT, 1, 200, \
                             param1=150, param2=10, minRadius=20, maxRadius=22)
    br_well = cv2.HoughCircles(br_region, cv2.HOUGH_GRADIENT, 1, 200, \
                             param1=150, param2=10, minRadius=20, maxRadius=22)
    tl_well = cv2.HoughCircles(tl_region, cv2.HOUGH_GRADIENT, 1, 200, \
                             param1=150, param2=10, minRadius=20, maxRadius=22)
    #print (bl_well[0][0])
    bl_center = (bl_well[0][0][0],int (r / 2) + bl_well[0][0][1])
    br_center = (int (c / 2) + br_well[0][0][0],int(r / 2) + br_well[0][0][1])
    tl_center = (tl_well[0][0][0],tl_well[0][0][1])
    radius = 0.95 * (bl_well[0][0][2] + br_well[0][0][2] + tl_well[0][0][2]) / 3

    for i in bl_well[0,:]:
        cv2.circle(bl_region,(i[0],i[1]),i[2],127,1)
    for i in br_well[0,:]:
        cv2.circle(br_region,(i[0],i[1]),i[2],127,1)
    for i in tl_well[0,:]:
        cv2.circle(tl_region,(i[0],i[1]),i[2],127,1)  
    
    return (bl_center,br_center,tl_center,int(radius))
    

outputfile = open('result.txt','w')
outputfile.write("Img\tIntensity\tSTD\n")

for imgfile in os.listdir('.'):
    if imgfile.endswith('.jpg') and imgfile.startswith('array') is False:
        
        print (imgfile)
        img0 = cv2.imread(imgfile)
        r,c,_ = img0.shape
        img0 = cv2.resize(img0,None,fx=0.25,fy=0.25,interpolation=cv2.INTER_AREA)
        r1 = int(r / 4)
        c1 = int(c / 4)
        #cv2.namedWindow('wells',cv2.WINDOW_NORMAL)

        labels = img0[:,:,0]
        img = img0[:,:,2]
        
        #_,thresh = cv2.threshold(img,10,255,cv2.THRESH_BINARY)
        _,labels = cv2.threshold(labels,127,255,cv2.THRESH_BINARY)
        #cv2.imshow('labels',img0)

        bl,br,tl,radius = FindLabels(labels,r1,c1)
        #print (bl,br,tl,radius)

        x_dist_row = (br[0] - bl[0]) / 49
        y_dist_row = (br[1] - bl[1]) / 49
        x_dist_col = (bl[0] - tl[0]) / 15
        y_dist_col = (bl[1] - tl[1]) / 15

        intensity = []
        for i in range(8):
            intensity.append([])
            #print (intensity)
            anchor = (tl[0] + 2 * i * x_dist_col,tl[1] + 2 * i * y_dist_col)
            for j in range(48):
                x = int(anchor[0] + (j + 1) * x_dist_row)
                y = int(anchor[1] + (j + 1) * y_dist_row)
                mask = np.zeros((2 * radius,2 * radius),np.uint8)
                cv2.circle(mask,(radius,radius),radius,255,-1)
                cv2.circle(img0,(x,y),radius,(255,0,0),3)
                #cv2.imshow('img0',img0)
                intensity[i].append(cv2.mean(img[y-radius:y+radius,x-radius:x+radius],mask=mask)[0])
            anchor2 = (anchor[0] + x_dist_col,anchor[1] + y_dist_col)
            for j in range(48):
                x = int(anchor2[0] + (j + 1) * x_dist_row)
                y = int(anchor2[1] + (j + 1) * y_dist_row)
                mask = np.zeros((2 * radius,2 * radius),np.uint8)
                cv2.circle(mask,(radius,radius),radius,255,-1)
                cv2.circle(img0,(x,y),radius,(255,0,0),3)
                intensity[i].append(cv2.mean(img[y-radius:y+radius,x-radius:x+radius],mask=mask)[0])

        for i in range(8):
            #print (np.mean(intensity[i]),np.std(intensity[i]))
            outputfile.write("%s\t%.2f\t%.2f\n" % (imgfile,np.mean(intensity[i]),np.std(intensity[i])))
            
        #cv2.imshow('wells',img0)
        #cv2.resizeWindow('wells',(2000,int(r/(c/2000))))
        cv2.imwrite('array' + imgfile,img0)
        #cv2.waitKey(0)

outputfile.close()
#cv2.waitKey(0)

        
