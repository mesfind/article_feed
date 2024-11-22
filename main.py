# Configuration parameters
RSS_FEEDS = [
    "http://feeds.aps.org/rss/allsuggestions.xml",
    'http://feeds.aps.org/rss/recent/prl.xml',
    "http://feeds.aps.org/rss/recent/prx.xml",
    "http://feeds.aps.org/rss/recent/physics.xml",
    'http://feeds.aps.org/rss/recent/rmp.xml',
    'https://phys.org/rss-feed/physics-news/',
    'https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science',
    'https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=sciadv',
    'https://www.nature.com/nature.rss',
    "https://www.nature.com/natcomputsci.rss",
    "https://www.nature.com/nchem.rss",
    "https://www.nature.com/natmachintell.rss",
    "https://www.nature.com/natrevmats.rss",
    "https://www.nature.com/nphys.rss",
    "https://www.nature.com/natrevchem.rss",
    "https://www.nature.com/natelectron.rss",
    "https://www.nature.com/nnano.rss",
    "https://www.nature.com/nphoton.rss",
    "https://www.nature.com/natrevphys.rss",
    "https://www.nature.com/ncomms.rss",
    "https://www.nature.com/npjcompumats.rss",
    "https://academic.oup.com/rss/site_5332/3198.xml",
    "https://rss.sciencedirect.com/publication/science/20959273",
    "http://feeds.feedburner.com/acs/jacsat",
    "https://pubs.acs.org/action/showFeed?type=axatoc&feed=rss&jc=ancac3",
    "https://onlinelibrary.wiley.com/action/showFeed?jc=15213773&type=etoc&feed=rss",
    "https://pubs.acs.org/action/showFeed?type=axatoc&feed=rss&jc=nalefd",
    "https://www.annualreviews.org/action/showFeed?ui=45mu4&mi=3fndc3&ai=68t8&jc=conmatphys&type=etoc&feed=atom",
    "https://www.annualreviews.org/action/showFeed?ui=45mu4&mi=3fndc3&ai=sy&jc=physchem&type=etoc&feed=atom",
    "https://pubs.acs.org/action/showFeed?type=axatoc&feed=rss&jc=jpclcd",
    'https://www.pnas.org/rss/Physics.xml',
    'https://www.pnas.org/rss/Applied_Physical_Sciences.xml',
    "https://pubs.acs.org/action/showFeed?type=axatoc&feed=rss&jc=jctcce",
    'https://aip.scitation.org/action/showFeed?type=etoc&feed=rss&jc=jcp',
    "http://aip.scitation.org/action/showFeed?type=etoc&feed=rss&jc=apl",
    "https://pubs.aip.org/rss/site_1000043/1000024.xml",
    "http://feeds.aps.org/rss/recent/prxenergy.xml",
    "http://feeds.aps.org/rss/recent/prmaterials.xml",
    "http://feeds.aps.org/rss/recent/prresearch.xml",
    "http://feeds.aps.org/rss/recent/prb.xml",
    "https://pubs.acs.org/action/showFeed?type=axatoc&feed=rss&jc=chreay",
    'http://feeds.feedburner.com/acs/nalefd',
    'http://feeds.feedburner.com/acs/achre4',
    "http://feeds.feedburner.com/physicstodaynews",
    'https://iopscience.iop.org/journal/rss/2632-2153',
    'https://onlinelibrary.wiley.com/action/showFeed?jc=15214095&type=etoc&feed=rss',
    'https://onlinelibrary.wiley.com/action/showFeed?jc=16163028&type=etoc&feed=rss',
    'https://onlinelibrary.wiley.com/action/showFeed?jc=21983844&type=etoc&feed=rss',
    'http://export.arxiv.org/rss/cond-mat',
    'http://export.arxiv.org/rss/physics',
    'https://chemrxiv.org/engage/rss/chemrxiv',
    "https://www.researchsquare.com/rss.xml",
]

import feedparser
import os
from datetime import datetime, timedelta
import re
from github import Github
import pytz
import translators.server as tss
import time
import requests

# Keywords
ML_KEYWORDS = [
    "neural network",
    "deep learning",
    "machine learning",
    "active machine learning",
]

DFT_KEYWORDS = [
    "NONADABATIC",
    "QUANTUM DYNAMIC",
    "TDDFT",
    "TIME DEPENDENT DENSITY",
    "density functional",
]

BATTERY_KEYWORDS = [
    "lithium",
    "battery",
    "electrode",
    "anode",
    "cathode",
    "separator",
]

# WhatsApp Webhook URLs
WHATSAPP_WEBHOOK_ML = os.getenv('WHATSAPP_WEBHOOK_ML')
WHATSAPP_WEBHOOK_DFT = os.getenv('WHATSAPP_WEBHOOK_DFT')
WHATSAPP_WEBHOOK_BATTERY = os.getenv('WHATSAPP_WEBHOOK_BATTERY')

# GitHub configuration
GITHUB_TOKEN = os.getenv('MY_GITHUB_TOKEN')
REPO_NAME = "mesfind/article-feed"
TIMEZONE = pytz.timezone('UTC')

def check_keywords(text, keywords):
    """Check if the text contains any keyword from the given list."""
    if not text:
        return False
    text = text.lower()
    return any(keyword.lower() in text for keyword in keywords)

def get_category(title, description):
    """Determine the category of an article."""
    text = f"{title} {description}".lower()
    
    if check_keywords(text, ML_KEYWORDS):
        return "ML"
    elif check_keywords(text, DFT_KEYWORDS):
        return "DFT"
    elif check_keywords(text, BATTERY_KEYWORDS):
        return "Battery"
    return None

def format_content(entry):
    """Format article content."""
    date = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    title = entry.title
    content = f"# {title}\n\n"
    content += f"Link: {entry.link}\n\n"
    if hasattr(entry, 'summary'):
        content += f"{entry.summary}\n\n"
    return content

def send_to_whatsapp(content, webhook_url):
    """Send message to WhatsApp."""
    headers = {'Content-Type': 'application/json'}
    max_length = 1500
    parts = [content[i:i+max_length] for i in range(0, len(content), max_length)]
    for i, part in enumerate(parts):
        data = {
            "msgtype": "text",
            "text": {
                "content": f"(Part {i+1}/{len(parts)})\n\n{part}"
            }
        }
        response = requests.post(webhook_url, headers=headers, json=data)
        if response.status_code != 200:
            print(f"Failed to send message part {i+1} to WhatsApp: {response.text}")
        time.sleep(1)

def main():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    now = datetime.now(TIMEZONE)
    year_month = now.strftime("%Y-%m")
    today = now.strftime("%Y-%m-%d")
    
    # Content lists
    ml_content = []
    dft_content = []
    battery_content = []
    
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            print(f"Processing feed: {feed_url}")
            
            for entry in feed.entries:
                if 'published_parsed' in entry:
                    entry_date = datetime(*entry.published_parsed[:6]).date()
                elif 'updated_parsed' in entry:
                    entry_date = datetime(*entry.updated_parsed[:6]).date()
                else:
                    entry_date = now.date()
                
                if entry_date == now.date():
                    title = entry.get('title', '')
                    description = entry.get('description', '')
                    category = get_category(title, description)
                    if category:
                        formatted_content = format_content(entry)
                        if category == "ML":
                            ml_content.append(formatted_content)
                        elif category == "DFT":
                            dft_content.append(formatted_content)
                        elif category == "Battery":
                            battery_content.append(formatted_content)
                        print(f"Found {category} content: {title}")
                
        except Exception as e:
            print(f"Error processing feed {feed_url}: {str(e)}")
    
    for category, content_list in [
        ("ML", ml_content), 
        ("DFT", dft_content), 
        ("Battery", battery_content)
    ]:
        if content_list:
            all_content = "\n---\n".join(content_list)
            
            # GitHub Save Logic
            folder = f"articles/{category}/{year_month}"
            filename = f"{folder}/{today}.md"
            
            try:
                file_content = repo.get_contents(filename)
                repo.update_file(filename, f"Update {filename}", all_content, file_content.sha)
            except Exception:
                repo.create_file(filename, f"Create {filename}", all_content)
            
            # Send to WhatsApp
            if category == "ML":
                send_to_whatsapp(all_content, WHATSAPP_WEBHOOK_ML)
            elif category == "DFT":
                send_to_whatsapp(all_content, WHATSAPP_WEBHOOK_DFT)
            elif category == "Battery":
                send_to_whatsapp(all_content, WHATSAPP_WEBHOOK_BATTERY)

if __name__ == "__main__":
    main()
