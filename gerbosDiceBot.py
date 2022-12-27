
import discord
import random
import time
import re
from numpy import sort
import requests
import math

def diceDecode(diceInput):
    characters = []
    splitValue = diceInput.split('d')
    #print(splitValue)
    return splitValue
    #for letter in diceInput:
        #characters.append(letter)

def randomJsonRequest(diceNumber,diceType,apiKey):
    jsonResponse = requests.post('https://api.random.org/json-rpc/4/invoke', json={
    "jsonrpc": "2.0",
    "method": "generateIntegers",
    "params": {
        "apiKey": apiKey,
        "n": diceNumber,
        "min": 1,
        "max": diceType,
        "base": 10
    },
    "id": 19185
    })
    #print(f"Status Code: {jsonResponse.status_code}, Response: {jsonResponse.json()}")
    return jsonResponse.json()['result']['random']['data']

######################################################################################################
runningOnPi = 1 #depending on the python version it needs the full path. on my main pc and the pi, it works with just the file name, but my laptop needs the full path. set to one for rapid debugging
#runningOnPi = int(input('Is this running on the pi? 1 for yes 0 for no.'))
if runningOnPi == 1:
    x = open("tokens.env", 'rt')
else:
    x = open("Python/gerboDiceBot/tokens.env", 'rt')
dotenv = x.readlines(0)
discordToken = dotenv[0]  #go to discords developer portal and create a bot and get your token there.
randomToken = dotenv[1] #go to random.org and get your token after creating an api key. remember, non commercial unless you pay.

x.close()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

######################################################################################################
#main command stuffs

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$help'):
        await message.channel.send('Welcome to my dice shop. Currently underconstruction.')


    if message.content.startswith('$1roll'):

        rolled20 = False #just a bunch of variables :)
        rolled1 = False
        nat20Count = 0
        splitString = message.content.split() #splits string so we can parse the words
        splitString.append('') #adds a blank string for debugging. I used it in another program and it got left over, its useful so im leaving it
        userChoice = splitString[1].lower() #sanitize your inputs
        values = diceDecode(userChoice) #turns 2d20 into ['2','20']
        diceNumber = values[0]
        diceType = values[1]

        if (int(diceType)) == 1:
            await message.channel.send('You rolled {} one(s).'.format(diceNumber))
        else:

            roll = randomJsonRequest(diceNumber,diceType,randomToken)
            roll.sort()
            await message.channel.send(roll) #roll them bones

            total = 0
            for each in roll: #counts the rolls
                total += int(each)
            if int(diceType) == 20: #checks if the user requested d20s
                if 20 in roll: rolled20 = True
                if 1 in roll: rolled1 = True
                for each in roll:
                    if int(each) == 20:
                        nat20Count += 1
                if rolled20 == True and rolled1 == True: await message.channel.send('Sure hope that was advantage.')
                elif rolled20 == True: await message.channel.send('Nat 20 :)')
                elif rolled1 == True: await message.channel.send('Nat 1 :(')
                elif nat20Count >= 2: await message.channel.send('Double crit :D')

    ###################################################################################################### begin d20 auditing

            try:
                if runningOnPi == 1:
                    x = open("scores/d{}auditor.txt".format(diceType), 'rt')
                else:
                    x = open("Python/gerboDiceBot/scores/d{}auditor.txt".format(diceType), 'rt')
            except:
                if runningOnPi == 1:
                    x = open("scores/d{}auditor.txt".format(diceType), 'x')
                else:
                    x = open("Python/gerboDiceBot/scores/d{}auditor.txt".format(diceType), 'x')

                for y in range(int(diceType)):
                    x.write('0\n')

                if runningOnPi == 1:
                    x = open("scores/d{}auditor.txt".format(diceType), 'r')
                else:
                    x = open("Python/gerboDiceBot/scores/d{}auditor.txt".format(diceType), 'r')

            playerTempScore = x.readlines() #loads the saved data
            x.close()
                
            tempList = []

            for each in playerTempScore: #turns the string '0\n' into 0. this was a bitch to code, tuns out \n is one character in a string.
                each = each.rstrip(each[-1]) #it is important to remove the last character in the string.
                tempList.append(int(each))

            diceIndex = [] # creates an index that I use to determine the value of the roll
            for x in range(int(diceType)):
                diceIndex.append(int(x) + 1)

            copyOfRoll = roll.copy()

            for each in roll: #updates the saved data via temp data. I dont like this being hardcoded
                currentDieRoll = copyOfRoll[0]
                currentIndex = diceIndex.index(currentDieRoll)
                tempList[currentIndex] += 1
                copyOfRoll.pop(0)

            strList = []

            for each in tempList:
                tempValue = str(each)
                stringWithNewLine = tempValue + '\n'
                strList.append(stringWithNewLine)

            if runningOnPi == 1: #must be opened in write mode
                x = open('scores/d{}auditor.txt'.format(diceType),'w')
            else:
                x = open('Python/gerboDiceBot/scores/d{}auditor.txt'.format(diceType),'w')
            x.close

            x.writelines(strList)

######################################################################################################

    if message.content.startswith('$1audit'):
        splitString = message.content.split() #splits string so we can parse the words
        splitString.append('') #adds a blank string for debugging. I used it in another program and it got left over, its useful so im leaving it

        try:
            if runningOnPi == 1:
                x = open("scores/d{}auditor.txt".format(splitString[1]), 'rt')
            else:
                x = open("Python/gerboDiceBot/scores/d{}auditor.txt".format(splitString[1]), 'rt')
        except:
            await message.channel.send('This dice value hasnt been rolled yet. Roll them bones!')

        audits = x.readlines()

        auditList = []

        for each in audits: #turns the string '0\n' into 0. this was a bitch to code, tuns out \n is one character in a string.
            each = each.rstrip(each[-1]) #it is important to remove the last character in the string.
            auditList.append(int(each))

        await message.channel.send(auditList)
        #calculating standard deviation and variance.
        stdDeviation = 0
        totalOfAudit = sum(auditList)
        meanOfAudit = totalOfAudit / len(auditList)
        
        mathedAuditList = []

        for each in auditList:
            each -= meanOfAudit
            each *= each
            mathedAuditList.append(each)

        sumOfMathedAuditList = sum(mathedAuditList)
        variance = sumOfMathedAuditList / (len(auditList) - 1)
        sqrOfVariance = math.sqrt(variance) #not using due to only needing the variance value
        #await message.channel.send('Variance of all d20 rolls made by this bot is: {:.2f}.\nA good variance is between 10 and 30. The lower the better.'.format(variance))
        highestValue = 0
        lowestValue = 0
        for each in auditList:
            if each >= highestValue:
                highestValue = each
        for each in auditList:
            if each <= highestValue:
                lowestValue = each
        await message.channel.send('The highest result count is {}.\nThe lowest result count is {}.'.format(highestValue,lowestValue))
        n = 1
        allRolls = []
        for each in auditList:
            for x in range(each):
                allRolls.append(n)
            n += 1
        averageRoll = sum(allRolls) / len(allRolls)
        await message.channel.send('Calculating based off of {} rolls.\nAverage of all rolls is {:.2f}.'.format(sum(auditList),averageRoll))
            
client.run(discordToken)