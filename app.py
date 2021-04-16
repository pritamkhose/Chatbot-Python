# https://data-flair.training/blogs/download-python-chatbot-data-project-source-code/
# https://data-flair.training/blogs/python-chatbot-project/

# libraries
import os
from dotenv import load_dotenv
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
import json
import random
from datetime import datetime
from flask import Flask, Response, request, jsonify, render_template
from flask_cors import CORS
from flask_ngrok import run_with_ngrok
import requests

from keras.models import load_model
import nltk
nltk.download('punkt')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

# Load env file
load_dotenv(os.path.join('.env'))
GoogleCoLab = os.environ.get('GoogleCoLab')
if(GoogleCoLab != None and GoogleCoLab == "True"):
    GoogleCoLab = True
else:
    GoogleCoLab = False
print('GoogleCoLab is setup -->', GoogleCoLab)

app = Flask(__name__)
CORS(app)
if(GoogleCoLab):
    run_with_ngrok(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/viewtraindata")
def viewTrainData():
    return render_template("viewtraindata.html")


@app.route("/index")
def index():
    the_time = datetime.now().strftime("%c")
    return """
    <h1>Welcome to AI Chatbot!</h1>
    <p>It is currently {time}.</p>
    """.format(time=the_time)


@ app.route('/postman', methods=['GET'])
def postmanAPI():
    # Read json file in folder
    return json.load(open('ChatbotPython.postman_collection.json'))

# use VS code plugin Prettier - Code formatter for intents.json


@ app.route('/traindata', methods=['GET'])
def trainDataAPI():
    return json.load(open('intents.json'))


# chat initialization
isModelLoaded = False
try:
    model = load_model('chatbot_model.h5')
    intents = json.loads(open('intents.json').read())
    words = pickle.load(open('words.pkl', 'rb'))
    classes = pickle.load(open('classes.pkl', 'rb'))

    isModelLoaded = True
except Exception as e:
    isModelLoaded = False


@app.route("/get", methods=["POST"])
def chatbot_response():
    msg = request.form["msg"]
    try:
        if(isModelLoaded):
            return jsonify({'msg': chatbot_predict(msg), 'error': False}), 200
        else:
            return jsonify({'msg': 'Opps! Model not yet started, Please Wait!', 'error': True}), 200
    except Exception as e:
        errRes = {'time': str(datetime.now().strftime("%c")), 'error': True,
                  'msg': 'Opps! Something went Wrong! Error is =' + str(e), 'errorMsg': str(e)}
        return jsonify(errRes), 200


def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(
        word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence


def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return(np.array(bag))


def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(ints, intents_json, msg):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag'] == tag):
            result = random.choice(i['responses'])
            break
    try:
        result = getAction(tag, i['context'][0], result, msg)
    except KeyError:
        print()
    return result


def getAction(tag, context, responses, msg):
    if(tag == 'currentDateTime'):
        return responses + str(datetime.now().strftime("%c"))
    elif(tag == 'locationWeather'):
        if(len(getLocaton(msg)) > 0):
            return fetchWeatherAPI(getLocaton(msg)[0], responses)
        else:
            return 'Please provide proper location name with case sensitivity!'
    else:
        return responses


def getLocaton(line):
    sentences = nltk.sent_tokenize(line)
    tokenized_sentences = [nltk.word_tokenize(
        sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence)
                        for sentence in tokenized_sentences]
    chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)
    entities = []
    for tree in chunked_sentences:
        entities.extend(extract_entity_names(tree))
    return entities


def extract_entity_names(t):
    entity_names = []
    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))
    return entity_names


def fetchWeatherAPI(loc, responses):
    url = 'https://api.weatherapi.com/v1/current.json?key=' + \
        os.environ.get('WEATHERAPI')+'&q='+loc+'&aqi=no'
    data = requests.get(url)
    if(data.status_code == 200):
        data = data.json()
        res = responses + ' ' + loc + ' is ' + (data['current']['condition']['text'] +
                                                ', ' + str(data['current']['feelslike_c']) + '°C at Temperature, ' +
                                                ' Humidity at ' + str(data['current']['humidity']) + '%' +
                                                ' and Wind waves nearly ' +
                                                str(data['current']
                                                    ['wind_kph']) + 'km/h.'
                                                )
    elif(data.status_code == 400):
        res = "No matching location found!"
    elif(data.status_code == 401):
        res = "Sorry! WEATHER API key is invalid or not provided at .env file."
    else:
        res = "Opps! Something went wrong!"
    return res


def chatbot_predict(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents, msg)
    return res

# Error Handling


@ app.errorhandler(404)
def page_not_found(e):
    data = {'time': str(datetime.now().strftime("%c")), 'errorMsg': str(e)}
    return jsonify(data), 404


# Flask server invoke
if __name__ == '__main__':
    if(GoogleCoLab):
        app.run()
    else:
        app.run(debug=True, use_reloader=True)
