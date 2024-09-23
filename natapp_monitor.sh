#!/bin/bash
export WHATSAPPTOKEN=EAAYkp8miIFoBO61FZCaXWAN17KHcUZB2egrcle3QRfrPhQjwZCYfMxb7DeNfyyZA78kZAif5TclljULVSqHhAo0EZBbKi3fcGifTfn0UEnzlZAcHjgs6NjEwGfRoufE139FiKbEXLdJQt8MAB3REvfGpHyrwTF6YN4WcAnF05nIG6w6qAEcrmeY5mV2XHIRGLJO
# Path to the nohup output file
# chmod +x /home/terry/Desktop/HomePi-S3/natapp_monitor.sh
nohup_file="/home/terry/Desktop/HomePi-S3/nohup.out"

echo "natapp_monitor start"  >> "$nohup_file"
# Monitor the file for "Tunnel established" and extract the URL
while true; do
    if grep -q "Tunnel established at" "$nohup_file"; then
        # Extract the URL
        tunnel_url=$(grep "Tunnel established at" "$nohup_file" | awk '{print $NF}')
        # Send the URL to your API using curl
#        curl -X POST -H "Content-Type: application/json" -d "{\"tunnel_url\": \"$tunnel_url\"}" http://your-api-endpoint.com/receive-url
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