# https://data-flair.training/blogs/download-python-chatbot-data-project-source-code/
# https://data-flair.training/blogs/python-chatbot-project/

# libraries
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
import json
import random
from datetime import datetime
from flask import Flask, Response, request, jsonify, render_template
from flask_cors import CORS

from keras.models import load_model
import nltk
nltk.download('punkt')
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return render_template("index.html")


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


def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag'] == tag):
            result = random.choice(i['responses'])
            break
    try:
        if(i['context'][0] != ""):
            result = getAction(tag, i['context'][0], result)
    except KeyError:
        print()
    return result


def getAction(tag, context, responses):
    if(context == 'currentDateTime'):
        return responses + str(datetime.now().strftime("%c"))
    else:
        return responses


def chatbot_predict(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res

# Error Handling


@ app.errorhandler(404)
def page_not_found(e):
    data = {'time': str(datetime.now().strftime("%c")), 'errorMsg': str(e)}
    return jsonify(data), 404


# Flask server invoke
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
