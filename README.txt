Domain Status Verifier.

The domainStatus.py script verifies the status of domain names based on a provided file 
or command line input. Additionally it gets the Domain Name Registrar and referral URL. 
The results are stored in an automatically generated html file or printed to stdout 
depending on the options used.

!!IMPORTANT: This script assumes that the external file containing the domains to be
verified are each on a newline and are of the following form:

  VALID:
  'https://www.example.com'
  'http://www.example.com'
  'www.example.com'
  'example.com'

  NOT VALID:
  'http://example.com'
  'www.example.com/index.html'

EXAMPLE USAGE:
  
  --feeding from file and saving to html:

    python domainStatus.py -f domains.txt
    python domainStatus.py -f domains.txt --registrar --> also adds the registrar column
    python domainStatus.py -f domains.txt --length 2 10 --> parses file from lines 10 to 20
  
  --print to stdout:
  
    python domainStatus.py -d example.org -r
  
HTML FILE:
  
  The html file generated to populate the results will use the the same core name as the 
  one used as argument + 'STATUS' + interval of lines parsed. It will be saved in a folder
  called 'generated_results' created where script is executing. The file uses the
  jQuery for table sorting. Click on headers to sort.

The domainStatus.py script uses the pywhois library for getting domain name registrar
and referral url. The needed files are included. More about python-whois on: 
'https://code.google.com/p/pywhois/'