import cv2
import numpy as np
import os


def FindLabels(img,labels,r,c):
    labels_cor = np.transpose(np.nonzero(labels))
    for i in labels_cor:
        if (i[0] > r / 2 and i[1] < c / 2):
            bl = i
        elif (i[0] < r / 2 and i[1] < c / 2):
            tl = i
        elif (i[0] > r / 2 and i[1] > c / 2):
            br = i
    bl_region = np.copy(labels[bl[0] - 50 : bl[0] + 50,bl[1] - 50 : bl[1] + 50])
    _,bl_region = cv2.threshold(bl_region,127,255,cv2.THRESH_BINARY)
    br_region = np.copy(labels[br[0] - 50 : br[0] + 50,br[1] - 50 : br[1] + 50])
    _,br_region = cv2.threshold(br_region,127,255,cv2.THRESH_BINARY)
    tl_region = np.copy(labels[tl[0] - 50 : tl[0] + 50,tl[1] - 50 : tl[1] + 50])
    _,tl_region = cv2.threshold(tl_region,127,255,cv2.THRESH_BINARY)
    
    bl_well = cv2.HoughCircles(bl_region, cv2.HOUGH_GRADIENT, 1, 200, \
                             param1=150, param2=5, minRadius=20, maxRadius=25)
    br_well = cv2.HoughCircles(br_region, cv2.HOUGH_GRADIENT, 1, 200, \
                             param1=150, param2=5, minRadius=20, maxRadius=25)
    tl_well = cv2.HoughCircles(tl_region, cv2.HOUGH_GRADIENT, 1, 200, \
                             param1=150, param2=5, minRadius=20, maxRadius=25)
    bl_center = (bl[0] - 50 + bl_well[0][0][1],bl[1] - 50 + bl_well[0][0][0])
    br_center = (br[0] - 50 + br_well[0][0][1],br[1] - 50 + br_well[0][0][0])
    tl_center = (tl[0] - 50 + tl_well[0][0][1],tl[1] - 50 + tl_well[0][0][0])
    radius = 0.95 * (bl_well[0][0][2] + br_well[0][0][2] + tl_well[0][0][2]) / 3

    for i in bl_well[0,:]:
        cv2.circle(bl_region,(i[0],i[1]),i[2],127,1)
    for i in br_well[0,:]:
        cv2.circle(br_region,(i[0],i[1]),i[2],127,1)
    for i in tl_well[0,:]:
        cv2.circle(tl_region,(i[0],i[1]),i[2],127,1)
    #cv2.circle(br_region,(int(br_well[0][0][0]),int(br_well[0][0][1])),3,127,-1)
    cv2.imshow('bl',bl_region)
    cv2.imshow('br',br_region)
    cv2.imshow('tl',tl_region)
    
    
    return (bl_center,br_center,tl_center,int(radius))
    

outputfile = open('result.txt','w')
outputfile.write("Img\tIntensity\tSTD\n")

for imgfile in os.listdir('.'):
    if imgfile.endswith('.jpg'):
        

        img0 = cv2.imread(imgfile)
        r,c,_ = img0.shape
        img0 = cv2.resize(img0,(int(c / 4),int(r / 4)),cv2.INTER_AREA)
        r = int(r / 4)
        c = int(c / 4)
        #cv2.namedWindow('wells',cv2.WINDOW_NORMAL)

        labels = img0[:,:,0]
        img = img0[:,:,2]

        #_,thresh = cv2.threshold(img,10,255,cv2.THRESH_BINARY)
        _,labels = cv2.threshold(labels,127,255,cv2.THRESH_BINARY)

        bl,br,tl,radius = FindLabels(img,labels,r,c)
        print (bl,br,tl,radius)

        x_dist_row = (br[1] - bl[1]) / 49
        y_dist_row = (br[0] - bl[0]) / 49
        x_dist_col = (bl[1] - tl[1]) / 15
        y_dist_col = (bl[0] - tl[0]) / 15
        print(1)
        intensity = []
        for i in range(8):
            intensity.append([])
            #print (intensity)
            anchor = (tl[0] + 2 * i * y_dist_col,tl[1] + 2 * i * x_dist_col)
            for j in range(48):
                x = int(anchor[1] + (j + 1) * x_dist_row)
                y = int(anchor[0] + (j + 1) * y_dist_row)
                mask = np.zeros((2 * radius,2 * radius),np.uint8)
                cv2.circle(mask,(radius,radius),radius,255,-1)

                cv2.circle(img0,(x,y),radius,(255,0,0),3)
                
                intensity[i].append(cv2.mean(img[y-radius:y+radius,x-radius:x+radius],mask=mask)[0])
            anchor2 = (anchor[0] + y_dist_col,anchor[1] + x_dist_col)
            for j in range(48):
                x = int(anchor2[1] + (j + 1) * x_dist_row)
                y = int(anchor2[0] + (j + 1) * y_dist_row)
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

        
