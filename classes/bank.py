class Bank():
    def getCardInfo(self, card):
        file = open('data/clients', 'rb+')
        try:
            card_info = [i for i in file.read().split(b"\n")[:-1] if card.encode() in i][0]
        except:
            card_info = ''
        file.close()
        return card_info

    def validatePIN(self, card, pin):
        correct_pin = self.getCardInfo(card).split(b":")[1]
        if pin.encode() == correct_pin:
            return 1
        else:
            return 0

    def changeBalanceAccount(self, card, amount):
        file = open('data/clients', 'rb+')
        te = file.read()
        file.close()
        a=te.find(str(card).encode()+b":")+len(card)+1+2
        curbalance = int(te[a:te.find(b'\n', a)])
        te = te[:a]+str(curbalance+amount).encode()+te[te.find(b'\n', a):]
        file.close()
        file = open('data/clients',"wb")
        file.write(te)
        file.close()

    def transferMoney(self, cardFrom, cardTo, amount):
        self.changeBalanceAccount(cardFrom, -amount)
        self.changeBalanceAccount(cardTo, amount)
