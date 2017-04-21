# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
from datetime import datetime
import logging
import os
import csv
from flask import Flask, redirect, render_template, request

import httplib2, argparse, sys, json
from oauth2client import tools, file, client
#from oauth2client.contrib.appengine import AppAssertionCredentials
#from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
#from googleapiclient import discovery
import cgi
from googleapiclient.errors import HttpError

#Project and model configuration
project_id = 'ai-calling'
model_id = 'skillspredictions'


app = Flask(__name__)


@app.route('/')
def homepage(skills=None):
    # Create a Cloud Datastore client.
    #datastore_client = datastore.Client()

    # Use the Cloud Datastore client to fetch information from Datastore about
    # each photo.
    #query = datastore_client.query(kind='Faces')
    #image_entities = list(query.fetch())
    # Return a Jinja2 HTML template and pass in image_entities as a parameter.
    # return render_template('homepage.html', image_entities=image_entities)
    return render_template('main.html', skills=skills)


@app.route('/skill_predictor', methods=['GET', 'POST'])
def skill_predictor():
    #skill = request.form['skill']
	#form = cgi.FieldStorage()
	#searchterm = form.getvalue('skill')
	#skill = "Artificial Intelligence"
	""" Use trained model to generate a new prediction """
	#api = get_prediction_api()
	print("Build API")
	
	scopes = ['https://www.googleapis.com/auth/prediction']
	credentials = ServiceAccountCredentials.from_json_keyfile_name('key.json', scopes)

	http = credentials.authorize(httplib2.Http())
	#http = AppAssertionCredentials('https://www.googleapis.com/auth/prediction').authorize(httplib2.Http())	
	service = build('prediction', 'v1.6', http=http)

	"""
	#Optionally analyze model stats (big json!)
	analysis = api.trainedmodels().analyze(project=project_id, id=model_id).execute()
	print(analysis)
	exit()
	"""
	
	#read new record from local file
	skill_list = []
	rating_list = []
	candidate_list = []
	previous_candidate = ""
	with open('testdata_formatted.csv') as f:
		csvreader = csv.reader(f, delimiter=',', quotechar='"')
		for entry in csvreader:
			current_candidate = entry[0]
			if previous_candidate == "":
			#first run
				previous_candidate = current_candidate
				skill_list.append(entry[1])

			if current_candidate == previous_candidate:
				skill_list.append(entry[1])
			else:
				print (skill_list)
				rating = make_predictions(skill_list)
				rating_list.append(current_candidate +" " + str(rating))
				#rating_result['name'] = current_candidate
				#rating_result['rating'] = rating
				print("Name: " + current_candidate + ", Rating: " + str(rating))
				skill_list = []
			previous_candidate = current_candidate
		
	return render_template('main.html', skills=rating_list)

def make_predictions(skill_list):
	print("Build API")
	scopes = ['https://www.googleapis.com/auth/prediction']
	credentials = ServiceAccountCredentials.from_json_keyfile_name('key.json', scopes)
	http = credentials.authorize(httplib2.Http())
	service = build('prediction', 'v1.6', http=http)
	count_ai = 0
	for skill in skill_list:
		print (skill)
		#obtain new prediction LOOP skill list
		prediction = service.trainedmodels().predict(project=project_id, id=model_id, body={
			'input': {
				'csvInstance': [skill]
			},
		}).execute()
	
		#retrieve classified label and reliability measures for each class
		label = prediction.get('outputLabel')
		stats = prediction.get('outputMulti')
		
		print ("Prediction finished")
		#print ("Label: "+label)
		#print ("Reponse: "+stats)	
		# generate prediction score: 1 point for AI skill
		if label == "AI":
			count_ai+=1
		
	return (count_ai/len(skill_list))
	#return render_template('main.html', skills=stats)


""" 
def get_prediction_api(service_account=True):
	scope = [
		'https://www.googleapis.com/auth/prediction',
		'https://www.googleapis.com/auth/devstorage.read_only'
	]
	return get_api('prediction', scope, service_account)
""" 
""" 
def get_api(api, scope, service_account=True):
	Build API client based on oAuth2 authentication
	STORAGE = file.Storage('oAuth2.json') #local storage of oAuth tokens
	credentials = STORAGE.get()
	if credentials is None or credentials.invalid: #check if new oAuth flow is needed
		if service_account: #server 2 server flow
			credentials = ServiceAccountCredentials('service_account.json', scopes=scope)
			STORAGE.put(credentials)
		else: #normal oAuth2 flow
			CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
			FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS, scope=scope)
			PARSER = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[tools.argparser])
			FLAGS = PARSER.parse_args(sys.argv[1:])
			credentials = tools.run_flow(FLOW, STORAGE, FLAGS)

	#wrap http with credentials
	http = credentials.authorize(httplib2.Http())
	return discovery.build(api, "v1.6", http=http)
""" 


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
