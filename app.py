#import the necessary packages
import os
from warnings import filters
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean
import sqlalchemy

#set up flask and initialize database. 
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#establish uploads table in the database
class Upload(db.Model):
    #id will be an autogenerated index for each video upload
    id = db.Column(db.Integer, primary_key=True)
    #fileName is the title of the video
    fileName = db.Column(db.String(50))
    #author is the creator of the video
    author = db.Column(db.String(16))
    #fileURL is the youtube link of the video which when uploaded becomes formated as 
    #"https://www.youtube.com/embed/"+ the video id of youtube (found after the v= section of the link). 
    # However the user inputs a normal full link [see add()  below for more info]
    fileURL= db.Column(db.String(50))
    #tags will include the audience and subjects of the videos as a concatonated string
    tags= db.Column(db.String(50))
    #description is the brief summary of the social story to be displayed under the video
    description = db.Column(db.String(150))
    #when show_filter is True [default], the video should be displayed under the current filter criteria [see filterSearch() below for more details]
    show_filter= db.Column(db.Boolean)
    #when show_search is True [default], the video should be displayed under the current search terms [see filterSearch() below for more details]
    show_search = db.Column(db.Boolean)

#create the table
db.create_all()

#create and add the following example social story to the table: https://www.youtube.com/watch?v=N8oRz9vbuhY
db.session.add(Upload(fileName='NVA Auditions2', author = 'Sam Ginn, Corin Magee',
                    description = 'A social story that goes through the process of auditioning at New Village Arts Theater',
                    fileURL='https://www.youtube.com/embed/N8oRz9vbuhY',
                    tags= 'youngAdult', show_search=True, show_filter=True))
db.session.commit()

#runs through the table and creates a list of the name, author, url, and description for each video that meats filter and search criteria to be displayed
def checkDisplays():
    displayVids = []
    #query all videos in database
    for video in Upload.query.all():
        #only those videos that can be shown according to both the search and filter criteria are added to the list for display
        if video.show_filter==True and video.show_search==True:
            displayVids.append([video.fileName,video.author,  video.fileURL,video.description])
    return displayVids

#sets all video's filters and searches off [used in FilterSearch()]
def clearSearchFilters():
    for video in Upload.query.all():
        video.show_search = False
        video.show_filter = False
        db.session.commit()

#Home page loading instructions
@app.route('/')
def index():
    #add all videos in the database to the display list, as all searches and filters are empty
    fullDisplay = []
    for video in Upload.query.all():
         fullDisplay.append([video.fileName,video.author, video.fileURL, video.description])
    #load the index.html template, with the full list of videos to display
    return render_template('index.html', vids=fullDisplay)

#Filtering and Searching instructions
@app.route('/filterSearch', methods=['POST', 'GET'])
def filterSearch():
    #reset all show settings to False as a default
    clearSearchFilters()
    #grab the search terms and filters from the corresponding form responses
    searchTerm = request.form["searchterm"]
    cat_filter= request.form["category-filter"]
    aud_filter = request.form["audience-filter"]
    #if there is no search term check the filters
    if searchTerm  == "":
        #if there are no filters in place route the website back to the homepage [show-all default]
        if  cat_filter == "all" and aud_filter == "all":
            return redirect('/')
        #if filters are in place but there is no search term, then all videos should be shown according to search criteria
        for video in Upload.query.all():
            video.show_search = True
    #if there is a search term
    else:
        #go through all videos and mark the ones where the search term is contained in the author,
        # title, and/or description for show according to search criteria
        for video in Upload.query.filter(Upload.author.contains(searchTerm)|
        Upload.fileName.contains(searchTerm) |Upload.description.contains(searchTerm)):
            video.show_search = True
    #if there is no filters, all videos should be shown according to filter criteria
    if cat_filter == "all" and aud_filter == "all":
        for video in Upload.query.all():
            video.show_filter = True
    #if there are filters go through all videos and mark the ones where the filter is applicable for show according to filter criteria
    else:
        for video in Upload.query.filter(Upload.tags.contains(cat_filter) | Upload.tags.contains(aud_filter)):
            video.show_filter = True
    #upload the changes to show-criteria  to the database
    db.session.commit()
    #create the list to display of videos eligible using both search and filter criteria
    displayVids = checkDisplays()
    #load the index.html template,
    return render_template('index.html',vids=displayVids)


#uploads page instructions
@app.route('/uploads', methods=['GET','POST'])
def uploads():
    #load the uploading.html template to gather information for uploads
    return render_template('uploading.html')

#instructions for when the "submit" button is clicked on the uploads page
@app.route('/add', methods=['GET','POST'])
def add():
        #pull the url from the submitted form
        fullURL = request.form["videoURL"]
        #find where the youtube id number begins (and where the generic webpage ends)
        startNumIndex = fullURL.find("v=")
        #if you can't find the id number or if it isn't a youtube link, reject the submission and reroute to uploads page
        if startNumIndex == -1 or "youtube" not in fullURL:
            flash('Not valid URL try again')
            return redirect('/uploads')
        #extract the urlID, based on the v= criteria and concatonate it with the base youtube embeded url
        urlID= "https://www.youtube.com/embed/"+ fullURL[startNumIndex+2:startNumIndex +13]
        #pull the checked-tags and audience from the submitted form
        tagList=request.form.getlist('tags')
        audience = request.form["audience"]
        #add audience to tags
        tags = audience
        #if the audience is everyone, concatonate the full list with tags for search purposes later
        if audience == "all_aud":
            tags = tags + "preschool elementary preteen teenager youngAdult adult senior"
        #for all checked tags, concatonate them with the tags
        for tag in tagList:
            tags = tags +tag
        #create a new database entry in Upload, using the above gathered information
        newUpload = Upload(fileName=request.form['videoName'], author =request.form['author'],description = request.form['description'],fileURL=urlID,
                    tags= tags, show_search=True, show_filter=True)
        #add the new entry to Upload and save the changes
        db.session.add(newUpload)
        db.session.commit()
        #reroute to home page once new entry is saved
        return redirect('/')
        
#howTo Page instructions: Load the howTo.html template (this page is static)        
@app.route('/howTo')
def howTo():
    return render_template("howTo.html")

#resources Page instructions: Load the resourcesPage.html template (this page is currently static but may get subsections)
@app.route('/resourcesPage')
def resourcesPage():
    return render_template("resourcesPage.html")

#Flask boot up commands for deployment
if __name__== "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port,debug= True)

