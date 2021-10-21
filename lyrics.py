import configparser
import requests
import os
import re
from bs4 import BeautifulSoup

def getAccessToken():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['Client_Access_Token']['token']

token = getAccessToken()

def searchMusicArtist(name):
    api_url = f'https://api.genius.com/search?q={name}'
    headers = {'authorization': token}
    r = requests.get(api_url, headers=headers)
    return r.json()

def getArtistID(name):
    r = searchMusicArtist(name)
    id = r['response']['hits'][0]['result']['primary_artist']['id']
    return id 

def getTopTenSongs(name):
    id = getArtistID(name)
    api_url = f'https://api.genius.com/artists/{id}/songs'
    headers = {'authorization': token}
    params = {
        'sort':'popularity',
        'per_page':10
    }
    r = requests.get(api_url, headers=headers, params=params)
    return r.json()

def getLyricsArray(name):
    r = getTopTenSongs(name)
    songs = r['response']['songs']
    lyrics_array = [song['url'] for song in songs]
    return lyrics_array

def scrapeLyricText(name):
    links = getLyricsArray(name)
    song_lyrics = [] 

    for link in links:

        page = requests.get(link)    
        soup = BeautifulSoup(page.content, "html.parser") # Extract the page's HTML as a string
        # Scrape the song lyrics from the HTML
        lyrics = soup.find(class_="lyrics")
        if lyrics is not None:
            # print(link)
            anchor_tags = lyrics.find_all('a')
            curr_lyrics = []
            for anchor in anchor_tags:
                if len(anchor) > 0 and anchor.text[0] != '[':
                    text = anchor.text.replace('\n', 'NEWLINE')
                    curr_lyrics.append(text)
            song_lyrics.append(curr_lyrics)
        else:
            pass
    
    return song_lyrics
