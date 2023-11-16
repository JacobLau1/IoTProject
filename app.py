import RPi.GPIO as GPIO
import dash
import dash as doc
import dash as html
import dash_daq as daq
from dash.dependencies import Input, Output
import threading
from dash import Dash, dcc, html, Input, Output, callback, State

import time
from humidity_temperature import HumidityTemperature
from lightSensor import LightSensor

import imaplib
import email
from email.header import decode_header
import time
import smtplib
import random
import string
from email.mime.text import MIMEText

import board
import Adafruit_DHT

import datetime
import serial

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

username = "etotesto1234@outlook.com"
password = "TestingIot3"
emailSentMotor = 0
emailSentLight = 0

LED = 18

Motor1 = 26
Motor2 = 19
Motor3 = 13
fanOn = False
humidTemp = HumidityTemperature()

GPIO.setup(LED, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor1, GPIO.OUT)
GPIO.setup(Motor2, GPIO.OUT)
GPIO.setup(Motor3, GPIO.OUT)

sens = LightSensor()
lightVal = 0

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
                html.Div(children=[
                    html.H1("Fan"),
                ], id='temp-fan-section'),
                html.Img(id='fan-image', src='/assets/fan_icon.png', className='fan-animation', style={'width': '145px', 'height': '145px'})
            ], className='section-divs-small'),
            html.Div(children=[
                html.H1("Humidity"),
                html.Div(children=[
                    daq.Gauge(
                        id='hum_gauge',
                        showCurrentValue=True,
                        value=5,
                        max=100,
                        min=0,
                        size=145,
                        color='#A0E9FF'
                    ),
                ]),
            ], className='section-divs-small'),
        ], id='left-components'),
    ]),
    html.Div(children=[
        html.H1("Temperature"),
        html.Div(children=[
            daq.Thermometer(
                id='temp_termometer',
                value=23,
                min=-10,
                max=40,
                height=300,
                color='#A0E9FF'
            ),
        ]),
        html.Div(id='temp_gauge_label'),
    ], className='section-divs-tall'),
    dcc.Interval(
        id = "interval",
        interval = 5 * 1000,
        n_intervals = 0,
    ),
    html.Div(children=[
        html.H1("LED Control"),
        html.Div([
            html.Img(id='led-image', src='/assets/light_off.png', style={'width': '220px', 'height': '220px'}),
        ]),
        html.Div(children=[
            html.H4("Environment Light Intensity", style={'color': 'white'}),
            daq.GraduatedBar(
                id='light_intensity',
                showCurrentValue=True,
                color={"gradient":True,"ranges":{"#b2edff":[0,4],"#80dffc":[4,7],"#1ccaff":[7,10]}},
                value=50
            ),
            html.P("", id="email_text"),
        ], id='light-intensity'),
    ], className='section-divs-tall'),
    html.Div(id='email_div'),
    dcc.Interval(
        id = "interval-fan",
        interval = 5 * 1000,
        n_intervals = 0,
    ),
    html.Div(id='motor_email'),
    dcc.Interval(
        id = "interval-motor-email",
        interval = 4 * 1000,
        n_intervals = 0,
    ),
    html.Div(id='light_div'),
    dcc.Interval(
        id = "interval-light",
        interval = 5 * 1000,
        n_intervals = 0,
    ),
    html.Div(id='light_email'),
    dcc.Interval(
        id = "interval-light-email",
        interval = 5 * 1000,
        n_intervals = 0,
    ),
], className='content')


@app.callback(
    Output('led-image', 'src'),
    Output('light_intensity', 'value'),
    Output('email_text', 'children'),
    Input('interval-light', 'n_intervals')
)
def toggle_led(n):
    lightVal = (int(sens.lightValue))/10
    global light_intensity
    global email_text
    global emailSentLight
    
    if (int(lightVal) < 40 and emailSentLight == 2):
        GPIO.output(LED, GPIO.HIGH)
        light_intensity = (int(lightVal)/10)
        led_image = '/assets/light_on.png'
        email_text = "The light has been turned on, and a notification email has been sent."
    elif (int(lightVal) < 40):
        GPIO.output(LED, GPIO.HIGH)
        light_intensity = (int(lightVal)/10)
        led_image = '/assets/light_on.png'
        email_text = "The light has been turned on, and a notification email has been sent."
        emailSentLight = 1
    else:
        GPIO.output(LED, GPIO.LOW)
        light_intensity = (int(lightVal)/10)
        led_image = '/assets/light_off.png'
        email_text = ""
        emailSentLight = 0
    
    return led_image, light_intensity, email_text
    
    
@app.callback(
    Output('light_email', 'children'),
    Input('interval-light-email', 'n_intervals')
)
def send_light_email(n):
    global emailSentLight
    
    if (emailSentLight == 1):
        emailSentLight = 2
        send_email_light()


@app.callback(
    Output('fan-image', 'className'),
    Input('interval-fan', 'n_intervals')
)
def toggle_fan_animation(n):
    global fanOn
    global emailSentMotor
    
    if (emailSentMotor == 3):
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
    Output('motor_email', 'children'),
    Input('interval-motor-email', 'n_intervals')
)
def send_motor_email(n):
    global emailSentMotor
    
    email_identifier = generate_identifier()
    
    if (emailSentMotor == 1):
        emailSentMotor = 2
        send_email()


@app.callback(
    Output('temp_termometer', 'value'),
    Output('hum_gauge', 'value'),
    Output('temp_gauge_label', 'children'),
    Input('interval', 'n_intervals'),
)
def checkHumAndTemp(n):
    global temp_termometer
    global hum_gauge
    global temp_gauge_label
    global emailSentMotor

    humidity = HumidityTemperature.getHumAndTemp()['humidity']
    temperature = HumidityTemperature.getHumAndTemp()['temperature'] 

    temp_termometer = temperature
    hum_gauge = humidity
    temp_gauge_label = f'{temperature:.2f}°C'

    if (temperature <= 23):
        emailSentMotor = 0

    if (temperature > 24 and emailSentMotor == 0):
        emailSentMotor = 1

    return temp_termometer, hum_gauge, temp_gauge_label


@app.callback(
    Output('email_div', 'children'),
    Input('interval-fan', 'n_intervals')
)
def check_email(n):
    global emailSentMotor
    
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
                if status == "OK" and emailSentMotor == 2:
                    email_message = email.message_from_bytes(msg_data[0][1])
                    process_email(email_message)

        imap.logout()

    except Exception as e:
        print("An error occurred:", str(e))

def generate_identifier(length=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def send_email():
    imap_server = "outlook.office365.com"
    with smtplib.SMTP(imap_server, 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(username, password)
        subject = f'turn on fan?'
        body = f'The current temperature is over 24. Would you like to turn on the fan?'
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = username
        msg['To'] = username
        smtp.sendmail(username, username, msg.as_string())
        print("Email sent")


def send_email_light():
    imap_server = "outlook.office365.com"

    current_time = datetime.datetime.now()
    hh = current_time.hour
    mm = current_time.minute

    with smtplib.SMTP(imap_server, 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(username, password)
        subject = f'Light turned on'
        body = f'The Light is ON at {hh:02}:{mm:02} time.'
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = username
        msg['To'] = username
        smtp.sendmail(username, username, msg.as_string())
        
#for phase 4, call this when user tag is read
def send_email_rfid():
    imap_server = "outlook.office365.com"

    current_time = datetime.datetime.now()
    hh = current_time.hour
    mm = current_time.minute

    with smtplib.SMTP(imap_server, 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(username, password)
        subject = f'RFID tag was read'
        body = f'UserX entered at this time: {hh:02}:{mm:02}.'
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = username
        msg['To'] = username
        smtp.sendmail(username, username, msg.as_string())


def process_email(email_message):
    global emailSentMotor
    
    print("Processing...")
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

    if f"Re: turn on fan?" in subject:
        if "yes" in body.lower():
            print("Recieved Yes!")
            emailSentMotor = 3

if __name__ == '__main__':
    threading.Thread(target = sens.run).start()
    
    app.run_server(debug=True)
