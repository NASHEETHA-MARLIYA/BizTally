import os
from flask import Flask, render_template, request, jsonify, send_file,redirect
from pymongo import MongoClient
from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator
from InvoiceGenerator.pdf import SimpleInvoice

from random import randint

uri = "mongodb+srv://mohfaiz0504:mohfaiz543@cluster0.nmg1vs4.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri)
db = client["inventory"]
product = db["product"]
order=db["order"]
adm=db["admin"]
stkreq=db["stockreq"]

app = Flask(__name__, template_folder="templates")

def createinvoice(invoicelst,username,phone,address,num):
    #num=randint(1,1000)
    os.environ["INVOICE_LANG"] = "en"

    client = Client(username,phone=phone,address=address)
    provider = Provider('Biz Tally', bank_account='6454-6361-217273', bank_code='2021')
    creator = Creator('Biz Tally')
    invoice = Invoice(client, provider, creator)
    for data in invoicelst:
        invoice.add_item(Item(data["quantity"], data["price"], description=data["name"]))
    invoice.currency = "Rs."
    invoice.number = str(num)
    docu = SimpleInvoice(invoice)
    docu.gen(f"data/{str(num)}.pdf", generate_qr_code=False)
    return str(num)


@app.route("/")
@app.route("/home")
def home():
    sum=0
    spend=0
    for val in order.find():
        sum+=val["totalprice"]
        
    for k in stkreq.find():
        for j in product.find():
            if k["name"]==j["name"]:
                spend+=j["price"]*int(k["stockinc"])
                
    return render_template("dashbord.html",data=order.find(),sum=sum,exp=spend)

@app.route("/admi")
def admi():
    return render_template("admin.html")

@app.route("/login",methods=['POST', 'GET'])
def login():
    user = request.form['username']
    pas = request.form['password']
    for data in adm.find():
        if data["adminName"]==user and data["adminPass"]==pas:
            return redirect('/home')
        elif data["adminName"]==user and data["adminPass"]!=pas:
            return render_template("sign.html",info="Invalid Password")
        else:
            return render_template("sign.html",info="Invalid Username")
    
@app.route("/productpage")
def productpage():  
    return render_template("productpage.html",data=product.find(),stkd=stkreq.find())

@app.route("/buy")
def buy():
    product_list = []
    for data in product.find():
        product_list.append(data["name"])
    #print(product_list)
    return render_template("index.html",data=product.find())

@app.route('/send',methods=['POST'])
def send():
    if request.method == 'POST':
        num=order.count_documents({})+1
        invoicelst=[]
        text = request.json
        upd=text[0]["product"].keys()
        text[0]["_id"]=num
        text[0]["status"]="pending"
        #print(upd)
        for data in product.find():
            if data["name"] in upd:
                res={}
                res["name"]=data["name"]
                res["quantity"]=text[0]["product"][data["name"]]
                res["price"]=data["price"]
                invoicelst.append(res)
                value=(data["stock"]-text[0]["product"][data["name"]])
                product.update_one({"name":data["name"]},{"$set":{"stock":value}})
                
        order.insert_one(text[0])
        mes=createinvoice(invoicelst,text[0]["username"],text[0]["userphoneno"],text[0]["useraddress"],num)
        message={"message":mes}
        return jsonify(message)
@app.route('/download/<string:filename>')
def download(filename):
    path="/home/faiz/Desktop/inventory/data/"+filename+".pdf"
    return send_file(path, as_attachment=True)

@app.route('/addstk',methods=['POST'])
def addstk():
    if request.method == 'POST':
        text = request.json
        print(text)
        result={}
        for pro in product.find():
            if pro["name"]==text[0]["nam"]:
                result["name"]=pro["name"]
                result["stockinc"]=text[0]["stockin"]
                result["status"]="pending"
        print(result)
        stkreq.insert_one(result)
        mess={"message":"Stock requested"}
        return jsonify(mess)
    
@app.route("/analytics")
def analytics():
    return render_template('analytics.html',data=product.find())
        
        


if __name__ == "__main__":
    app.run(debug=True)
