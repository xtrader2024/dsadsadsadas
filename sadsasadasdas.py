import streamlit as st
import requests
from bs4 import BeautifulSoup

# Amazon scraper fonksiyonu
def get_amazon_deals():
    url = "https://www.amazon.com.tr/gp/goldbox"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return [{"title": "Sayfa alınamadı", "price": "", "link": ""}]

    soup = BeautifulSoup(response.content, "html.parser")
    deals = []

    for item in soup.select(".DealContent"):
        title_tag = item.select_one(".DealTitle")
        price_tag = item.select_one(".PriceBlock .price")
        link_tag = item.select_one("a")

        title = title_tag.get_text(strip=True) if title_tag else "Başlıksız"
        price = price_tag.get_text(strip=True) if price_tag else "Fiyat bilgisi yok"
        link = "https://www.amazon.com.tr" + link_tag["href"] if link_tag else "#"

        deals.append({
            "title": title,
            "price": price,
            "link": link
        })

    return deals

# Streamlit arayüzü
st.set_page_config(page_title="Anlık Kampanyalar", layout="wide")
st.title("Anlık Kampanya ve İndirimler")
st.markdown("Şu an sadece **Amazon Türkiye** üzerinden veri çekiliyor. Yakında diğer siteler eklenecek.")

if st.button("Amazon Kampanyalarını Göster"):
    with st.spinner("Kampanyalar yükleniyor..."):
        deals = get_amazon_deals()
        for deal in deals:
            st.markdown(f"""
                ### {deal['title']}
                **Fiyat:** {deal['price']}  
                [Ürüne Git]({deal['link']})  
                ---
            """)
