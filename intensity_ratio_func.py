import cv2
from matplotlib import pyplot as plt
import numpy as np

WELL_RADIUS = 10
ROUNDNESS = 8


def nothing(x):
    pass

# Draw the gridlines
def DrawLine(rho,theta,im):
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*rho
    y0 = b*rho
    x1 = int(x0 + 2000*(-b))
    y1 = int(y0 + 2000*(a))
    x2 = int(x0 - 2000*(-b))
    y2 = int(y0 - 2000*(a))
    cv2.line(im,(x1,y1),(x2,y2),(255,255,255),1)
    return (im)

# Fix the wells onto a 3-line grid
# Calculate STD and normalized avg.I over all wells
def FindWells(center_map,center_list,blur,im,radius):
    intensity_ratio_divide = 0
    intensity_ratio_subtract = 0
    stddev_divide = 0
    stddev_subtract = 0
    lines = cv2.HoughLines(center_map,radius / 5,np.pi / 360,5)
    if lines is None:
        return (im,intensity_ratio_divide,stddev_divide,intensity_ratio_subtract,stddev_subtract)
    [[rho0,theta0]] = lines[0]
    top3lines = [[rho0,theta0]]
    count = 1
    for i in range(1,len(lines)):
        if count >= 3:
            break
        rho = lines[i][0][0]
        theta = lines[i][0][1]
        #DrawLine(rho,theta,im)
        if np.absolute(theta - theta0) < 1e-4 and np.absolute(rho - rho0) > 2 * radius + 1:
            if count == 1 or np.absolute(rho - top3lines[1][0]) > 2 * radius + 1:
                top3lines.append([rho,theta])
                count += 1
    avgi_well_list_divide = []
    avgi_well_list_subtract = []
    for [rho,theta] in top3lines:
        #DrawLine(rho,theta,im)
        for [x,y] in center_list:
            rhoo = x * np.cos(theta) + y * np.sin(theta)
            dist = rho - rhoo
            if np.absolute(dist) < radius / 3:
                #x1 = x + dist * np.cos(theta)
                #y1 = y + dist * np.sin(theta)
                x1 = x
                y1 = y
                mask_fg = np.zeros(blur.shape,np.uint8)
                cv2.circle(mask_fg,(x1,y1),radius,255,-1)
                avgi_well_fg = cv2.mean(blur,mask=mask_fg)[0]
                mask_bg = np.zeros(blur.shape, np.uint8)
                cv2.circle(mask_bg, (x1, y1), int(1.8 * radius), 255, -1)
                cv2.circle(mask_bg, (x1, y1), int(1.5 * radius), 0, -1)
                avgi_well_bg = cv2.mean(blur, mask=mask_bg)[0]
                avgi_well_list_divide.append(avgi_well_fg / avgi_well_bg)
                avgi_well_list_subtract.append(avgi_well_fg - avgi_well_bg)
                cv2.circle(im,(x1,y1),radius,(0,255,0),1)
    
    stddev_divide = np.std(avgi_well_list_divide)
    intensity_ratio_divide = np.mean(avgi_well_list_divide)
    stddev_subtract = np.std(avgi_well_list_subtract)
    intensity_ratio_subtract = np.mean(avgi_well_list_subtract)
    return (im,intensity_ratio_divide,stddev_divide,intensity_ratio_subtract,stddev_subtract)

# Coarse detection of wells
def IntensityRatio(image):

    cv2.namedWindow('wells')
    cv2.createTrackbar('Radius','wells',WELL_RADIUS,20,nothing)
    cv2.createTrackbar('Roundness','wells',ROUNDNESS - 5,5,nothing)
    
    img0 = cv2.imread(image)
    r,c,_ = img0.shape
    img = cv2.resize(img0,(int(c/10),int(r/10)),interpolation=cv2.INTER_AREA)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    blur = cv2.GaussianBlur(hsv[:,:,2], (3, 3), 0)
    
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #blur = cv2.GaussianBlur(gray, (3, 3), 0)
    
    edges = cv2.Laplacian(blur,cv2.CV_8U)
    edges = (edges/np.max(edges)*255).astype(np.uint8)
    
    while(1):
        k = cv2.waitKey(10) & 0xFF
        if k == 27:
            break
        im = np.copy(img)
        intensity_ratio_divide = 0
        intensity_ratio_subtract = 0
        stddev_divide = 0
        stddev_subtract = 0
        radius = cv2.getTrackbarPos('Radius','wells')
        roundness = cv2.getTrackbarPos('Roundness','wells')
        
        #thres = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,2 * radius - 1,1)
        #edges = cv2.bitwise_or(edges,thres)
        #cv2.imshow('edges',edges)
        
        wells = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, radius * 2 + 1, \
                             param1=70, param2=roundness + radius - 5, minRadius=int(0.9 * radius), maxRadius=int(1.1 * radius))
        if wells is not None:
            wells = np.uint16(np.around(wells))
            center_map = np.zeros((int(r/10),int(c/10)),np.uint8)
            center_list = []
            for i in wells[0,:]:
                mask_fg = np.zeros((int(r/10),int(c/10)),np.uint8)
                cv2.circle(mask_fg,(i[0],i[1]),i[2],255,-1)
                mask_bg = np.zeros((int(r/10),int(c/10)),np.uint8)
                cv2.circle(mask_bg,(i[0],i[1]),int(i[2] * 1.5),255,-1)
                cv2.circle(mask_bg,(i[0],i[1]),i[2],0,-1)
                if cv2.mean(blur,mask=mask_fg)[0] > 1.5 * cv2.mean(blur,mask=mask_bg)[0]:
                    center_map[i[1]][i[0]] = 255
                    center_list.append([i[0],i[1]])
            im,intensity_ratio_divide,stddev_divide,intensity_ratio_subtract,stddev_subtract = FindWells(center_map,center_list,blur,im,radius)
        cv2.imshow('wells',im)

    print("intensity ratio (divide) = " + str(intensity_ratio_divide))
    print("stddev (divide) = " + str(stddev_divide))
    print("intensity ratio (subtract) = " + str(intensity_ratio_subtract))
    print("stddev (subtract) = " + str(stddev_subtract))
    cv2.destroyAllWindows()
    return (intensity_ratio_divide,stddev_divide,intensity_ratio_subtract,stddev_subtract)

if __name__ == '__main__':
    #IntensityRatio("./viability/1dapi.bmp")
    IntensityRatio("./time/2.bmp")
