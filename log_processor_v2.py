import time, json, requests, statsd
from datetime import datetime, timedelta
# Specify the name of the JSON file (in the same directory as your script)
json_file_name = 'keywords.json'

# Open and read the JSON file
try:
    with open(json_file_name, 'r') as json_file:
        data = json.load(json_file)

except FileNotFoundError:
    print(f"The file '{json_file_name}' does not exist.")
except json.JSONDecodeError as e:
    print(f"Error parsing JSON: {e}")
statsd_host = 'localhost'
statsd_port = 8125
# Initialize a StatsClient instance
statsd_client = statsd.StatsClient(statsd_host, statsd_port)

# Define the path to the log file you want to monitor
log_file_path = "C:/Users/INSUJUL/OneDrive - ABB/Desktop/Edge Monitoring/logs.txt"
gauge_list = [ "Cloud_connection_status", "OPC_Telemetry_Read_Call", "Genix_Router_to_MQTT_Connection", "Stream_Processor_Latency"]
up_counter_list = ["OPC_Adapter_Outgoing_Data", "Genix_Proxy_Messages_Received", "Genix_Proxy_Messages_Sent"]
def push_metrics(metric_name:[gauge_list,up_counter_list], greptext, value):
    if greptext in line:
        if metric_name in gauge_list:
            statsd_client.gauge(metric_name, value)
        elif metric_name in up_counter_list:
            statsd_client.incr(metric_name, value)
        else:
            print('metric type not found' )

def send_alert(alert_text):
    payload = {
        "text": alert_text
    }
    webhook_url = "https://abb.webhook.office.com/webhookb2/1332da6a-eed0-4351-a0d4-551fa1a429a6@372ee9e0-9ce0-4033-a64a-c07073a91ecd/IncomingWebhook/6c3a795d3fbe466bbffbe2bc4f3ddd7e/f38ad421-7d6a-4493-b1a3-ce23e04bdeb4"
    try:
        response = requests.post(webhook_url, json=payload)

        if response.status_code == 200:
            print("Message sent successfully to Teams channel.")
        else:
            print(f"Failed to send message. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending message: {str(e)}")       
def check_alerts(grep_text, alert_text):
    if grep_text in line:
        send_alert(alert_text)
        print(alert_text)
# try:
with open(log_file_path, 'r') as log_file:
    
    recent_logs = log_file.readlines()
for line in recent_logs:
    #Metrics Section
    push_metrics("Cloud Connection Status", "CLOUD CONNECTED", 1)
    push_metrics("Cloud Connection Status", "CLOUD DISCONNECTED", 0)

#OPCUA
    push_metrics("OPC Adapter Outgoing Data", "Platform.EdgePlatformInterface: Published message to topic", 1)

    if "Telemetry Read Call executed in" in line:
        value=int(line.split()[-2])
        statsd_client.gauge("OPC Telemetry Read Call" , value)

#Genix ROuter
    push_metrics("Genix_Router_to_MQTT_Connection", "INFO GenixRouter.GenixRouter:  MQTT Broker connection success", 1)

    if "GenixRouter.GenixRouter:  Number of Message Received to " in line:
        router_recieved = int(line.split()[-1])
        #push_metrics("Genix_Router_Data Received", "GenixRouter.GenixRouter:  Number of Message Received to outtopic", value)
        statsd_client.incr("Genix_Router_Messages_Received", router_recieved)

    if "GenixRouter.GenixRouter:  Number of Message Published" in line:
        router_published = int(line.split()[-1])
        #push_metrics("Genix_Router_Data Received", "GenixRouter.GenixRouter:  Number of Message Published to outtopic", value)
        statsd_client.incr("Genix_Router_Messages_Sent", router_published)
    
#Stream Processor
    if "streamprocessor entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)" in line:
        stream_latency = int(line.split()[-3])
        statsd_client.gauge("Stream_Processor_Latency", stream_latency)



    #Alert Section
    check_alerts("TooManyRequests (429)", "check the MongoDB Request Units")
    check_alerts("Dps Authenticate response is null", "Check the NorthBound Connection")
    
statsd_client.gauge("Genix_Router_Data_Loss", router_recieved-router_published)
# except Exception as e:
#     print(f"Error: {str(e)}")




