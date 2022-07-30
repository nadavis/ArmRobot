import serial
from time import localtime, strftime
import logging

class ArduinoMsg:
    def __init__(self, baudRate, serialPortName, time_msg_interval, sleep_msg):
        self.time_msg_interval = time_msg_interval
        self.prevTime = 0
        self.startMarker = '<'
        self.endMarker = '>'
        self.dataStarted = False
        self.dataBuf = ""
        self.messageComplete = False
        self.no_msg = 'No msg'
        self.arduinoReply = self.no_msg
        self.sleep_msg = sleep_msg
        try:
            self.serialPort = serial.Serial(port=serialPortName, baudrate=baudRate, timeout=0, rtscts=True)
            logging.info("Serial port " + serialPortName + " opened  Baudrate " + str(baudRate))
            self.wait_for_arduino()
            self.is_connection = True
        except:
            self.is_connection = False
            logging.warning("Warning: Arduino serial cannt find a port")

    def wait_for_arduino(self):
        logging.info("Waiting for Arduino to reset")
        msg = ""
        while msg.find("Arduino is ready") == -1:
            msg = self.recv_arduino_msg()

    def send_msg_by_values(self, ind, val):
        msg = ('run:' + str(ind) + ':' + str(round(val)))
        self.send_to_arduino(msg)

    def send_to_arduino(self, stringToSend):
        if self.is_connection:
            stringWithMarkers = (self.startMarker)
            stringWithMarkers += stringToSend
            stringWithMarkers += (self.endMarker)
            self.serialPort.write(stringWithMarkers.encode('utf-8'))
            logging.info('Sent msg to arduino: ', stringToSend)

    def check_serial_port(self):
        self.arduinoReply = self.recv_arduino_msg()
        if not (self.arduinoReply == self.no_msg):
            msg = strftime("%a, %d %b %Y %H:%M:%S", localtime())+'\n'+self.arduinoReply
            logging.info('received msg from arduino: ', msg)
        return self.arduinoReply

    def recv_arduino_msg(self):
        if self.is_connection:
            if self.serialPort.inWaiting() > 0 and self.messageComplete == False:
                x = self.serialPort.read().decode("utf-8")  # decode needed for Python3
                if self.dataStarted == True:
                    if x != self.endMarker:
                        self.dataBuf = self.dataBuf + x
                    else:
                        self.dataStarted = False
                        self.messageComplete = True
                elif x == self.startMarker:
                    self.dataBuf = ''
                    self.dataStarted = True
            if (self.messageComplete == True):
                self.messageComplete = False
                return self.dataBuf
            else:
                return self.no_msg
        else:
            return self.no_msg
