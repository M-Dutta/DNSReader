Name: Mishuk Dutta
ID: 811361849

Submission: 
	    A dns_client that can read DNS responses from servers 

Virtual Env Activation:
	    To activate the virtual enviornment, 
	    get inside the hw02 folder and type:
						source bin/activate

Running the Submission:
	    Run the dns_client.py by typing in the following format:
	    for udp:
	    python3 dns_client.py -t [TYPE] [DNSIP] [HOST] 
	    for tcp:
	    python3 dns_client.py -t [TYPE] --tcp [DNSIP] [HOST]
	     
	    example: python3 dns_client.py -t NS --tcp 8.8.8.8 google.com