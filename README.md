# AI Chatbot Python
Deploying a simple Flask app to the cloud via Heroku

# Install dependecies

```sh
python --version

pip install -r requirements.txt

or 
pip list

pip install flask
pip uninstall flask
pip show flask

```
# To train model

```sh
python train_chatbot.py
```

# Run server

```sh
python app.py
```

You should be able to run this app on your own system via the familiar invocation and visiting [http://localhost:5000](http://localhost:5000).

# To Deploy on [Google colab](https://colab.research.google.com)

Open appColab.ipynb run all script or follow below command.

```sh
python --version
!git clone https://github.com/pritamkhose/Chatbot-Python
cd Chatbot-Python
ls
pip install -r requirements.txt
!python appColab.py
```
You will able to run this app by visiting Running URL somethibng like http://454xxxxxxx.ngrok.io.

# To Deploy on [Gitpod](https://gitpod.io/#https://github.com/pritamkhose/Chatbot-Python)

```sh
python --version
pyenv versions
pyenv install --list
pyenv install 3.8.3
pyenv local 3.8.3
python --version
```
# References
* [Soruce Project](https://data-flair.training/blogs/python-chatbot-project/) and [Code Link](https://data-flair.training/blogs/download-python-chatbot-data-project-source-code/)

* [Flask error handling](https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/)

* [w3schools Python Mongodb](https://www.w3schools.com/python/python_mongodb_getstarted.asp)


