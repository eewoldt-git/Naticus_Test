# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 16:32:25 2020

@author: Akshay Mathur
"""

from flask import Flask, request, jsonify, render_template
import joblib
import traceback, os
import pandas as pd
import jinja2
from androguard.core.bytecodes.apk import APK



'''Initializing FLASK and index.html'''
app = Flask(__name__)
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),autoescape=True)



'''Initializing the "uploads" folder'''
uploads_dir = os.path.join(app.instance_path, 'uploads')
os.makedirs(uploads_dir, exist_ok = True)



'''Starting point of Web App, shows the "Home" page'''
@app.route('/')
def index():
   return render_template('index.html')



'''
This is the main part of the App.
It recieves the uploaded apk file, saves it in the "uploads folder",
Fetches the apk from the "uploads folder", calls the "create_perm_vector" function,
calls the "classify" function, removes the uploaded file, and displays the result.
'''
@app.route('/upload', methods = ['POST'])
def upload_file():
   if request.method == 'POST':
       try:
           f = request.files['file']
           f.save(os.path.join(uploads_dir,f.filename))
           
           
           if(uploads_dir != None):
               apk_file_directory = uploads_dir
               if(not os.path.exists(apk_file_directory)):
                   print('%s does not exist' % apk_file_directory)
               else:
                   for root, dir, files in os.walk(apk_file_directory):
                       apk_file_list = [os.path.join(root, file_name) for file_name in files]
                      
               apk = apk_file_list.pop()

               permission_vector = create_perm_vector(apk)

               result = classify(permission_vector)
              
               os.remove(uploads_dir+"\\"+f.filename)

           return jsonify(result)
       except:
           return jsonify({'trace': traceback.format_exc()})
   else:
      return jsonify({'Result': 'file not uploaded'})



'''
This function takes the apk file as arguments, and creates a permission vector for the model
'''
def create_perm_vector(apk_file):
    try:
	    a = APK(apk_file)
    except:
        return None
    perms = a.get_permissions()
    for permission in PERMISSIONS:
        hit = 1 if permission in perms else 0
        perm_vector.append(hit)
    
    return list(perm_vector)



'''
This function creates the json file, passes the permission vector to the model,
and yeilds whether an app is benign or malicious
'''
def classify(query):
    if model:
        try:
            json_ = request.json
            print(json_)
            #query = pd.get_dummies(pd.DataFrame(json_))
            
            #query = [[0,0,1,0,1,0,0,1,1,0,0,1,0,0,0,1,0,0,0,1,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1,1,1,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0]]
            query = [query]
            query = pd.DataFrame(query, columns = model_columns)
            
            classification = model.predict(query)
            if classification == 0:
                category = 'Benign'
            else:
                category = 'Malware'
                
            return category
        
        except:
            str = {'trace': traceback.format_exc()}
            return str
    else:
        return ('No model here to use')



'''
The main function initializes the ports for the server, loads the model and variables, and runs the server.
'''
if __name__ == '__main__':    
    try:
        port = int(sys.argv[1]) # This is for a command-line input
    except:
        port = 12345 # If you don't provide any port the port will be set to 12345

    model = joblib.load("Naticus.pkl") # Load "model.pkl"
    print ('Model loaded')
    model_columns = joblib.load("Naticus_columns.pkl") # Load "model_columns.pkl"
    print ('Model columns loaded')
    PERMISSIONS = model_columns
    v = len(PERMISSIONS)
    perm_vector = [] * v
#    app.run(host='192.168.1.242',port=port)    
    app.run(port=port)    