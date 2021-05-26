import time
from classes.bank import Bank

import threading
import numpy as np
import cv2 as cv

from termcolor import cprint, colored


class ATM():
    card_number = None


    def __init__(self, location, type):
        self.location = location
        self.type = type

        self.cardReader = CardReader()
        self.cacheIssue = CacheIssue()
        self.keyboard = Keyboard()
        self.securitySystem = SecuritySystem("very cool camera", "very cool safe")
        self.displayScreen = DisplayScreen()
        self.ATMmanageSystem = ATMManageSystem()

    def show(self):
        print(self.location)
        print(self.type)

    def start(self):
        self.run()

    def run(self):
        # start camera recording as separate thread
        t = threading.Thread(target=self.securitySystem.videoRecorder.startRecord, args=())
        t.start()

        input = -1

        # while user didn't choose 'exit'
        while input !='0':
            # output menu
            if self.card_number == None:
                self.displayScreen.prompt(0)
            else:
                self.displayScreen.prompt(2)

            input = self.keyboard.getInput()

            # if user chose to insert a card
            if input == '1' and self.card_number==None:
                # get card
                self.card_number = self.cardReader.retractCard()
                card_info = self.ATMmanageSystem.getCardInfo(self.card_number)

                # validate card
                if not self.cardReader.validateCard(self.card_number, card_info):
                    self.displayScreen.prompt("You've entered wrong card number")
                    self.card_number = None
                    continue

                self.displayScreen.prompt(1)

                # get and validate pin
                pin = self.keyboard.getInput()
                if not self.ATMmanageSystem.validatePIN(self.card_number, pin):
                    self.displayScreen.prompt("You've entered wrong PIN")
                    self.displayScreen.prompt("Try again: ")
                    pin = self.keyboard.getInput()
                    if not self.ATMmanageSystem.validatePIN(self.card_number, pin):
                        self.displayScreen.prompt(0)
                        self.card_number = None
                        continue

                self.displayScreen.promptS("Your PIN has been accepted.")

            # if user chose to withdraw some cash
            elif input == '1' and self.card_number!=None:
                # get withdrawal amount
                self.displayScreen.prompt("Enter the amount you want to withdraw: ")
                amount = self.keyboard.getInput()
                if not amount.isnumeric():
                    self.displayScreen.prompt("Sorry, the wrong amount")
                    continue

                # get card balance
                card_info = self.ATMmanageSystem.getCardInfo(self.card_number)
                balance = int(self.ATMmanageSystem.calculateBalance(card_info))

                if balance<int(amount):
                    self.displayScreen.prompt("Not enough money on the card")
                    continue

                # try open safe and get money
                safe = self.securitySystem.safe.open()
                self.cacheIssue.setAvailableCash(safe)
                if self.cacheIssue.getSignalM(int(amount)):
                    new_money = self.cacheIssue.supplyCash(int(amount), safe)
                    self.securitySystem.safe.withdraw(new_money)
                    self.ATMmanageSystem.sendWithdrawalSum(self.card_number, int(amount))
                    self.displayScreen.promptS("The withdrawal has been successful.")
                else:
                    self.displayScreen.prompt("Sorry, the ATM doesn't have enough money")

            # if user chose to transfer money to another account
            elif input == '2' and self.card_number !=None:
                # ask for the amount of transfer
                self.displayScreen.prompt("Enter the amount you want to transfer: ")
                amount = self.keyboard.getInput()
                if not amount.isnumeric():
                    self.displayScreen.prompt("Sorry, the wrong amount")
                    continue

                # check if there is enough money on the card
                card_info = self.ATMmanageSystem.getCardInfo(self.card_number)
                balance = int(self.ATMmanageSystem.calculateBalance(card_info))

                if balance<int(amount):
                    self.displayScreen.prompt("Not enough money on the card")
                    continue

                # ask for number of destination card and (if valid) transfer money
                self.displayScreen.prompt("Enter the card number to transfer money to: ")
                cardTo = self.keyboard.getInput()
                if self.ATMmanageSystem.getCardInfo(cardTo)!='':
                    self.ATMmanageSystem.transferMoney(self.card_number, cardTo, int(amount))
                    self.displayScreen.promptS("The transfer has been successful.")
                else:
                    self.displayScreen.prompt("There is no such card.")
                    continue
            # if user chose to see their balance
            elif input == '3' and self.card_number!=None:
                card_info = self.ATMmanageSystem.getCardInfo(self.card_number)
                balance = int(self.ATMmanageSystem.calculateBalance(card_info))
                self.displayScreen.promptS("Your balance is "+str(balance)+"UAH")

            # if user chose to get their card back
            elif input == '4' and self.card_number!=None:
                self.displayScreen.prompt("Please, take your card.")
                self.cardReader.ejectCard(self.card_number)
                self.card_number = None

        # stop camera recording
        self.securitySystem.videoRecorder.saveRecord()



class CardReader():
    log = 'log.txt'
    def retractCard(self):
        f = open(self.log, 'a+')
        number = input(colored("/"*14, 'cyan') +"Input your card number"+colored("/"*14+"\n> ", 'cyan'))
        f.write(time.strftime('%m.%d.%y;%H:%M:%S')+": card "+number+" inserted\n")
        f.close()
        return number

    def validateCard(self, card, card_info):
        if card_info == '':
            return 0
        correct_number = card_info.split(b":")[0]
        if card.encode() == correct_number:
            return 1
        else:
            return 0

    def ejectCard(self, card):
        f = open(self.log, 'a+')
        f.write(time.strftime('%m.%d.%y;%H:%M:%S')+": card "+card+" ejected\n")
        f.close()

class CacheIssue():
    def setAvailableCash(self, safe):
        self.availableCash = int(safe.read().replace(b'\n', b''))
    def getSignalM(self, amount):
        return amount<=self.availableCash
    def supplyCash(self, amount, safe):
        self.availableCash = self.availableCash-amount
        return self.availableCash

class Keyboard():
    def getInput(self):
        return self.inputProcessing(input("> "))

    def inputProcessing(self, inp):
        return inp.strip(" .")


class Safe():
    safe_code = 92734631
    safe_name = 'data/money'
    file_safe = None
    def open(self, mode = "rb"):
        self.file_safe = open(self.safe_name, mode)
        return self.file_safe
    def close(self):
        self.file_safe.close()
    def withdraw(self, money):
        self.close()
        self.open(mode = "w")
        self.file_safe.write(str(money))
        self.close()

class VideoRecord():
    def startRecord(self):
        self.cap = cv.VideoCapture(0)
        # Define the codec and create VideoWriter object
        fourcc = cv.VideoWriter_fourcc(*'XVID')
        path='camera/'+time.strftime('%m.%d.%y;%H:%M:%S')+'.avi'
        self.out = cv.VideoWriter(path, fourcc, 20.0, (640, 480))
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            frame = cv.flip(frame, 0)
            # write the flipped frame
            self.out.write(frame)

    def saveRecord(self):
        self.cap.release()
        self.out.release()
        cv.destroyAllWindows()

class SecuritySystem():
    safe = Safe()
    videoRecorder = VideoRecord()

    def __init__(self, camera, safe):
        self.cameratype = camera
        self.safe_characteristics = safe



class DisplayScreen():
    borders = 'cyan'
    outtext = 'yellow'
    intext = 'white'
    def promptS(self, message):
        print(colored("#", self.borders)*50)
        print(self.formatMiddleWithLen(message, len(message), 'green'))
        print(colored("#", self.borders)*50)

    def formatMiddle(self, message):
        if len(message)<49:
            return colored("#", self.borders)+" "*9+colored(message, self.intext)+" "*(50-len(message)-9-2)+colored("#", self.borders)
        else:
            return colored("#", self.borders)+colored(message, self.intext)+colored("#", self.borders)

    def formatMiddleWithLen(self, message, l, color = ''):
        if color == '':
            color = self.outtext
        if len(message)<49:
            tmp = ((50-len(message)-2))
            if tmp%2==0:
                return colored("#", self.borders)+" "*(tmp//2)+colored(message, color)+" "*(tmp//2)+colored("#", self.borders)
            else:
                return colored("#", self.borders)+" "*(tmp//2)+colored(message, color)+" "*(tmp//2+1)+colored("#", self.borders)
        else:
            return colored("#", self.borders)+colored(message, color)+colored("#", self.borders)

    def prompt(self, message):
        print(colored("#", self.borders)*50)
        if not str(message).isnumeric():
            l = len(message)
            print(self.formatMiddleWithLen(message, l))
        elif message==0:
            print(self.formatMiddle("Thank you for using this ATM."))
            print(self.formatMiddle("Here is the list of commands:"))
            print(self.formatMiddle("0. Exit ATM"))
            print(self.formatMiddle("1. Insert your card"))
        elif message==1:
            print(self.formatMiddle("Your card number has been validated."))
            print(self.formatMiddle("Now, please, enter PIN code."))
        elif message==2:
            print(self.formatMiddle("Choose the operation:"))
            print(self.formatMiddle("0. Exit ATM"))
            print(self.formatMiddle("1. Withdraw money"))
            print(self.formatMiddle("2. Transfer money"))
            print(self.formatMiddle("3. Show the balance"))
            print(self.formatMiddle("4. Eject the card"))
        print(colored("#", self.borders)*50)

class ATMManageSystem():
    def getCardInfo(self, card):
        b = Bank()
        return b.getCardInfo(card)

    def validatePIN(self, card, pin):
        b = Bank()
        return b.validatePIN(card, pin)

    def calculateBalance(self, card_info):
        return card_info.split(b':')[2]

    def transferMoney(self, cardFrom, cardTo, amount):
        b = Bank()
        b.transferMoney(cardFrom, cardTo, amount)


    def sendWithdrawalSum(self, card, sum):
        b = Bank()
        b.changeBalanceAccount(card, -sum)
