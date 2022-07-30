import asyncio
import aioconsole
import serial
from time import localtime, strftime
import time

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
            print("Serial port " + serialPortName + " opened  Baudrate " + str(baudRate))
            self.waitForArduino()
            self.is_connection = True
        except:
            self.is_connection = False
            print("Error: Arduino serial cannt find a port")

    def send_msg_by_values(self, ind, val):
        msg = ('run:' + str(ind) + ':' + str(round(val)))
        time.sleep(0.1)
        print(msg)
        self.sendToArduino(msg)

    def sendToArduino(self, stringToSend):
        if self.is_connection:
            stringWithMarkers = (self.startMarker)
            stringWithMarkers += stringToSend
            stringWithMarkers += (self.endMarker)
            self.serialPort.write(stringWithMarkers.encode('utf-8'))
            #await asyncio.sleep(0.01)

    def checkSerialPort(self):
        self.arduinoReply = self.recvLikeArduino()
        if not (self.arduinoReply == self.no_msg):
            #print(strftime("%a, %d %b %Y %H:%M:%S", localtime()))
            #print(self.arduinoReply)
            msg = strftime("%a, %d %b %Y %H:%M:%S", localtime())+'\n'+self.arduinoReply
        return self.arduinoReply

    def checkSerialPort_(self):
        recentPacketString = []
        if self.serialPort.isOpen() and self.serialPort.in_waiting:
            recentPacket = self.serialPort.readline()
            recentPacketString = recentPacket.decode('utf').rstrip('\n')
            print(recentPacketString)
        return recentPacketString

    def recvLikeArduino(self):
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

    def waitForArduino(self):
        print("Waiting for Arduino to reset")
        msg = ""
        while msg.find("Arduino is ready") == -1:
            msg = self.recvLikeArduino()
            if not (msg == self.no_msg):
                print(msg)

    async def run(self):
        print("Arduino msg routine")
        self.prevTime = time.time()
        while True:
            # check for a reply
            self.arduinoReply = self.recvLikeArduino()
            if not (self.arduinoReply == self.no_msg):
                print(strftime("%a, %d %b %Y %H:%M:%S", localtime()))
                print(self.arduinoReply)

            # send a message at intervals
            if (time.time() - self.prevTime > self.time_msg_interval):
                #msg = input("Enter a input: ")
                msg = await aioconsole.ainput("Enter a input: ")
                self.sendToArduino(msg)
                print(msg)
                self.prevTime = time.time()

    async def sendMsg(self):
        print("Arduino send msg routine")
        self.prevTime = time.time()
        while True:
            # send a message at intervals
            if (time.time() - self.prevTime > self.time_msg_interval):
                # msg = input("Enter a input: ")
                msg = await aioconsole.ainput("Enter a input: ")
                self.sendToArduino(msg)
                print(msg)
                self.prevTime = time.time()

    async def recvMsg(self):
        print("Arduino recv msg routine")
        while True:
            # check for a reply
            self.arduinoReply = self.recvLikeArduino()
            if not (self.arduinoReply == self.no_msg):
                print(strftime("%a, %d %b %Y %H:%M:%S", localtime()))
                print(self.arduinoReply)
            await asyncio.sleep(self.sleep_msg)

async def main():
    time_msg_interval = 1.0
    msg_buff = 9600
    port = '/dev/cu.usbmodem1433201'
    sleep_msg = 0.01

    print("Setup multiprocess")
    arduino_msg = ArduinoMsg(msg_buff, port, time_msg_interval, sleep_msg)

    print("Start tasks")

    task_am_recv = asyncio.create_task(coro=arduino_msg.recvMsg())
    task_am_send = asyncio.create_task(coro=arduino_msg.sendMsg())


    await task_am_recv
    await task_am_send


if __name__ == "__main__":
    asyncio.run(main())