from flask import *
import convert
import util




app = Flask(__name__)

@app.route("/")
def upload(): 
   return render_template("file_upload.html")


@app.route("/success", methods=["POST"])
def success():    
    f = request.files["uploadedFile"]
    global uploadedFile
    uploadedFile = f.filename
    f.save(uploadedFile)
    return render_template("success.html", name=uploadedFile)



@app.route("/convert")
def heapMap():             
        isKoc = util.isKoc(uploadedFile)        
        convert.heapMap(uploadedFile, isKoc)
        return render_template("download.html", name=uploadedFile)



@app.route("/download")
def download():
        filename = util.file_decoder(uploadedFile)
        print("download: "+filename)
        return send_file(filename,as_attachment=True)

        
if __name__ == "__main__":
    app.run(debug=True)
