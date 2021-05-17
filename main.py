import requests                # Include HTTP Requests module
from bs4 import BeautifulSoup  # Include BS web scraping module
import xml.dom.minidom as parser
import json
from flask import Flask,render_template,jsonify,request,Response
import firebase_admin
from firebase_admin import credentials,firestore
import time

app = Flask(__name__)
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)
firestore_db=firestore.client()


#rendering data
@app.route('/top-coupons')
def fetchTopCoupons():
    coupon={'coupons':[]}
    url='https://www.grabon.in/'
    r = requests.get(url)          
    delete_collection(firestore_db.collection('topcoupons'), 100)
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all('div',{'class':'g-htop-c show'}):
        for b in a.find_all('div','gh-ec'):
            topcpnobj={}
            discount=b.find_all('div',{'class':'amt go-cpn-show'})[0].find_all('span')[0].text
            imgsrc=b.find_all('a',{'class':'imw go-redir-here'})[0].find_all('img')[0]['data-original']
            description=b.find_all('p',{'class':'go-cpn-show'})[0].text
            id=b.find_all('p',{'class':'go-cpn-show'})[0]['data-goid']
            topcpnobj['id']=id
            topcpnobj['imgsrc']=imgsrc
            topcpnobj['discount']=discount
            topcpnobj['description']=description
            coupon['coupons'].append(topcpnobj)
            # print(coupon)
    firestore_db.collection('topcoupons').add(coupon)
    return jsonify(coupon)


#fetch top Stores
@app.route('/top-stores')
def fetchTopStores():
    url='https://www.grabon.in/'
    r = requests.get(url)          
    soup = BeautifulSoup(r.text, "html.parser")
    topcpnimgsrcs=soup.find_all('a',{'class':'go-popstore'})
    delete_collection(firestore_db.collection('topproducts'), 100)
    for topcpnimgsrc in topcpnimgsrcs:
        topcpnobj={}
        topcpnobj['storeurl']=topcpnimgsrc['href']
        topcpnobj['logosrc']=topcpnimgsrc.find('img')['data-original']
        firestore_db.collection('topproducts').add(topcpnobj)
        
    #print(topcpnimgsrc)
    return {'statuscode':'200','message':'done'}


#rendering category index html
@app.route('/fetchCategories')
def fetchCategoryData():            
    return render_template('index2.html') 



#Fetch Categories
@app.route('/progress2')
def fetchCategories():
    def generate():
        abc=parser.parse("category.xml")
        sites=abc.getElementsByTagName("url")
        result=[]
        i=1
        ##
        delete_collection(firestore_db.collection('categories'), 100)
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
                abcde=soup.find_all('ul',{"class":'gmc-list list-unstyled'})
                # print(len(abcde))
                for a in abcde:
                    lilist = a.find_all('div',{'class':'gc-box ct'})
                    for li in lilist:
                        id=li.find_all('div',{'class':'gcbr go-cpn-show go-cpy'})[0]['data-goid']
                        logo=li.find_all('div',{'class':'gcbr go-cpn-show go-cpy'})[0].find_all('div',{'class':'bank'})[0].find_all('span')[0].find_all('img')[0]['src']
                        if logo=='data:image/png;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=':
                            logo=li.find_all('div',{'class':'gcbr go-cpn-show go-cpy'})[0].find_all('div',{'class':'bank'})[0].find_all('span')[0].find_all('img')[0]['data-original']
                        discount=li.find_all('div',{'class':'gcbr go-cpn-show go-cpy'})[0].find_all('div',{'class':'bank'})[0].find_all('span')[1].text
                        desc=li.find_all('div',{'class':'gcbr go-cpn-show go-cpy'})[0].find_all('p')[0].text
                        couponCode=li.find_all('div',{'class':'gcbr go-cpn-show go-cpy'})[0].find_all('div',{'class':'gcbr-r'})[0].find_all('span',{'class':'cbtn'})[0].find_all('span',{'class':'visible-lg'})[0].text
                        couponobj={}
                        if couponCode!='ACTIVATE OFFER':
                            couponobj['dicount']=discount
                            couponobj['id']=id
                            couponobj['description']=desc
                            couponobj['couponcode']=couponCode
                            couponobj['merchatlogo']=logo
                            resultobj['coupon'].append(couponobj)
                resultobj['totalcoupons']=len(resultobj['coupon']) 
                resultobj['link']=url        
                firestore_db.collection('categories').add(resultobj)
                print('finished'+str(i)+'Website')
                i=i+1
                yield "data:" + str(int(round((i/len(sites))*100))) + "\n\n"
                yield "title:" + 'Fetching Data' + "\n\n"
                
        ##        
    return Response(generate(), mimetype= 'text/event-stream')




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
                        id=a.find_all('div',{'class':'gcbr go-cpn-show go-cpy'})[0]['data-goid']
                        couponCode=c.find_all('span','visible-lg')[0].text
                        if couponCode!='ACTIVATE OFFER':
                            couponobj['dicount']=discount
                            couponobj['id']=id
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