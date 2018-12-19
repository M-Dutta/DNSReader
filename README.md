A dns_client that can read DNS responses from servers 


 Run the dns_client.py by typing in the following format:
for udp:
python3 dns_client.py -t [TYPE] [DNSIP] [HOST] 
for tcp:
python3 dns_client.py -t [TYPE] --tcp [DNSIP] [HOST]
	     
example: python3 dns_client.py -t NS --tcp 8.8.8.8 google.com
