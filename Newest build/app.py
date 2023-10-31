import RPi.GPIO as GPIO
import dash
import dash as doc
import dash as html
import dash_daq as daq
from dash.dependencies import Input, Output
from dash import Dash, dcc, html, Input, Output, callback

import time
from humidity_temperature import HumidityTemperature

import imaplib
import email
from email.header import decode_header
import time
import smtplib
import random
import string

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

username = "iot_testing_321@outlook.com"
password = "TestingIot3"
emailSent = 0
isFanOn = False
LED = 18

Motor1 = 13
Motor2 = 6
Motor3 = 5
humidTemp = HumidityTemperature()

GPIO.setup(LED, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor1, GPIO.OUT)
GPIO.setup(Motor2, GPIO.OUT)
GPIO.setup(Motor3, GPIO.OUT)

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.Div(children=[
        html.Div(children=[
            html.Div(children=[
                html.H1("IoT: Project"),
                html.H3("By Jacob, Nicholas, and Sonia"),
            ], className='section-divs-big'),
        ]),
        html.Div(children=[
            html.Div(children=[
                html.H1("Humidity"),
                html.Div(children=[
                    daq.Gauge(
                        id='hum_gauge',
                        showCurrentValue=True,
                        value=0,
                        max=100,
                        min=0,
                        size=145,
                        color='#A0E9FF'
                    ),
                ]),
            ], className='section-divs-small'),
            html.Div(children=[
                html.Div(children=[
                    html.H1("Fan"),
                    html.Button('Start Fan', id='fan-button', style={'margin': '20px'})
                ], id='temp-fan-section'),
                html.Img(id='fan-image', src='/assets/fan_icon.png', className='fan-animation', style={'width': '145px', 'height': '145px'})
            ], className='section-divs-small'),
        ], id='left-components'),
    ]),
    html.Div(children=[
        html.H1("LED Control"),
        html.Div([
            html.Img(id='led-image', src='/assets/light_off.png', style={'width': '300px', 'height': '300px'}),
        ]),
        html.Div([
            html.Button('Toggle LED', id='led-button', style={'margin': '20px'}),
        ]),
    ], className='section-divs-tall'),
    dcc.Interval(
        id = "interval",
        interval = 5 * 1000,
        n_intervals = 0,
    ),
    html.Div(children=[
        html.H1("Temperature"),
        html.Div(children=[
            daq.Thermometer(
                id='temp_termometer',
                value=0,
                min=-10,
                max=40,
                height=300,
                color='#A0E9FF'
            ),
        ]),
        html.Div(id='temp_gauge_label'),
    ], className='section-divs-tall'),
    html.Label(id='temp_div'),
    dcc.Interval(
        id = "interval-fan",
        interval = 5 * 1000,
        n_intervals = 0,
    ),
], className='content')

@app.callback(
    Output('led-image', 'src'),
    Input('led-button', 'n_clicks')
)
def toggle_led(led_clicks):
    if led_clicks is None:
        led_image = '/assets/light_off.png'
    else:
        if led_clicks % 2 == 1:
            GPIO.output(LED, GPIO.HIGH)
            led_image = '/assets/light_on.png'
        else:
            GPIO.output(LED, GPIO.LOW)
            led_image = '/assets/light_off.png'
            
    return led_image

@app.callback(
    Output('fan-image', 'className'),
    Input('fan-button', 'n_clicks')
)
def toggle_fan_animation(fan_clicks):
    if fan_clicks is None:
        GPIO.output(Motor1, GPIO.LOW)
        GPIO.output(Motor2, GPIO.LOW)
        GPIO.output(Motor3, GPIO.LOW)
        return 'fan-image-off'
    if fan_clicks % 2 == 1:
        GPIO.output(Motor1, GPIO.HIGH)
        GPIO.output(Motor2, GPIO.HIGH)
        GPIO.output(Motor3, GPIO.LOW)
        return 'fan-image-on'
    else:
        GPIO.output(Motor1, GPIO.LOW)
        GPIO.output(Motor2, GPIO.LOW)
        GPIO.output(Motor3, GPIO.LOW)
        return 'fan-image-off'

@app.callback(
    Output('temp_termometer', 'value'),
    Output('hum_gauge', 'value'),
    Output('temp_gauge_label', 'children'),
    Input('interval', 'n_intervals')
)            
def checkHumAndTemp(n):
    global emailSent
    
    humidity = HumidityTemperature.getHumAndTemp()['humidity']
    temperature = HumidityTemperature.getHumAndTemp()['temperature'] 
    
    temp_termometer = temperature
    hum_gauge = humidity
    temp_gauge_label = f'{temperature:.2f}°C'
    
    if (temperature < 20 and emailSent == 2):
        sendEmail = 0
    
    if (temperature > 22 and emailSent == 0):
        ##email_identifier = generate_identifier()
        ##send_email(email_identifier)
        emailSent = 1
        
    return temp_termometer, hum_gauge, temp_gauge_label
'''
@app.callback(
    Output('temp_div', 'children'),
    Input('interval-fan', 'n_intervals')
)
def CheckEmail(n):
    if (emailSent == 1):
        ##while True:
        try:
            # Connect to the IMAP server
            imap_server = "outlook.office365.com"
            imap = imaplib.IMAP4_SSL(imap_server)
            imap.login(username, password)

            # Select the INBOX
            imap.select("INBOX")

            # Search for all unseen messages
            status, messages = imap.search(None, "UNSEEN")

            if status == "OK" and messages:
                message_ids = messages[0].split()
                for msg_id in message_ids:
                    status, msg_data = imap.fetch(msg_id, "(RFC822)")
                    if status == "OK" and emailSent == 1:
                        email_message = email.message_from_bytes(msg_data[0][1])
                        process_email(email_message, email_identifier)

            imap.logout()

        except Exception as e:
            print("An error occurred:", str(e))
'''

def generate_identifier(length=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def send_email(email_identifier):
    imap_server = "outlook.office365.com"
    with smtplib.SMTP(imap_server, 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(username, password)
        subject = f're: turn on fan? [{email_identifier}]'
        body = f'The current temperature is {currTemp}. Would you like to turn on the fan?'
        msg = f'subject: {subject}\n\n{body}'
        smtp.sendmail(username, username, msg)
'''
def process_email(email_message, email_identifier):
    # This function processes the received email
    subject = email_message["Subject"]
    
    # Check if the email is multipart
    if email_message.is_multipart():
        body = ""
        for part in email_message.walk():
            content_type = part.get_content_type()
            if "text/plain" in content_type:
                body += part.get_payload(decode=True).decode()
    else:
        body = email_message.get_payload()
    
    if f"Re: turn on fan? [{email_identifier}]" in subject:
        if "Yes" in body:
            print("Received 'Yes' in the email body.")
            isFanOn = True
            emailSent = 2

@app.callback(
    Output('email_output', 'value'),
    Input('interval', 'n_intervals')
)

def sendEmail(n):
    email_identifier = generate_identifier()
    send_email(email_identifier)
    
    while not isFanOn:
        try:
            # Connect to the IMAP server
            imap_server = "outlook.office365.com"
            imap = imaplib.IMAP4_SSL(imap_server)
            imap.login(username, password)

            # Select the INBOX
            imap.select("INBOX")

            # Search for all unseen messages
            status, messages = imap.search(None, "UNSEEN")

            if status == "OK" and messages:
                message_ids = messages[0].split()
                for msg_id in message_ids:
                    status, msg_data = imap.fetch(msg_id, "(RFC822)")
                    if status == "OK":
                        email_message = email.message_from_bytes(msg_data[0][1])
                        process_email(email_message, email_identifier)

            imap.logout()

            # Pause for a few seconds before checking again
            time.sleep(2)

        except Exception as e:
            print("An error occurred:", str(e))
'''

if __name__ == '__main__':
    app.run_server(debug=True)

