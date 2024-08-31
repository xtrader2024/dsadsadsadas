import streamlit as st
import facebook
import schedule
import time
import threading
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import random

# Facebook API erişim jetonunuzu buraya girin
ACCESS_TOKEN = 'your_access_token'
PAGE_ID = 'your_page_id'

# Kitap sözlerini internetten çekme
def fetch_quotes():
    url = 'http://quotes.toscrape.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    quotes = []
    for quote in soup.select('.quote'):
        text = quote.select_one('.text').get_text()
        author = quote.select_one('.author').get_text()
        quotes.append(f'"{text}" — {author}')
        
    return quotes

def get_translated_quote(quote_text):
    translator = Translator()
    translation = translator.translate(quote_text, src='en', dest='tr')
    return translation.text

def get_random_quote():
    quotes = fetch_quotes()
    selected_quote = random.choice(quotes)
    # İngilizce ve Türkçe çevirisini almak
    translated_quote = get_translated_quote(selected_quote)
    return selected_quote, translated_quote

# Facebook API ile bağlantı kurma
graph = facebook.GraphAPI(access_token=ACCESS_TOKEN, version="3.1")

# Streamlit önbellek
if 'posted_quotes' not in st.session_state:
    st.session_state.posted_quotes = []

if 'first_quote' not in st.session_state:
    st.session_state.first_quote = None

def post_to_facebook(message):
    graph.put_object(parent_object=PAGE_ID, connection_name='feed', message=message)
    st.session_state.posted_quotes.append({
        'quote': message,
        'timestamp': datetime.now()
    })
    st.write(f"Paylaşıldı: {message}")

def post_daily_quotes():
    english_quote, turkish_quote = get_random_quote()
    post_to_facebook(english_quote)  # Sadece İngilizce paylaşalım
    return english_quote, turkish_quote

def schedule_posts():
    schedule.every().day.at("09:00").do(post_daily_quotes)
    schedule.every().day.at("18:00").do(post_daily_quotes)

    while True:
        schedule.run_pending()
        time.sleep(1)

def display_initial_quote():
    if st.session_state.first_quote is None:
        english_quote, turkish_quote = get_random_quote()
        st.session_state.first_quote = (english_quote, turkish_quote)
        st.write(f"{english_quote}")
        st.write(f"{turkish_quote}")

# Streamlit arayüzü
st.title('Facebook Kitap Sözleri Botu')

if st.button('Başlat'):
    st.write('Bot başlatıldı.')
    display_initial_quote()
    threading.Thread(target=schedule_posts).start()

# Arşivlenen sözleri göster
st.header('Paylaşılan Sözler')
for quote in st.session_state.posted_quotes:
    st.write(f"**Söz (İngilizce):** {quote['quote']}")
    st.write(f"**Tarih:** {quote['timestamp']}")
    st.write("---")

st.write("Bot, her gün sabah ve akşam saatlerinde otomatik olarak kitap sözleri paylaşacak.")
