#!/bin/bash

# Path to the nohup output file
nohup_file="/home/terry/Desktop/HomePi-S3/nohup.out"

# Monitor the file for "Tunnel established" and extract the URL
while true; do
    if grep -q "Tunnel established at" "$nohup_file"; then
        # Extract the URL
        tunnel_url=$(grep "Tunnel established at" "$nohup_file" | awk '{print $NF}')

        # Send the URL to your API using curl
        # curl -X POST -H "Content-Type: application/json" -d "{\"tunnel_url\": \"$tunnel_url\"}" http://your-api-endpoint.com/receive-url
        # Send the WhatsApp message using curl
				curl -i -X POST \
				  https://graph.facebook.com/v20.0/411026728762888/messages \
				  -H "Authorization: Bearer $WHATSAPPTOKEN" \
				  -H "Content-Type: application/json" \
				  -d '{
				        "messaging_product": "whatsapp",
				        "to": "85253986939",
				        "type": "template",
				        "template": {
				          "name": "raspberry",
				          "language": { "code": "en" },
				          "components": [
				            {
				              "type": "body",
				              "parameters": [
				                {
				                  "type": "text",
				                  "text": "'"$tunnel_url"'"
				                }
				              ]
				            }
				          ]
				        }
				      }'
        # Break the loop after finding the URL
        break
    fi
    sleep 2
done

# remember to make the script executable and add the following line before exit 0
# chmod +x /home/terry/Desktop/HomePi-S3/natapp_monitor.sh
# sudo nano /etc/rc.local
# /home/terry/Desktop/HomePi-S3/natapp_monitor.sh &
# reboot