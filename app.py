import requests
from flask import *
from flask_cors import CORS
from bs4 import BeautifulSoup
from pymongo import MongoClient
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

client = MongoClient("mongodb+srv://hari:hari@cluster0.1socvoq.mongodb.net/")
db = client['movierulz']
collection=db['movierulz_urls']
getUrl=collection.find()[0]["url"]

def scape_link(url:str)->str:
    req = requests.get(url).content
    soup = BeautifulSoup(req,"html.parser")
    link = soup.find("a",{"class":"main-button dlbutton"})['href']
    return link 


def get_page(url:str)->list:
    req = requests.get(url).content
    soup = BeautifulSoup(req,"html.parser")
    divs = soup.find_all("div",class_="cont_display")
    data = []
    for i in range(2,len(divs)):
        title = divs[i].find("a")
        img = divs[i].find("img")
        dat = {"title":title['title'],"image":img['src'],"link":title['href']}
        data.append(dat)
    return data
def get_movie(url:str,check=False)->dict:
    if check:
        try:
            req = requests.get(url).content
            soup = BeautifulSoup(req,"html.parser")
            title = soup.find("h2",class_="entry-title").text.replace("Full Movie Watch Online Free","")
            image = soup.find("img",class_="attachment-post-thumbnail size-post-thumbnail wp-post-image")['src']
            description = soup.find_all("p")[2].text
            cast=soup.find_all("p")[1].text
            torrents = soup.find_all("a",class_="mv_button_css")
            print(len(torrents))
            torrent = []
            other_links = []
            for tor in torrents:
                link = tor['href']
                size = tor.find_all("small")[0].text[:tor.find_all("small")[0].text.find("b")+1]
                quality = tor.find_all("small")[0].text[tor.find_all("small")[0].text.find("b")+1:]
                data = {"magnet":link,"size":size,"quality":quality}
                torrent.append(data)
            ps = soup.find_all("p")
            data = {"status":True,"url":url,"title":title,"description":description,"image":image,"torrent":torrent,"other_links":[],"cast":cast}
            # data = {"status":True,"url":"https://media.istockphoto.com/id/185590965/photo/yellow-rubber-duck-for-bath-time.jpg?s=612x612&w=0&k=20&c=QoT-O5jbOugCgdQhLat15c0L9jCmRrSTiO9U50W_eQc=","title":"Server Has been Stopped","description":"No Description","image":"https://media.istockphoto.com/id/185590965/photo/yellow-rubber-duck-for-bath-time.jpg?s=612x612&w=0&k=20&c=QoT-O5jbOugCgdQhLat15c0L9jCmRrSTiO9U50W_eQc=","torrent":[],"other_links":[],"cast":"cast"}
        except Exception as e :
            print(e)
            data = {"status":True,"url":"https://media.istockphoto.com/id/185590965/photo/yellow-rubber-duck-for-bath-time.jpg?s=612x612&w=0&k=20&c=QoT-O5jbOugCgdQhLat15c0L9jCmRrSTiO9U50W_eQc=","title":"Server Has been Stopped","description":"No Description","image":"https://media.istockphoto.com/id/185590965/photo/yellow-rubber-duck-for-bath-time.jpg?s=612x612&w=0&k=20&c=QoT-O5jbOugCgdQhLat15c0L9jCmRrSTiO9U50W_eQc=","torrent":[],"other_links":[],"cast":"cast"}
            
        return data
    else:
        print("check failed")
        data = {"status":True,"url":"https://media.istockphoto.com/id/185590965/photo/yellow-rubber-duck-for-bath-time.jpg?s=612x612&w=0&k=20&c=QoT-O5jbOugCgdQhLat15c0L9jCmRrSTiO9U50W_eQc=","title":"Server Has been Stopped","description":"No Description","image":"https://media.istockphoto.com/id/185590965/photo/yellow-rubber-duck-for-bath-time.jpg?s=612x612&w=0&k=20&c=QoT-O5jbOugCgdQhLat15c0L9jCmRrSTiO9U50W_eQc=","torrent":[],"other_links":[],"cast":"cast"}
        return data


@app.route("/search",methods=["GET"])
def search():
    a = request.args.get("query")
    page=request.args.get("p")
    url = f"{getUrl}/search_movies/page/{page}?s={a}"
    try:
        data = get_page(url)
        total = len(data)
        main_data = {"status":True,"total_found":total,"url":url,"data":data}
    except:
        main_data = main_data = {"status":False,"msg":"No Data Found"}
    return jsonify(main_data)

@app.route("/<language>/<page>")
def get_home(language:str,page:int):
    page = 1 if page == None else page
    if language == "telugu":
        url = getUrl+"/category/telugu-featured/page/"+str(page)
    elif language == "hindi":
        url = getUrl+"/category/bollywood-featured/page/"+str(page)
    elif language == "tamil":
        url = getUrl+"/category/tamil-featured/page/"+str(page)
    elif language == "malayalam":
        url = getUrl+"/category/malayalam-featured/page/"+str(page)
    elif language == "english":
        url = getUrl+"/category/hollywood-featured/page/"+str(page)
    else:
        url = None
    if url != None:
        data = get_page(url)
        total = len(data)
        main_data = {"status":True,"total_found":total,"url":url,"data":data}
    else:
        main_data = {"status":False}
    return jsonify(main_data)

@app.route("/")
def home():
    try:
        url = getUrl
        data = get_page(url)
        total = len(data)
        main_data = {"status":True,"total_found":total,"url":url,"data":data}
    except:
        main_data = {"status":False,"total_found":0,"url":"","data":{}}
        
    return jsonify(main_data)

@app.route("/fetch",methods=["GET"])
def s():
    a = request.args.get("url")
    req = requests.get(a)
    return req.content

@app.route("/get",methods=["GET"])
def get_s():
    a = request.args.get("url")
    print(a)
    try:
        data = get_movie(a)
        return jsonify(data)
    except Exception as e:
        data = {"status":False,"msg":"Unable to get data","error":e}
        return jsonify(data)

@app.route("/get",methods=["POST"])
def post_s():
    request_data = request.get_json(force=True)
    a = ""
    token=""
    try:
        a=request_data['url']
        token=request_data['token']
        response=requests.post('https://seedr-stream-apis.vercel.app/decryptAuthentication',json={"token":token})
        response_data=response.json()
        if response_data['status']: 
            try:
                data = get_movie(a,True)
                return jsonify(data)
            except Exception as e:
                data = {"status":False,"msg":"Unable to get data","error":e}
                return jsonify(data)
        else:
            return jsonify({"message": response_data['message'],"logout_status":True})
    except:
        return jsonify({"message":"cannot find url"})
        
    

if __name__ == "__main__":
    app.run(debug=True)
