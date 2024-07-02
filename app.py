from flask import Flask, render_template, request, jsonify
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Replace with your LINE Notify access token
LINE_NOTIFY_ACCESS_TOKEN = 'xxxxxxxxxxxxxxxxx'
# BINANCE:BTCUSDT
# dark
# tf": "15","60" "240 "D" ,W
# http://127.0.0.1:5000/?sb=BINANCE:BTCUSDT&tf=15

@app.route('/')
def index():
    sb = request.args.get('sb', 'BINANCE:BTCUSDT')
    md = request.args.get('md', 'dark')
    tf = request.args.get('tf', '60')
    TK = request.args.get('tk', '')

    # Print fetched data to console (optional for debugging)
    print(f"sb: {sb}, md: {md}, pd: {tf}")

    return render_template('index.html', sb=sb, md=md, tf=tf)


# http://127.0.0.1:5000/send?sb=BINANCE:BTCUSDT&tf=15&tk=xxxxxxxxxxxxxxxxx
@app.route('/send')
def sendLine():
    sb = request.args.get('sb', 'BINANCE:BTCUSDT')
    md = request.args.get('md', 'dark')
    tf = request.args.get('tf', '60')
    TK = request.args.get('tk', '')
    print(f"sb: {sb}, md: {md}, pd: {tf}, tk: {TK}")
    
    chart_image_path = capture_tradingview_chart(sb,md,tf)
    
    if TK == "":
        return "Token (tk): อยู่ไหนครับ ?"
    if chart_image_path :
        # Send chart image to LINE Notify
        message = f"TradingView Chart for"+sb +'TF:'+tf
        send_line_notify(message, chart_image_path,TK)
        return 'Success '
    else:
        return 'Failed to capture TradingView chart. Check logs for details.'
    



@app.route('/send_to_line', methods=['POST'])
def send_to_line():
    # Capture TradingView chart
    chart_image_path = capture_tradingview_chart()

    if chart_image_path:
        # Send chart image to LINE Notify
        message = f"TradingView Chart for NASDAQ:AAPL"
        send_line_notify(message, chart_image_path)
        return 'Chart sent to LINE Notify!'
    else:
        return 'Failed to capture TradingView chart. Check logs for details.'


def capture_tradingview_chart(sb,md,tf):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_window_size(1200, 800)
    try:
        url ='https://flaskapp-sendline-chart-fb4a1cc719f8.herokuapp.com/?sb='+sb+'&md='+md+'&tf='+tf
        #url ='http://127.0.0.1:5000/?sb='+sb+'&md='+md+'&tf='+tf
        print(f"URL = {url}")
        driver.get(url)  # Replace with your Flask app URL
        time.sleep(10)  # Wait for page to load

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