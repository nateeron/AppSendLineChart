from flask import Flask, render_template, request, jsonify
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Replace with your LINE Notify access token
LINE_NOTIFY_ACCESS_TOKEN = 'GBUXdDrBPOmT8vELYFXZUSmLnDI3gG4mLeJqUXIQh1o'

@app.route('/')
def index():
    return render_template('index.html')


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


def capture_tradingview_chart():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_window_size(1200, 800)

    try:
        driver.get('http://127.0.0.1:5000/')  # Replace with your Flask app URL
        time.sleep(10)  # Wait for page to load

        chart_image_path = 'static/tradingview_chart.png'
        driver.save_screenshot(chart_image_path)

        return chart_image_path  # Return the path to the saved screenshot
    except Exception as e:
        print(f"Error capturing TradingView chart: {e}")
        return None
    finally:
        driver.quit()


def send_line_notify(message, image_path):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": "Bearer " + LINE_NOTIFY_ACCESS_TOKEN}
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
# git commit -m "Add buildpacks for Chrome and Chromedriver"
# git push heroku main