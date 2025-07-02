import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import schedule
import time
from datetime import datetime

# Configuration
GMAIL_USER = "vanshikakanwar023@gmail.com"
GMAIL_APP_PASSWORD = "abcl khso uggw rfyr" 
RECIPIENT_EMAIL = "vanshikakanwar023@gmail.com"
BDG_URL = "https://bdgwinvip9.com/#/saasLottery/K3?gameCode=K3_1M&lottery=K3"

# Tracking variables
predictions_today = []
daily_stats = {
    'total': 0,
    'correct': 0,
    'wrong': 0,
    'profit': 0
}

def scrape_results():
    try:
        response = requests.get(BDG_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Add actual selector for results
        result = int(soup.select_one('.result-class').text)
        period = soup.select_one('.period-class').text
        return {'number': result, 'period': period}
    except Exception as e:
        print(f"Scraping error: {e}")
        return None

def analyze_pattern():
    # Implement your 70% algorithm + 30% strategy here
    # Return prediction (3, 18, or None) and confidence score
    pass

def send_email(subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = GMAIL_USER
    msg['To'] = RECIPIENT_EMAIL
    msg.set_content(body)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)

def check_and_predict():
    global predictions_today, daily_stats
    
    if len([p for p in predictions_today if not p['correct']]) >= 2:
        return  # Pause after 2 wrong predictions
        
    if daily_stats['total'] >= 10:
        return  # Daily limit reached
        
    data = scrape_results()
    if not data:
        return
        
    prediction, confidence = analyze_pattern()
    if prediction in [3, 18] and confidence >= 0.7:
        # Send prediction alert
        alert_msg = f"3 ya 18 aa sakta hai\nPeriod: {data['period']}\nTime: {datetime.now().strftime('%H:%M %p')}"
        send_email("K3 Prediction Alert", alert_msg)
        
        # Store prediction
        predictions_today.append({
            'number': prediction,
            'period': data['period'],
            'time': datetime.now(),
            'confidence': confidence
        })
        daily_stats['total'] += 1

def verify_predictions():
    global predictions_today, daily_stats
    
    data = scrape_results()
    if not data:
        return
        
    for pred in predictions_today:
        if not pred.get('verified') and pred['period'] == data['period']:
            is_correct = pred['number'] == data['number']
            pred['verified'] = True
            pred['correct'] = is_correct
            
            if is_correct:
                daily_stats['correct'] += 1
                daily_stats['profit'] += 60
            else:
                daily_stats['wrong'] += 1
                daily_stats['profit'] -= 60

def send_daily_summary():
    if predictions_today:
        accuracy = (daily_stats['correct'] / daily_stats['total']) * 100
        summary = f"""K3 Daily Summary - {datetime.now().date()}

📊 Predictions: {daily_stats['total']}
✅ Correct: {daily_stats['correct']}
❌ Wrong: {daily_stats['wrong']}
📈 Accuracy: {accuracy:.2f}%
💰 Profit/Loss: ₹{daily_stats['profit']}

System Status: ACTIVE"""
    else:
        summary = f"""K3 Daily Summary - {datetime.now().date()}

🔍 No predictions today
Reason: Unstable patterns/low confidence
📊 Trades: 0
📈 Accuracy: N/A
💰 Profit/Loss: N/A

System Status: ACTIVE (Monitoring)"""

    send_email("K3 Daily Summary", summary)
    # Reset for next day
    predictions_today = []
    daily_stats = {'total': 0, 'correct': 0, 'wrong': 0, 'profit': 0}

# Scheduling
schedule.every(1).minutes.do(check_and_predict)
schedule.every(1).minutes.do(verify_predictions)
schedule.every().day.at("22:00").do(send_daily_summary)  # 10 PM IST

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
