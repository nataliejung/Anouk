from flask import *
import convert

uploadedFile = None

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
        return render_template("download.html")

@app.route("/download")
def download():
        filename = convert.file_decoder(uploadedFile)
        return send_file(filename,as_attachment=True)


        
if __name__ == "__main__":
    app.run(debug=True)
