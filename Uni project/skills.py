import os, webbrowser, sys, requests, subprocess, pyttsx3
import datetime
from api_key import API_TOKEN
from uni import main
import words

now = datetime.datetime.now()
engine = pyttsx3.init()
engine.setProperty('rate', 180)

def speaker(text):
    engine.say(text)
    engine.runAndWait()


def greeting():
    print(greeting)


def weather():
    try:
        params = {'q': 'Ryazan', 'units': 'metric', 'lang': 'ru', 'appid': 'f5cff91b9fcb6232c03a9cfd9ba0470e'}
        response = requests.get(f'https://api.openweathermap.org/data/2.5/weather', params=params)
        if not response:
            raise
        w = response.json()
        speaker(f"На улице {w['weather'][0]['description']} {round(w['main']['temp'])} градусов")

    except:
        speaker('Произошла ошибка при попытке запроса к ресурсу API, проверь код')


def morning():
    print(morning)


def night():
    print(night)


def browser():
    webbrowser.open('https://google.com', new=2)


def time():
    print(time)


def disabling():
    sys.exit()


def anime():
    webbrowser.open('https://animego.org', new=2)


def manga():
    webbrowser.open('https://mangalib.me/?section=home-updates', new=2)

def youtube():
    webbrowser.open('https://www.youtube.com', new=2)


def music():
    webbrowser.open('https://www.youtube.com/watch?v=EgVt4oiAHqM', new=2)


def farewell():
    print(farewell)
    sys.exit()

def sasha():
    print(sasha)