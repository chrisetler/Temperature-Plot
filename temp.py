#Thank you to Adafruit for the libraries for interfacing with the DHT11, because I can't read Chinese
#Using GPIO4 (this can be changed in the getVals() functions

print 'Importing Dependencies'

#I swear these are all (probably) neccesary 
import sys
import Adafruit_DHT
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from pylab import *
import datetime as dt
import os.path
import time

def main():
    print 'Initializing Variables'
    #variables use for finding min max and avg
    #min and max are used for scaling the graph and for keeping track of data
    maxTemp = 0
    minTemp = 10000
    avgTemp = 0

    #need both posix time and datetime time
    curr_time_posix = time.time()
    curr_time = dt.datetime.now()
    
    year = curr_time.year
    month = curr_time.month
    day = curr_time.day

    #file name for text file containing data
    file_name = `year`+ ' ' + `month` + ' ' + `day`

    #check to see if there is already a datafile, and import it
    if(os.path.isfile(file_name+".txt")):
       
        data = import_data(file_name+".txt")
        #I want to save as posix but matplot lib works best with datetime... that's an issue
        #have to go through element-wise and convert every posix stamp to datetime object
        #and also keep track of time with both datetiem and time.time()
        #it's frustrating, but datetime doesn't have a command to convert to posix, only from
        time_array_posix = data[0:1:]
        time_array = np.empty(np.shape(time_array_posix),dtype='object')
        print 'Previous data for today found. Importing ' + `np.shape(time_array_posix)[1]` + ' entries.' 
        for i in range(0,np.shape(time_array_posix)[1]):
            time_array[0][i] = dt.datetime.fromtimestamp(time_array_posix[0][i])
        temp_array = data[1:2:]
        humidity_array = data[2:3:]
    #if no data file is found, create blank array
    else:
        print 'No previous data found.'
        temp_array = []
        humidity_array = []
        time_array = []
        time_array_posix=[]
    

    update_delay = 1 #how many minutes between data collection

    print 'Collecting data every ' + `update_delay` + ' minute(s)'
    print 'Executing main function loop'
    while True:
        curr_time = dt.datetime.now()
        curr_time_posix = time.time()
 
        
        #print " "    
        print 'Running at: ' + `curr_time.hour` + ':'+ `curr_time.minute`
        #time_array =  # so 6:50 => 6.5
        #print 'Getting data'
        #get the data, and set max and min
        c_temp, c_hum = getVals()
        if (c_temp > maxTemp):
            maxTemp = c_temp
        if (c_temp < minTemp):
            minTemp = c_temp
        #print 'Appending arrays'

        #add data to arrays
        temp_array = np.append(temp_array,c_temp)
        humidity_array = np.append(humidity_array,c_hum)
        time_array = np.append(time_array,curr_time)
        time_array_posix = np.append(time_array_posix,curr_time_posix)


        #print 'Plotting data'
        #two separate y-axes for temperature and humidity
        fig, ax1 = plt.subplots()

        ax1.plot(time_array,temp_array, 'r.', label='Temp (F)')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Temperature (F)', color='r')

        ax2 = ax1.twinx()
        ax2.plot(time_array,humidity_array, 'b.',label='Humidity(%)')
        ax2.set_ylabel('Humidity (%)', color='b')
        ax2.axis([time_array[0],time_array[len(time_array)-1],0,100])
        ax1.axis([time_array[0],time_array[len(time_array)-1],minTemp-5,maxTemp+5])

        #Set the x axis to show Hours:Minutes
        formatter = DateFormatter('%H')
        plt.gcf().axes[0].xaxis.set_major_formatter(formatter)

        #place textbox in bottom right
        ax1.text(.97,.05,"Max: " + `np.max(temp_array)` + "\n Min: " + `np.min(temp_array)` + "\n Avg: " + `int(np.mean(temp_array))`, transform = ax1.transAxes, fontsize = 14, verticalalignment = 'bottom', horizontalalignment='right')

        #add a title
        plt.title(`month`+'/'+`day`+'/'+`year`)
  
        #print 'Saving plot to file'

        #save the plot as a png under the same filename as the text file
        
        savefig(`file_name`+'.png')
        plt.close()
        
        #print 'Plot saved. Saving Data to file'
        export_data(file_name+".txt", time_array_posix, temp_array, humidity_array)
        #print 'Data collection routine complete.'
        dtime = dt.datetime.now()

        #check to see if the day will roll over before the next run. if so, run the day-switching routine
        time_of_next_run = dt.datetime.now() + dt.timedelta(0,update_delay*60)
        if(time_of_next_run.day > curr_time.day):
            print 'Rolling over into next day!'
            #we must roll over onto the next day
            #any date-dependent variables must be updated
            #the arrays must be reset (no need to worry about importing data from next day unless time travel is invented )
            print 'Exporting min/max data'
            export_data_scalar("min and max.txt",time.time(),np.max(temp_array),np.min(temp_array),np.mean(temp_array)) #lets make a file to store max and min temps
            print 'Resetting Everything...'
            #reset all arrays
            time_array = []
            time_array_posix = []
            temp_array = []
            humidity_array = []

            #reset other data
            maxTemp = 0
            minTemp = 10000
            avgTemp = 0

            
            curr_time_posix = time.time()
            last_time = curr_time
            curr_time = dt.datetime.now()
            print 'Rolling over complete!'
            #that should suffice. Now to delay until next cycle
            print 'Sleeping for ' + `update_delay`+' minute(s)'
            time.sleep(update_delay*60 - (curr_time.second-last_time.second))
            
            curr_time_posix = time.time()
            curr_time = dt.datetime.now()
            #recompute variables for new day
            year = curr_time.year
            month = curr_time.month
            day = curr_time.day
            file_name = `year`+ ' ' + `month` + ' ' + `day`

        

        else:
            #print 'Sleeping for ' + `update_delay`+' minute(s)'
            time.sleep(update_delay*60  - (dtime.second - curr_time.second))
            
        

#get the temperature and humidity from the sensor. Courtousey of ADA_Fruit
def getVals():
    humidity, temperature = Adafruit_DHT.read_retry(11, 4)
    temperature = int(double(temperature)*9.0/5.0+32.0) # c to f
    return [temperature,humidity]

#Data format: csv with first row time, second temp, third humidity
def import_data(file_name):

    data = np.transpose(np.genfromtxt(file_name,delimiter=','))
    return data

def export_data(file_name, time_array, temp_array, humidity_array): 
    
    data = np.empty([3,len(temp_array)])
    data[0:1:] = time_array
    data[1:2:] = temp_array
    data[2:3:] = humidity_array
    np.savetxt(file_name,np.transpose(data),delimiter=',')

#For exporting the min,max,avg for a given day
#The time is in posix for conviencience, but really on the day/month/year is important
def export_data_scalar(file_name,a1,a2,a3,a4):
    data = [a1,a2,a3,a4]
    file_to_append = file(file_name, 'a') #unlike the import/export for each day's file, this one needs appending.
    np.savetxt(file_to_append,data,delimiter=',')
    file_to_append.close()
                    
    

if __name__ == '__main__':
    print 'Starting up'
    while True:
        main()
    
