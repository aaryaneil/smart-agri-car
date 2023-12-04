
from machine import Pin
from machine import Pin
from PicoDHT22 import PicoDHT22
import utime
import network
import socket
from time import sleep
import machine
from machine import Pin
import _thread as th


# Yes, these could be in another file. But on the Pico! So no more secure. :)
ssid = 'Gajaanan Ganaray'
password = 'Cahill#2311'

# Define pins to pin motors!
Mot_A_Forward = Pin(18, Pin.OUT)
Mot_A_Back = Pin(19, Pin.OUT)
Mot_B_Forward = Pin(20, Pin.OUT)
Mot_B_Back = Pin(21, Pin.OUT)

def move_forward():
    Mot_A_Forward.value(0)
    Mot_B_Forward.value(1)
    Mot_A_Back.value(1)
    Mot_B_Back.value(0)
    
def move_backward():
    Mot_A_Forward.value(1)
    Mot_B_Forward.value(0)
    Mot_A_Back.value(0)
    Mot_B_Back.value(1)

def move_stop():
    Mot_A_Forward.value(0)
    Mot_B_Forward.value(0)
    Mot_A_Back.value(0)
    Mot_B_Back.value(0)

def move_left():
    Mot_A_Forward.value(1)
    Mot_B_Forward.value(1)
    Mot_A_Back.value(0)
    Mot_B_Back.value(0)

def move_right():
    Mot_A_Forward.value(0)
    Mot_B_Forward.value(0)
    Mot_A_Back.value(1)
    Mot_B_Back.value(1)

#Stop the robot as soon as possible
move_stop()
    
def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip
    
def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind(address)
    connection.listen(1)
    return connection
def webpage():
    file_name = 'sensor_data.txt'
    # Read sensor data from file
    try:
        with open(file_name, 'r') as file:
            sensor_data = file.read()
    except OSError as e:
        print("Error reading file:", e)
        sensor_data = "No sensor data available"

    # Template HTML including sensor data
    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <title>Zumo Robot Control</title>
            </head>
            <body>
            <center><b>
            <h1>Robot Control</h1>
            <h2>Sensor Data:</h2>
            <pre>{sensor_data}</pre>
            <h2>Control Panel:</h2>
            <form action="./forward">
            <input type="submit" value="Forward" style="height:120px; width:120px" />
            </form>
            <table><tr>
            <td><form action="./left">
            <input type="submit" value="Left" style="height:120px; width:120px" />
            </form></td>
            <td><form action="./stop">
            <input type="submit" value="Stop" style="height:120px; width:120px" />
            </form></td>
            <td><form action="./right">
            <input type="submit" value="Right" style="height:120px; width:120px" />
            </form></td>
            </tr></table>
            <form action="./back">
            <input type="submit" value="Back" style="height:120px; width:120px" />
            </form>
            </body>
            </html>
            """
    return str(html)

def sensor_logging():
    file_name = 'sensor_data.txt'

    dht_sensor = PicoDHT22(Pin(28, Pin.IN, Pin.PULL_UP), dht11=True)
    while True:
        T, H = dht_sensor.read()
        if T is None:
            print("Sensor error")
        else:
            print("{}'C  {}%".format(T, H))

    # Write data to a file
        try:
            with open(file_name, 'a') as file:
                file.write("{}'C  {}%\n".format(T, H))
        except OSError as e:
            print("Error writing to file:", e)

    # DHT22 not responsive if delay is too short
        utime.sleep(30)
    
def serve(connection):
    #Start web server
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/forward?':
            move_forward()
        elif request =='/left?':
            move_left()
        elif request =='/stop?':
            move_stop()
        elif request =='/right?':
            move_right()
        elif request =='/back?':
            move_backward()
        html = webpage()
        client.send(html)
        client.close()


th.start_new_thread(sensor_logging, ())

try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()

