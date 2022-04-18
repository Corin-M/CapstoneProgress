import os
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fileName = db.Column(db.String(50))
    fileURL= db.Column(db.String(50))
    tags= db.Column(db.String(50))
  #  medical= db.Column(db.String(16))
   # errands=db.Column(db.String(16))
  #  emotReg = db.Column(db.String(16))
    audience= db.Column(db.String(50))

db.create_all()

@app.route('/')
def index():
    displayVids = []
    for video in Upload.query.all():
        displayVids.append([video.fileName,video.fileURL])
    return render_template('index.html', vids=displayVids)

@app.route('/filter', methods=['POST'])
def filter():
    displayVids = []
    filter=request.form['filter-method']
    if filter == "all":
      return redirect('/')
    else:
        for video in Upload.query.filter(Upload.tags.contains(filter)):
            displayVids.append([video.fileName,video.fileURL])
    return render_template('index.html', vids=displayVids)

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
        newUpload = Upload(fileName=request.form['videoName'], fileURL=urlID, audience=request.form['audience'], 
                   tags= tags)
      #  newUpload = Upload(fileName=request.form['videoName'], fileURL=urlID, audience=request.form['audience'], 
      #                      school = request.form['school'],
      #                      medical= request.form['medical'],
      #                      errands= request.form['errands'],
      #                      emotReg=request.form['emotReg'])
        db.session.add(newUpload)
        db.session.commit()
        return redirect('/')
        
@app.route('/howTo')
def howTo():
    return render_template("howTo.html")

if __name__== "__main__":
    db.create_all()
    
    app.run(debug = True)
