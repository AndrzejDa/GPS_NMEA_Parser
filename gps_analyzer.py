import serial
from loguru import logger
import time
from pprint import pprint

class Location:
    def __init__(self) -> None:
        self.latitude = 0
        self.lat_indicator = ''
        self.longitude = 0
        self.lon_indicator = ''
        self.num_of_satellites = 0
        self.list_of_satellites = list()
        self.headers = list()

    def get_id(self):
        for _ in range(4):
            sentence = read_sentence().split(',')
            if sentence[0][-3:] == "GSA":
                for i in range(3,14):
                    if sentence[i] != '':
                        element = [sentence[0][1:3], int(sentence[i]), 0]
                        self.list_of_satellites.append(element)
        pass
    
    def find_headers(self): 
        for i in range(0,len(self.list_of_satellites)):
            if self.list_of_satellites[i][0] not in self.headers:
                self.headers.append(self.list_of_satellites[i][0])

    def get_cn0(self):
        self.find_headers()
        loop = 0
        while loop != len(self.headers):
            sentence = read_sentence().split(',')
            temp = sentence[-1].split('*')
            sentence[-1] = temp[0]
            if sentence[0][-3:] == "GSV":
                header = sentence[0][1:3]
                if header in self.headers:
                    for i in range(4,len(sentence),4):
                        for j in range(0,len(self.list_of_satellites)):
                            if sentence[i] != '':
                                if (self.list_of_satellites[j][1] == int(sentence[i])) and (self.list_of_satellites[j][0] == header):
                                    if sentence[i+3] != '':
                                        self.list_of_satellites[j][2] = int(sentence[i+3])
                                    break
            if sentence[1] == sentence[2]:
                loop += 1                    
        



def send_command(string):
    cmd = '"' + string+"\r" + '"'
    ser.write(cmd.encode())
    time.sleep(0.1)
    ser.readline()
    response = ser.readline().decode()
    if response == "OK\r\n":
        logger.info(f"Command {string} accepted")
    else:
        logger.error(f"Command {string} encountered error")

def read_sentence():
    data = ""
    while True:
        char = ser.read().decode()
        if char == "$":
            data += char
            while True:
                char = ser.read().decode()
                data += char
                if char == "\n":
                    return data
    
def find_GNGGA():
    sentence = read_sentence().split(',')
    if sentence[0][-3:] == "GGA":
        if sentence[2] != '':
            loc.latitude = float(sentence[2])
        if sentence[3] != '':    
            loc.lat_indicator = sentence[3]
        if sentence[4] != '':
            loc.longitude = float(sentence[4])
        if sentence[5] != '':    
            loc.lon_indicator = sentence[5]
        if sentence[7] != '':
            loc.num_of_satellites = int(sentence[7])
        return True
    



    

    
loc = Location()
try:
    ser = serial.Serial('COM5', 115200, 8, 'N', 1, timeout=0)
    if ser.is_open:
        logger.info("Connected to comPort")
except:
    logger.error("Cannot open the port")



send_command("AT")  #test cmd
send_command("AT+CGNSPWR=1")    #turn on GNSS module
send_command("AT+CGNSTST=1")  #show NMEA continuous data

while True:
    start = time.time()
    if find_GNGGA():
        loc.headers.clear()
        loc.list_of_satellites.clear()
        loc.get_id()
        loc.get_cn0()
        pprint(loc.list_of_satellites)
        end = time.time()
        print(f"czas trwania: {end-start}")
        
ser.close()


