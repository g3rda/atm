import time

class ATM():
    card_number = None


    def __init__(self, location, type):
        self.location = location
        self.type = type

        self.cardReader = CardReader()
        self.cacheIssue = CacheIssue()
        self.keyboard = Keyboard()
        self.securitySystem = SecuritySystem("cam3", "3000$")
        self.displayScreen = DisplayScreen()
        self.ATMmanageSystem = ATMManageSystem()

    def show(self):
        print(self.location)
        print(self.type)

    def start(self):
        self.displayScreen.prompt(0)
        self.run()

    def run(self):
        input = -1
        while input !='0':
            if self.card_number == None:
                self.displayScreen.prompt(0)
            else:
                self.displayScreen.prompt(2)
            input = self.keyboard.getInput()
            if input == '1' and self.card_number==None:
                self.card_number = self.cardReader.retractCard()
                card_info = self.ATMmanageSystem.getCardInfo(self.card_number)
                if not self.cardReader.validateCard(self.card_number, card_info):
                    self.displayScreen.prompt("You've entered wrong card number")
                    self.displayScreen.acceptInput(self.card_number)
                    self.displayScreen.prompt(0)
                    self.card_number = None
                    continue
                self.displayScreen.prompt(1)
                self.securitySystem.videoRecorder.startRecord()
                pin = self.keyboard.getInput()
                if not self.ATMmanageSystem.validatePIN(self.card_number, pin):
                    self.displayScreen.prompt("You've entered wrong PIN")
                    self.displayScreen.prompt("Try again: ")
                    pin = self.keyboard.getInput()
                    if not self.ATMmanageSystem.validatePIN(self.card_number, pin):
                        self.displayScreen.prompt(0)
                        self.card_number = None
                        continue
                self.displayScreen.prompt("Your PIN has been accepted.")
                self.displayScreen.prompt(2)
            elif input == '1':
                self.displayScreen.prompt("Enter the amount you want to withdraw: ")
                amount = self.keyboard.getInput()
                if not amount.isnumeric():
                    self.displayScreen.prompt("Sorry, the wrong amount")
                    continue
                card_info = self.ATMmanageSystem.getCardInfo(self.card_number)
                balance = int(self.ATMmanageSystem.calculateBalance(card_info))
                if balance<int(amount):
                    self.displayScreen.prompt("Not enough money on the card")
                    continue
                safe = self.securitySystem.safe.open()
                self.cacheIssue.setAvailableCash(safe)
                if self.cacheIssue.getSignalM(int(amount)):
                    new_money = self.cacheIssue.supplyCash(int(amount), safe)
                    self.securitySystem.safe.withdraw(new_money)
                    self.displayScreen.prompt("The withdrawal has been successful.")


class CardReader():
    def retractCard(self):
        return input("Input your card number: ")
    def validateCard(self, card, card_info):
        if card_info == '':
            return 0
        correct_number = card_info.split(b":")[0]
        if card.encode() == correct_number:
            return 1
        else:
            return 0
    def ejectCard(self):
        pass

class CacheIssue():
    def setAvailableCash(self, safe):
        self.availableCash = int(safe.read()[:-1])
    def getSignalM(self, amount):
        return amount<=self.availableCash
    def supplyCash(self, amount, safe):
        self.availableCash = self.availableCash-amount
        return self.availableCash

class Keyboard():
    def getInput(self):
        return self.inputProcessing(input())

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
    start_time = time.time()
    def startRecord(self):
        pass
    def saveRecord():
        pass

class SecuritySystem():
    safe = Safe()
    videoRecorder = VideoRecord()

    def __init__(self, camera, safe):
        self.cameratype = camera
        self.safe_characteristics = safe



class DisplayScreen():
    def acceptInput(self, message):
        print("You've entered: ", message)

    def prompt(self, message):
        if not str(message).isnumeric():
            print(message)
        elif message==0:
            print("Thank you for using this ATM.\nHere is the list of commands:\n0. exit ATM\n1. insert your card\nYour choice(0 or 1): ")
        elif message==1:
            print("Your card number has been validated.\nNow, please, enter PIN code.\nYour PIN: ", end='')
        elif message==2:
            print("Choose the operation:\n1. Withdraw money\n2. Show the balance")

class ATMManageSystem():
    def getCardInfo(self, card):
        file = open('data/clients', 'rb+')
        card_info = [i for i in file.read().split(b"\n")[:-1] if card.encode() in i][0]
        file.close()
        return card_info

    def validatePIN(self, card, pin):
        correct_pin = self.getCardInfo(card).split(b":")[1]
        if pin.encode() == correct_pin:
            return 1
        else:
            return 0
    def calculateBalance(self, card_info):
        return card_info.split(b':')[2]
