from flask import Flask, render_template, request

import RPi.GPIO as GPIO
import dht11
import time
import datetime
import sqlite3

GPIO.setmode(GPIO.BCM)

app = Flask(__name__)

instance = dht11.DHT11(pin=4)

@app.route("/")
def index():
    return "Hello from Flask"

@app.route("/main")
def main():
    sensorValue = instance.read()
    temperature = sensorValue.temperature
    humidity = sensorValue.humidity
    
    templateData = {
        'temp': temperature,
        'hum': humidity
        }
    
    print(type(templateData))
    
    return render_template('index.html', **templateData)

@app.route("/lab_db", methods=['GET'])
def database_page():
    
    conn = sqlite3.connect('/var/www/lab_app/lab_app.db')
    curs = conn.cursor()
    
    #run this block if there is no query in the message
    if request.args.to_dict() == {}:
        print('there is no request')
        curs.execute("SELECT * FROM temperatures")
        temperatures = curs.fetchall()
        curs.execute("SELECT * FROM humidities")
        humidities = curs.fetchall()
        conn.close()
        return render_template('db.html', temp = temperatures, hum=humidities)
    else:
        print('there is a request')
        from_date_str = request.args.get('from', time.strftime("%Y-%m-%d %H:%M"))
        to_date_str   = request.args.get('to', time.strftime("%Y-%m-%d %H:%M"))
        curs.execute("SELECT * FROM temperatures WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
        temperatures = curs.fetchall()
        curs.execute("SELECT * FROM humidities WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
        humidities = curs.fetchall()
        conn.close()
        return render_template('db.html', temp = temperatures, hum=humidities)

@app.route("/main_interface", methods =['GET'])
def interface():
    temperatures, humidities, from_date_str, to_date_str = get_records()
    
    return render_template('MainPage.html', temp = temperatures, hum=humidities)

def get_records():
	from_date_str 	= request.args.get('from',time.strftime("%Y-%m-%d 00:00")) 
    to_date_str 	= request.args.get('to',time.strftime("%Y-%m-%d %H:%M"))   
    range_h_form	= request.args.get('range_h','');  

	range_h_int 	= "nan" 

	try: 
		range_h_int	= int(range_h_form)
	except:
		print "input range is not a number"

	if not validate_date(from_date_str):			
		from_date_str 	= time.strftime("%Y-%m-%d 00:00")
	if not validate_date(to_date_str):
		to_date_str 	= time.strftime("%Y-%m-%d %H:%M")

		# If range_h is defined, we don't need the from and to times
	if isinstance(range_h_int,int):	
		time_now		= datetime.datetime.now()
		time_from 		= time_now - datetime.timedelta(hours = range_h_int)
		time_to   		= time_now
		from_date_str   = time_from.strftime("%Y-%m-%d %H:%M")
		to_date_str	    = time_to.strftime("%Y-%m-%d %H:%M")

	import sqlite3
	conn=sqlite3.connect('/var/www/lab_app/lab_app.db')
	curs=conn.cursor()
	curs.execute("SELECT * FROM temperatures WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
	temperatures 	= curs.fetchall()
	curs.execute("SELECT * FROM humidities WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
	humidities 		= curs.fetchall()
	conn.close()
	return [temperatures, humidities, from_date_str, to_date_str]
    

def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

@app.route("/db_graph", methods=['GET'])
def database_graph():
    
    import sqlite3
    conn = sqlite3.connect('/var/www/lab_app/lab_app.db')
    curs = conn.cursor()
    
    curs.execute("SELECT * FROM temperatures")
    temperatures = curs.fetchall()
    curs.execute("SELECT * FROM humidities")
    humidities = curs.fetchall()
    conn.close()
    
    dates=[data[0] for data in temperatures]
    temp=[data[2] for data in temperatures]
    hum=[data[2] for data in humidities]
    
    print(" Dates data type is ",type(dates))
    print(" Temperature data type is ",type(temp))
    print(" Humidity data type is ",type(hum))
        
    return render_template('graph.html', dates=dates, temp=temp, hum=hum)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)