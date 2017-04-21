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

from flask import Flask, redirect, render_template, request

import httplib2, argparse, sys, json
from oauth2client import tools, file, client
from oauth2client.appengine import AppAssertionCredentials
from apiclient.discovery import build
#from oauth2client.service_account import ServiceAccountCredentials
#from googleapiclient import discovery
import cgi
from googleapiclient.errors import HttpError

#Project and model configuration
project_id = 'ai-calling'
model_id = 'skillspredictions'


app = Flask(__name__)


@app.route('/')
def homepage():
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Use the Cloud Datastore client to fetch information from Datastore about
    # each photo.
    query = datastore_client.query(kind='Faces')
    image_entities = list(query.fetch())

    # Return a Jinja2 HTML template and pass in image_entities as a parameter.
    # return render_template('homepage.html', image_entities=image_entities)
    return render_template('main.html')


@app.route('/skill_predictor', methods=['GET', 'POST'])
def skill_predictor():
    #skill = request.form['skill']
	#form = cgi.FieldStorage()
	#searchterm = form.getvalue('skill')
	#skill = "Artificial Intelligence"
	""" Use trained model to generate a new prediction """
	#api = get_prediction_api()
	print("Build API")
	http = AppAssertionCredentials('https://www.googleapis.com/auth/prediction').authorize(httplib2.Http())	
	service = build('prediction', 'v1.6', http=http)

	"""
	#Optionally analyze model stats (big json!)
	analysis = api.trainedmodels().analyze(project=project_id, id=model_id).execute()
	print(analysis)
	exit()
	"""
	
	#read new record from local file
	#with open('record.csv') as f:
	#	record = f.readline().split(',') #csv

	#obtain new prediction
	prediction = service.trainedmodels().predict(project=project_id, id=model_id, body={
		'input': {
			'csvInstance': "Artificial Intelligence"
		},
	}).execute()

	#retrieve classified label and reliability measures for each class
	label = prediction.get('outputLabel')
	stats = prediction.get('outputMulti')

	#show results
	print("Prediction is working")
	print(prediction)
	print(label)
	print(stats)

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
