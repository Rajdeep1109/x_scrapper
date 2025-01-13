from flask import Flask, render_template, redirect, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from pymongo import MongoClient
import uuid
from datetime import datetime
import time

app = Flask(__name__)

# MongoDB setup
MONGO_URI = "mongodb+srv://dbUser:dbUserPassword@cluster1.0mn8a.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"
DATABASE_NAME = "x_database"
COLLECTION_NAME = "trendings"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

def fetch_trending_topics():
    options = Options()
    driver = webdriver.Chrome(options=options) 

    try:
        driver.get("https://twitter.com/login")
        time.sleep(5)

        username_field = driver.find_element(By.NAME, "text")
        username_field.send_keys("TestAcc1125082")
        username_field.send_keys(Keys.RETURN)
        time.sleep(5)

        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys("testpassword1")
        password_field.send_keys(Keys.RETURN)
        time.sleep(10)

        driver.get("https://twitter.com/home")
        time.sleep(5)

        whats_happening_section = driver.find_element(By.XPATH, "//section[@aria-labelledby='accessible-list-0']")
        trending_topics = whats_happening_section.find_elements(By.XPATH, ".//div[@data-testid='trend']")
        trends = []

        if trending_topics:
            for topic in trending_topics[:5]:
                spans = topic.find_elements(By.TAG_NAME, "span")
                if len(spans) > 1:
                    title = spans[1].text
                    trends.append(title)

        record = {
            "_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "trending_topics": trends
        }
        collection.insert_one(record)

        return trends, record

    finally:
        driver.quit()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run_script", methods=["POST"])
def run_script():
    trends, record = fetch_trending_topics()
    timestamp = record["timestamp"]
    return render_template(
        "results.html",
        timestamp=timestamp,
        trends=trends,
        record=record
    )

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
