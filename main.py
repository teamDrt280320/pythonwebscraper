import requests                # Include HTTP Requests module
from bs4 import BeautifulSoup  # Include BS web scraping module
import xml.dom.minidom as parser
import json
from flask import Flask,render_template,jsonify,request,Response
import firebase_admin
from firebase_admin import credentials,firestore
import time

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)
firestore_db=firestore.client()
app = Flask(__name__)
#rendering data
@app.route('/fetch')
def fetchData():            
    return render_template('index.html')  

#fetch data from server
@app.route('/progress')
def progress():
    def generate(): 
        abc=parser.parse("sites.xml")
        sites=abc.getElementsByTagName("url")
        result=[]
        i=1

        ##
        delete_collection(firestore_db.collection('coupons'), 100)

        ##
        for site in sites:
            for loc in site.getElementsByTagName("loc"):
                url = loc.firstChild.nodeValue 
                resultobj={'coupon':[]}
                r = requests.get(url)          
                soup = BeautifulSoup(r.text, "html.parser")
                imgsrc=soup.find_all('div',{'class':'gm-mri'})[0].find_all('img')[0]['src']
                title=soup.find_all('div',{'class':'gm-mrd'})[0].find_all('h1')[0].text
                resultobj['name']=title
                resultobj['logo']=imgsrc
                abc=soup.find_all('li')
                abcde=soup.find_all('div',{"class":'gc-box banko'})
                for a in abcde:
                    couponobj={}
                    discount=a.find_all('div',{'class':'bank'})[0].find_all('span')[0].text
                    desc=a.find_all('p')[0].text
                    b=a.find_all('span',{'class':'cbtn'})
                    for c in b:
                        couponCode=c.find_all('span','visible-lg')[0].text
                        if couponCode!='ACTIVATE OFFER':
                            couponobj['dicount']=discount
                            couponobj['description']=desc
                            couponobj['couponcode']=couponCode
                            resultobj['coupon'].append(couponobj)
                resultobj['totalcoupons']=len(resultobj['coupon']) 
                resultobj['link']=url        
                firestore_db.collection('coupons').add(resultobj)
                print('finished'+str(i)+'Website')
                i=i+1
                yield "data:" + str(int(round((i/len(sites))*100))) + "\n\n"
                yield "title:" + 'Fetching Data' + "\n\n"
                if(i==1):
                    break
        ##        
    return Response(generate(), mimetype= 'text/event-stream')

#delete previous data
def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0
    for doc in docs:
        doc.reference.delete()
        deleted = deleted + 1
    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

@app.route('/')
def start():
    return {"statucode":200,"message":"Go to /fetch for updating databse"}        

if __name__=='__main__':
    app.run()