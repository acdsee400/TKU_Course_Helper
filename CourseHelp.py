import shutil
import requests
import re
import json
from bs4 import BeautifulSoup
from time import sleep
captcha_word = "_0123456789"
word_class=len(captcha_word)
account=""
password=""
baseurl="http://www.ais.tku.edu.tw/EleCos/"
homeurl=baseurl+"login.aspx"
actionurl=baseurl+"action.aspx"
verfurl=baseurl+"Handler1.ashx"
def findLoginData(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    viewstate=soup.find(id="__VIEWSTATE")
    viewstategenerator=soup.find(id="__VIEWSTATEGENERATOR")
    eventval=soup.find(id="__EVENTVALIDATION")
    return viewstate["value"],viewstategenerator["value"],eventval["value"]
def getVerfcode(cwsession):
    looktable={"cfcd208495d565ef66e7dff9f98764da":"0",\
    "c4ca4238a0b923820dcc509a6f75849b":"1",\
    "c81e728d9d4c2f636f067f89cc14862c":"2",\
    "eccbc87e4b5ce2fe28308fd9f2a7baf3":"3",\
    "a87ff679a2f3e71d9181a67b7542122c":"4",\
    "e4da3b7fbbce2345d7772b0674a318d5":"5",\
    "1679091c5a880faf6fb5e6087eb1b2dc":"6",\
    "8f14e45fceea167a5a36dedd4bea2543":"7",\
    "c9f0f895fb98ab9159f51fd0297e236d":"8",\
    "45c48cce2e2d7fbdea1afc51c7c6ad26":"9"}
    r=cwsession.get(homeurl)
    r.encoding="utf8"
    vcdata=cwsession.get(verfurl)
    if vcdata.status_code == 200:
        vc_array=json.loads(vcdata.text)
        vc_ans=[]
        for raw_num in vc_array:
            vc_ans.append(looktable[str(raw_num)])
        verfcode_raw="".join(vc_ans)
    return verfcode_raw,r
def login(cwsession,account,password):
    vfcode,r=getVerfcode(cwsession)
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
def select(cwsession,r,selct_num):
    print("正在加選:"+str(selct_num))
    viewstate,vstgen,eventval=findLoginData(r.text)
    payload_select={"__EVENTTARGET":"btnAdd","__EVENTARGUMENT":""\
             ,"__VIEWSTATE":str(viewstate),"__VIEWSTATEGENERATOR":str(vstgen),\
             "__EVENTVALIDATION":str(eventval),"txtCosEleSeq":str(selct_num)}
    r=cwsession.post(actionurl,data=payload_select,stream=True)
    #print(r.text)
    respdata=re.findall("[E,I][0-9]{3}",r.text)
    #print(respdata)
    while(1):
        for repcode in respdata:
            if(repcode=="I000"):
                print("加選成功")
            if(repcode=="E054"):
                print("名額已滿")
            if(repcode=="E045"):
                print("重複加選")
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
    sel_array=[]
    print("請輸入你想選的課程編號,輸入完成後請輸入0")
    while(1):
        sel_num=input("課程編號:")
        if(sel_num=="0"):
            print("以下是否為你想選的課程編號?")
            print(sel_array)
            sel_chk=input("確認? 1:正確 ,2:錯誤:")
            if(sel_chk=="1"):
                break
            else:
                #print("Clear Array")
                sel_array=[]
        else:
            sel_array.append(sel_num)
            print("已輸入編號:"+str(sel_num))
    while(1):
        print("準備進行系統介接")
        print("登入中....")
        login_state=1
        while(login_state):
            r,lgs=login(cwsession,account,password)
            login_state=lgs
        print("迴圈加選中")
        for i in range(0,35):
            print(str(i+1)+"/"+"35")
            for sel_send in sel_array:
                r=select(cwsession,r,sel_send)
            sleep(2)
        logout(cwsession,r)
main()