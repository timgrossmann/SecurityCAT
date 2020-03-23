from zapv2 import ZAPv2

apiKey = "n6odhsffha7clen3tfldunjs0d"
target = "http://localhost:3000/"
zap = ZAPv2(apikey=apiKey)

scanID = zap.spider.scan()

print(zap)
