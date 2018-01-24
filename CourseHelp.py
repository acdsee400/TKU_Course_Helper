import shutil
import requests
import cv2
import re
import numpy as np
from PIL import Image
from bs4 import BeautifulSoup
from io import BytesIO
import keras.preprocessing
import h5py
from time import sleep
from keras.models import Model
#from keras.models import load_model
from keras.preprocessing import image
captcha_word = "_0123456789"
word_class=len(captcha_word)
account=""
password=""
baseurl="http://www.ais.tku.edu.tw/EleCos/"
homeurl=baseurl+"login.aspx"
actionurl=baseurl+"action.aspx"
def genCode(img):
    width = 120
    height = 32
    model=keras.models.load_model("model/captcha_model_v3.h5")
    #model.load_weights("model/captcha_model_weights_v3.h5")
    X_test = np.zeros((1, height, width,3), dtype = np.float32)
    X_test[0]=image.img_to_array(img)
    result=model.predict(X_test)
    vex_test = vec_to_captcha(result[0])
    return vex_test
def vec_to_captcha(vec):
    text = []
    vec[vec < 0.5] = 0
    char_pos = vec.nonzero()[0]
    for i, ch in enumerate(char_pos):
        text.append(captcha_word[ch % word_class])
    return ''.join(text)
def findLoginData(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    viewstate=soup.find(id="__VIEWSTATE")
    viewstategenerator=soup.find(id="__VIEWSTATEGENERATOR")
    eventval=soup.find(id="__EVENTVALIDATION")
    return viewstate["value"],viewstategenerator["value"],eventval["value"]
def RemoveIntef(img):
    img.setflags(write=1)
    h,w,c=img.shape
    #print(h,w,c)
    for i in range(w):
        for j in range(h):
            if(img[j][i][3]!=255):
                img[j][i][0]=0
                img[j][i][1]=128
                img[j][i][2]=0
                img[j][i][3]=255
    return img
def ImgThreshold(img):
    img=np.asarray(img)
    img=RemoveIntef(img)
    img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    _,th = cv2.threshold(img,0,255,\
                         cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    return th
def getVerfcode(cwsession):
    #cwsession=requests.Session()
    r=cwsession.get(homeurl)
    r.encoding="utf8"
    #print(r.text)
    verfcode_loc=re.findall("BaseData/confirm.ashx\?s=+[0-9]*",\
                            r.text)
    print(verfcode_loc[0])
    vcdata=cwsession.get(baseurl+verfcode_loc[0],\
                        stream=True)
    if vcdata.status_code == 200:
        #print("Success Getting Verfcode")
        #print(vcdata.content)
        verfcode_raw=Image.open(BytesIO(vcdata.content))
    return verfcode_raw,r
def login(cwsession,account,password):
    verf_code,r=getVerfcode(cwsession)
    verfimg=Image.fromarray(ImgThreshold(verf_code))
    vfcode=genCode(verfimg)
    print("驗證碼"+vfcode)
    viewstate,vstgen,eventval=findLoginData(r.text)
    payload_login={"txtStuNo":str(account),"txtPSWD":str(password),"txtCONFM":str(vfcode),"__EVENTTARGET":"btnLogin","__EVENTARGUMENT":""\
             ,"__VIEWSTATE":str(viewstate),"__VIEWSTATEGENERATOR":str(vstgen),"__EVENTVALIDATION":str(eventval)}
    r=cwsession.post(homeurl,data=payload_login,stream=True)
    respdata=re.findall("E[0-9]{3}",r.text)
    for repcode in respdata:
        if(repcode=="E064"):
            login_state=0
            print("登入成功")
            break
        else:
            print("登入失敗")
            login_state=1
    return r,login_state
def select(cwsession,r):
    viewstate,vstgen,eventval=findLoginData(r.text)
    payload_select={"__EVENTTARGET":"btnAdd","__EVENTARGUMENT":""\
             ,"__VIEWSTATE":str(viewstate),"__VIEWSTATEGENERATOR":str(vstgen),\
             "__EVENTVALIDATION":str(eventval),"txtCosEleSeq":"0851"}
    r=cwsession.post(actionurl,data=payload_select,stream=True)
    #print(r.text)
    respdata=re.findall("[E,I][0-9]{3}",r.text)
    print(respdata)
    for repcode in respdata:
        if(repcode=="I000"):
            print("加選成功")
            break
        elif(repcode=="E054"):
            print("名額已滿")
        elif(repcode=="E999"):
            print("加選失敗")
            break
    return r
def logout(cwsession,r):
    viewstate,vstgen,eventval=findLoginData(r.text)
    payload_logout={"__EVENTTARGET":"btnLogout","__EVENTARGUMENT":""\
             ,"__VIEWSTATE":str(viewstate),"__VIEWSTATEGENERATOR":str(vstgen),\
             "__EVENTVALIDATION":str(eventval),"txtCosEleSeq":""}
    r=cwsession.post(actionurl,data=payload_logout,stream=True)
    #return r
def main():
    cwsession=requests.session()
    while(1):
        account=input("請輸入帳號:")
        password=input("請輸入密碼:")
        print("帳號:"+account)
        print("密碼:"+password)
        check=int(input("以上資料是否正確? 1:正確,2:錯誤:"))
        if(check==1):
            break
    while(1):
        print("準備進行系統介接")
        print("登入中....")
        login_state=1
        while(login_state):
            r,lgs=login(cwsession,account,password)
            login_state=lgs
        #print(r.text)
        #print(r.text)
        #print(r.headers)
        print("迴圈加選中")
        for i in range(0,35):
            print(str(i+1)+"/"+"35")
            r=select(cwsession,r)
            sleep(2)
        logout(cwsession,r)
main()