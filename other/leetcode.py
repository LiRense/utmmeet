from datetime import datetime,timezone

start_check = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
file = open("/opt/utm/transport/l/transport_info.log","r")
line = ""
end_line = "INFO  org.springframework.messaging.simp.broker.SimpleBrokerMessageHandler - Starting..."
while line == end_line:
    if


print(start_check)