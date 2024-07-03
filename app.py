from flask import Flask, render_template, request, jsonify
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

@app.route('/')
def index():
    sb = request.args.get('sb', 'BINANCE:BTCUSDT')
    md = request.args.get('md', 'dark')
    tf = request.args.get('tf', '60')
    TK = request.args.get('tk', '')

    return render_template('index.html', sb=sb, md=md, tf=tf)


# http://127.0.0.1:5000/send?sb=BINANCE:BTCUSDT&tf=15&tk=xxxxxxxxxxxxxxxxxxx
@app.route('/send')
def sendLine():
    sb = request.args.get('sb', 'BINANCE:BTCUSDT')
    md = request.args.get('md', 'dark')
    tf = request.args.get('tf', '60')
    TK = request.args.get('tk', '')
    
    chart_image_path = capture_tradingview_chart(sb,md,tf,TK)
    
    if TK == "":
        return "Token (tk): อยู่ไหนครับ ?"
    if chart_image_path :
        # Send chart image to LINE Notify
        message = f"TradingView Chart for : "+sb +' TF : '+tf
        send_line_notify(message, chart_image_path,TK)
        return 'Success '
    else:
        return 'Failed to capture TradingView chart. Check logs for details.'
    


def capture_tradingview_chart(sb,md,tf,tk):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    try:
        url ='https://appsendlinechart.onrender.com/?sb='+sb+'&md='+md+'&tf='+tf+'&tk='+ tk
        # for TEST
        #url ='http://127.0.0.1:5000/?sb='+sb+'&md='+md+'&tf='+tf
        print(f"URL = {url}")
        # Browser Chrome
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.set_window_size(1200, 800)
        driver.get(url) 
        time.sleep(4)  # Wait for page to load
        chart_image_path = 'static/tradingview_chart.png'
        driver.save_screenshot(chart_image_path)

        return chart_image_path  # Return the path to the saved screenshot
    except Exception as e:
        print(f"Error capturing TradingView chart: {e}")
        return None
    finally:
        driver.quit()


def send_line_notify(message, image_path,TK):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": "Bearer " + TK}
    payload = {"message": message}
    files = {"imageFile": open(image_path, "rb")}
    response = requests.post(url, headers=headers, data=payload, files=files)
    return response.text

if __name__ == '__main__':
    app.run()


# heroku buildpacks:add --index 1 heroku/google-chrome -a flaskapp-sendline-chart
# heroku buildpacks:add --index 1 heroku/chromedriver -a flaskapp-sendline-chart
# ------------------- Remove -------------------
# heroku buildpacks:remove heroku/google-chrome -a flaskapp-sendline-chart
# heroku buildpacks:remove heroku/chromedriver -a flaskapp-sendline-chart
# ----------------------------------------------
# heroku buildpacks:add https://github.com/heroku/heroku-buildpack-chrome-for-testing -a flaskapp-sendline-chart
# git add .
# git commit -m "Add buildpacks for Chrome and Chromedriver Chang 2"
# git push heroku main

# heroku logs --tail -a flaskapp-sendline-chart
# https://flaskapp-sendline-chart-fb4a1cc719f8.herokuapp.com/
# https://flaskapp-sendline-chart-fb4a1cc719f8.herokuapp.com/send_to_line