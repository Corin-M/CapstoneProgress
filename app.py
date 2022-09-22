import os
from warnings import filters
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean
import sqlalchemy

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fileName = db.Column(db.String(50))
    author = db.Column(db.String(16))
    fileURL= db.Column(db.String(50))
    tags= db.Column(db.String(50))
    # errands=db.Column(db.String(16))
    #  emotReg = db.Column(db.String(16))
    audience= db.Column(db.String(50))
    show_filter= db.Column(db.Boolean)
    show_search = db.Column(db.Boolean)



db.create_all()


def checkDisplays():
    displayVids = []
    for video in Upload.query.all():
        if video.show_filter==True and video.show_search==True:
            displayVids.append([video.fileName,video.author, video.fileURL])
    return displayVids

def clearSearchFilters():
    for video in Upload.query.all():
        video.show_search = False
        video.show_filter = False
        db.session.commit


@app.route('/')
def index():
    displayVids = []
    for video in Upload.query.all():
         displayVids.append([video.fileName,video.author, video.fileURL])
    return render_template('index.html', vids=displayVids)


@app.route('/filterSearch', methods=['POST', 'GET'])
def filterSearch():
    clearSearchFilters()
    searchTerm = request.form["searchterm"]
    cat_filter= request.form["category-filter"]
    aud_filter = request.form["audience-filter"]
    if searchTerm  == "":
        if  cat_filter == "all" and aud_filter == "all":
            return redirect('/')
        for video in Upload.query.all():
            video.show_search = True
    else:
        for video in Upload.query.filter(Upload.author.contains(searchTerm)):
            video.show_search = True
        for video in Upload.query.filter(Upload.fileName.contains(searchTerm)):
            video.show_search = True
    if cat_filter == "all" and aud_filter == "all":
        for video in Upload.query.all():
            video.show_filter = True
    else:
        for video in Upload.query.filter(Upload.tags.contains(cat_filter) |Upload.tags.contains(aud_filter)):
            video.show_filter = True
    db.session.commit
    displayVids = checkDisplays()
    return render_template('index.html',vids=displayVids)


@app.route('/uploads', methods=['GET','POST'])
def uploads():
    return render_template('uploading.html')

@app.route('/add', methods=['GET','POST'])
def add():
        fullURL = request.form["videoURL"]
        startNumIndex = fullURL.find("v=")
        if startNumIndex == -1 or "youtube" not in fullURL:
            flash('Not valid URL try again')
            return redirect('/uploads')
        tagList=request.form.getlist('tags')
        tags=""
        for tag in tagList:
            tags = tags +tag
        urlID= "https://www.youtube.com/embed/"+ fullURL[startNumIndex+2:startNumIndex +13]
        newUpload = Upload(fileName=request.form['videoName'], author =request.form['author'],fileURL=urlID, audience=request.form['audience'], 
                   tags= tags, show_search=True, show_filter=True)
        db.session.add(newUpload)
        db.session.commit()
        return redirect('/')
        
@app.route('/howTo')
def howTo():
    return render_template("howTo.html")

if __name__== "__main__":
    db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug= True)

