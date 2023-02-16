import time, BifitCollection
from settings import ORG_ID, TRADE_OBJECT_ID, USER_ID
import time
import datetime

class Calculator:

    itemContent = []
    dayItemsCount = None
    docNumbers = None
    receiptsCount = None
    receiptItemsCount = None
    shiftNumber = None
    bifit = None


    def __init__(self, filename, receiptsCount, shiftNumber, docNumber):
        self.itemContent = self.getCSVContent(filename)
        self.dayItemsCount = self.calculateCount()
        self.bifit = BifitCollection.BifitCollection()
        self.docNumbers = docNumber
        self.receiptItemsCount = divmod(self.calculateCount(), receiptsCount)[0] + 1
        self.shiftNumber = shiftNumber
        self.receiptsCount = receiptsCount


    def calculateCount(self):
        summ = 0
        for i in self.itemContent:
            summ += i[1]
        return summ



    def getCSVContent(self, filename):

        data = []

        content = open(filename, 'r')
        for line in content:
            line = line.split(";")
            if int(line[1]) > 0:
                mas = [line[0], int(line[1])]
                data.append(mas)

        return data

    def getNotNullIdInContent(self):
        posInContent = 0
        l = 0
        for item in self.itemContent:
            if item[1] > 0 and posInContent == 0:
                return l
            l += 1
        return posInContent

    #Собираем позиции для чека
    def makeItemContent(self):
        items = []
        summ = 0

        positionsInReceipt = self.receiptItemsCount
        if self.calculateCount() < positionsInReceipt:
            positionsInReceipt = self.calculateCount()

        i = 0
        while i < positionsInReceipt:

            posInContent = self.getNotNullIdInContent()
            nomenclature = self.bifit.getNomenclature(self.itemContent[posInContent][0])
            item = {
                "nomenclatureId": nomenclature.nomenclatureId,
                "description": nomenclature.nomenclatureName,
                "price": nomenclature.nomenclaturePurchasePrice,
                "vatValue": nomenclature.nomenclatureVatValue,
                "quantity": 1,
                "status": "OPEN",
                "markType": "UNKNOWN",
                "gtin": "",
                "calculationMethod": "FULL_PAY",
                "paymentSubject": "PRODUCT",
                "countryCode": "",
                "customsDeclaration": "",
                "notCreateProduction": "false"
            }
            summ += round(nomenclature.nomenclaturePurchasePrice * 1, 2)
            items.append(item)
            self.itemContent[posInContent][1] -= 1
            i += 1

        return [items, summ]


    #Формируем контент чека
    def makeReceipts(self, date):

        receiptDate = datetime.datetime.strptime(date + " 10:00:00", "%Y_%m_%d %H:%M:%S")
        receiptTime = int(time.mktime(receiptDate.timetuple())) * 1000
        receiptTimeDelay = divmod(43200, self.receiptsCount)[0] * 1000

        i = 0
        while self.calculateCount() > 0:

            items = self.makeItemContent()
            if items[0].__len__() > 0:
                time.sleep(0.8)
                receiptJSONContent = {
                                "receipt": {
                                    "created": receiptTime,
                                    "organizationId": ORG_ID,
                                    "tradeObjectId": TRADE_OBJECT_ID,
                                    "userId": USER_ID,
                                    "deviceToken": "N0sLoTNiiHEbtFdZdTA3AbT3F6t64gNQHF45VfB01rKiF1gvbU",
                                    "trueKkmId": 1284,
                                    "kkmId": "АТОЛ SIGMA 7",
                                    "receiptNumber": i,
                                    "receiptType": "SALE",
                                    "totalAmount": round(items[1], 2),
                                    "cashAmount": 0,
                                    "cardAmount": round(items[1], 2),
                                    "paymentAmountsInfo": {
                                        "Картой": round(items[1], 2)
                                    },
                                    "notified": "false",
                                    "status": "CLOSED",
                                    "statusTime": receiptTime,
                                    "shiftNumber": self.shiftNumber,
                                    "cardReaderProvider": "UNKNOWN",
                                    "fiscalDocumentNumber": self.docNumbers + i,
                                    "fiscalDriveNumber": 9999078902008717,
                                    "fiscalDriveNumberString": "9999078902008717",
                                    "fiscalSign": 2915411582,
                                    "fiscalSignString": "2915411582",
                                    "fiscalReceiptTime": receiptTime,
                                    "externalId": int(time.time()),
                                    "taxSystemCode": 0,
                                    "taxSystem": "COMMON",
                                    "internalSession": 1
                                },
                                "receiptItemList": items[0],
                                "cashierInfo": {
                                    "userId": 90,
                                    "firstName": "Иван",
                                    "lastName": "Звонилов"
                                }
                            }

            self.bifit.createReceipt(receiptJSONContent)
            print(f"[{date}] отправил чек: {i} из примерно {self.receiptsCount} с №: {self.docNumbers + i}")
            receiptTime += receiptTimeDelay
            i += 1
