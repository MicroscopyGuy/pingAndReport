from datetime import datetime
import icmplib
import importlib.util
import sys
sys.path.append("/home/pi/lcd")
import drivers
import math

spec = importlib.util.spec_from_file_location("drivers", "/home/pi/lcd")
display = drivers.Lcd()
initialLaunchTime = str(datetime.now())
fileName = 'netLogFile' + initialLaunchTime.replace(':', '-')[:21].replace(" ", "") + '.txt'
logFile = open(str(fileName), 'w')
#configures file name as netLogFileDateTime

avgPingThreshold = 12.0
maxPingThreshold = 50.0
packetLossThreshold = 0.01

target = 'google.com' #The location to whose connection is being tested
def displayToScreen(displayName, msgLine1, msgLine2):
    displayName.lcd_display_string(msgLine1, 1)
    display.lcd_display_string(msgLine2, 2)

def findDownString(time1, time2):
    retString = ""
    
    if (not (time1[5] == time2[5])) or (not (time1[6] == time2[6])):
        return (time1[5:19] + " " + time2[5:19])

    for index in range(5,22):
        if time1[index] == time2[index]:
            retString += time1[index]
        else:
            return (retString + time1[index]+"_" + time2[index:21])
    return ""

def ping(website):
    timeNow = datetime.today()
    
    res = icmplib.ping(website, 200, 0, 1)
    timeNow = datetime.today()
    return ([str(timeNow), res.min_rtt, res.avg_rtt, res.max_rtt, res.packet_loss, res.jitter])    
    #return ([str(timeNow), -1, -1, -1, -1])

def monitorAndLog():
    #logFile = open(str(fileName),'a')
    events=[]
    display.lcd_display_string(("No Issues Since:").center(20, " "), 2)
    display.lcd_display_string((initialLaunchTime[5:19]).center(20, " "), 3)
    
    #print(type(display))
    prevDown = False
    timeFirstDown = ''
    timeCurrDown = ''
    
    while True:
        try:
            results = ping('8.8.8.8')
            #print(results)
            
            if results[1] < 0.0001: #if internet is down 
                if not prevDown:
                    timeFirstDown = results[0][5:22]
                    prevDown = True
                    logFile.write("***** LOST CONNECTION *****" + str(results))
                    events.append("***** LOST CONNECTION *****")
                    
                else:
                    timeCurrDown = results[0][5:22]
                display.lcd_display_string("***NO CONNECTION*** ", 1)
                display.lcd_display_string(("Since:").center(20, " "), 2)
                display.lcd_display_string((timeFirstDown).center(20, " "), 3)
                display.lcd_display_string("********************", 4)
                
                logFile.write(str(results))
            
            else:                   #if internet is not down
                if prevDown:
                    prevDown = False
                    events.append("***** RECONNECTED *****" + results[0])
                    logFile.write("***** RECONNETED AT {} *****".format(str(results[0])))
                    display.lcd_display_string("** No Connection: **", 1)
                    display.lcd_display_string((timeFirstDown).center(20, " "), 2)
                    display.lcd_display_string(("*** Reconnected ***"), 3)
                    display.lcd_display_string((timeCurrDown).center(20, " "), 4)
                    timeFirstDown = ''
                    timeCurrDown = ''
                
                elif results[2] > avgPingThreshold or results[3]>maxPingThreshold or results[4]>0.1:
                    print(results)
                    display.lcd_display_string((results[0][5:22]).ljust(20, " "), 1)
                    display.lcd_display_string(("max:{} pl: {}".format(results[3], results[4])), 2)
                    display.lcd_display_string( ("avg:{} jter:{}".format(results[2], results[5])), 3)
                    display.lcd_display_string("********************", 4)
                   
                    events.append(results)
                    logFile.write(str(results))
            
            
        except KeyboardInterrupt:
            logFile.close()
            display.lcd_clear()
            print("****************************************************")
            print("There were {} events since {}".format(len(events), initialLaunchTime))
            for event in events:
                print(event)
            print("****************************************************")
            break
            
monitorAndLog()
        
        
