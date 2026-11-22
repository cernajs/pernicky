import cv2, numpy as np, sys, json
img = cv2.imread(sys.argv[1])
src = np.float32([[212,165],[2483,121],[2567,1894],[-16,1893]])
S=10 # px per mm
P=100
dst = np.float32([[P,P],[2970+P,P],[2970+P,2100+P],[P,2100+P]])
M = cv2.getPerspectiveTransform(src,dst)
w = cv2.warpPerspective(img, M, (2970+2*P,2100+2*P), borderValue=(255,255,255)).astype(int)
cv2.imwrite('warped.jpg', w.astype(np.uint8))
b,g,r = w[...,0],w[...,1],w[...,2]
m = (((b-r)>22)&((b-g)>8)).astype(np.uint8)*255
m[:600]=0
m = cv2.dilate(m, np.ones((5,5),np.uint8))
n,lab,st,cen = cv2.connectedComponentsWithStats(m)
out={}
for name,(xa,xb) in zip(['hat','house','bear'], [(0,1150),(1150,2220),(2220,4000)]):
    keep=[i for i in range(1,n) if xa<=cen[i,0]<xb and st[i,4]>30]
    c = np.isin(lab,keep).astype(np.uint8)*255
    c = cv2.morphologyEx(c, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(35,35)))
    ys,xs = np.nonzero(c); ymax=ys.max()
    # close the bottom: connect the lowest ink point left of centre with lowest right of centre
    cx = (xs.min()+xs.max())/2
    L = [(x,y) for x,y in zip(xs,ys) if x<cx]; R=[(x,y) for x,y in zip(xs,ys) if x>=cx]
    pl = max(L,key=lambda t:t[1]); pr = max(R,key=lambda t:t[1])
    yb = max(pl[1],pr[1])
    cv2.line(c,(int(pl[0]),int(pl[1])),(int(pl[0]),yb),255,9)
    cv2.line(c,(int(pr[0]),int(pr[1])),(int(pr[0]),yb),255,9)
    cv2.line(c,(int(pl[0]),yb),(int(pr[0]),yb),255,9)
    cs,_ = cv2.findContours(c, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    filled = np.zeros_like(c); cv2.drawContours(filled,[max(cs,key=cv2.contourArea)],-1,255,-1)
    filled = cv2.erode(filled, np.ones((5,5),np.uint8))  # centre on pen line
    filled = cv2.GaussianBlur(filled,(15,15),0); filled=(filled>127).astype(np.uint8)*255
    cs,_ = cv2.findContours(filled, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnt = max(cs,key=cv2.contourArea).reshape(-1,2).astype(float)/S
    out[name]=cnt.tolist()
    x0,y0,ww,hh = cv2.boundingRect(max(cs,key=cv2.contourArea))
    print(name, 'drawn size mm', ww/S, hh/S, 'pl',pl,'pr',pr)
json.dump(out, open('outlines.json','w'))
vis = np.full((2300,3170,3),255,np.uint8)
for k,v in out.items():
    cv2.polylines(vis,[(np.array(v)*S).astype(np.int32)],True,(0,0,200),4)
cv2.imwrite('trace_vis.png', cv2.resize(vis,(1585,1150)))
