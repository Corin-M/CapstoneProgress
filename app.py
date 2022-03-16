import os
from base64 import urlsafe_b64decode
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = 'templates/uploads'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
db = SQLAlchemy(app)

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    fileurl= db.Column(db.String(50))
db.create_all()

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        upload = Upload(filename=file.filename, fileurl=(app.config['UPLOAD_FOLDER']+file.filename))
        db.session.add(upload)
        db.session.commit()
    displayVids = []
    for file in Upload.query.all():
        displayVids.append(file)
    return render_template('index.html', vids=displayVids)



if __name__== "__main__":
    db.create_all()
    
    app.run(debug = True)
