import cgi
import httplib2, argparse, os, sys, json
from oauth2client import tools, file, client
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
from googleapiclient.errors import HttpError

form = cgi.FieldStorage()
searchterm = form.getvalue('skill')

#Project and model configuration
project_id = 'ai-calling'
model_id = 'skills-identifier'

def make_prediction():
	""" Use trained model to generate a new prediction """

	api = get_prediction_api()
	
	print("Fetching model.")

	#model = api.trainedmodels().get(project=project_id, id=model_id).execute()

	#if model.get('trainingStatus') != 'DONE':
	#	print("Model is (still) training. \nPlease wait and run me again!") #no polling
	#	exit()

	#print("Model is ready.")
	
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
	prediction = api.trainedmodels().predict(project=project_id, id=model_id, body={
		'input': {
			'csvInstance': searchterm
		},
	}).execute()

	#retrieve classified label and reliability measures for each class
	#label = prediction.get('outputLabel')
	#stats = prediction.get('outputMulti')

	#show results
	#print("You are currently %s (class %s)." % (labels[label], label) ) 
	#print(stats)
	

def train_model():
	""" Create new classification model """

	api = get_prediction_api()

	print("Creating new Model.")

	api.trainedmodels().insert(project=project_id, body={
		'id': model_id,
		'storageDataLocation': 'ai-calling/PeopleSkills_formatted.csv'
	}).execute()


def get_prediction_api(service_account=True):
	scope = [
		'https://www.googleapis.com/auth/prediction',
		'https://www.googleapis.com/auth/devstorage.read_only'
	]
	return get_api('prediction', scope, service_account)