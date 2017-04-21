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
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import cgi
from googleapiclient.errors import HttpError
#from google.appengine.api import mail

#Project and model configuration
project_id = 'ai-calling'
model_id = 'skillspredictions'


app = Flask(__name__)


@app.route('/')
def homepage(skills=None):
    # render homepage with skills parameter
    return render_template('main.html', skills=skills)

@app.route('/skill_predictor', methods=['GET', 'POST'])
def skill_predictor():
	
	print("Build API")
	
	scopes = ['https://www.googleapis.com/auth/prediction']
	credentials = ServiceAccountCredentials.from_json_keyfile_name('key.json', scopes)

	http = credentials.authorize(httplib2.Http())	
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

@app.route('/send_to_bot', methods=['GET', 'POST'])
def contact_candidate():
	sender_address = "Karl Müller <zlatko.beg89@gmail.com>"
	recipientadress = "Zlatko Avdagic <zlatko.avdagic@accenture.com>"
	recipientname = "Zlatko"

	message =  google.appengine.api.mail.EmailMessage(sender=sender_address, subject="Invitation to Skype Interview for AI Project")
	message.to = recipientadress
	message.body = """Dear """ + recipientname + """: You have been selected as potential candidate for a new AI project. We would like to invite to a short Skype interview to evaluate your potential.To start the interview please click on the link below:
{https://bot.api.ai/c4cde66f-4cc8-4406-8475-b1d7bcd50b05 }

Best regards,
Karl

"""
	message.send()


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
