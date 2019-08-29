from flask import *
import convert
import util


uploadedFile = "Koc-Holding-2018-Annual-Report.pdf"  #None

app = Flask(__name__)

@app.route("/")
def upload(): 
   return render_template("file_upload.html")


@app.route("/success", methods=["POST"])
def success():
    global uploadedFile  
    f = request.files["uploadedFile"]
    uploadedFile = f.filename
    f.save(uploadedFile)
    return render_template("success.html", name=uploadedFile)

@app.route("/convert")
def heapMap():
        convert.heapMap(uploadedFile)
        return render_template("download.html", name=uploadedFile)

@app.route("/download")
def download():
        filename = util.file_decoder(uploadedFile)
        return send_file(filename,as_attachment=True)

        
if __name__ == "__main__":
    app.run(debug=True)
