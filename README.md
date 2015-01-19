<strong>Domain Status Verifier.</strong>

The domainStatus.py script verifies the status of domain names based on a provided file 
or command line input. Additionally it gets the Domain Name Registrar and referral URL. 
The results are stored in an automatically generated html file or printed to stdout 
depending on the options used.

EXAMPLE USAGE:
  
  --feeding from file and saving to html:

    python domainStatus.py -f domains.txt
    python domainStatus.py -f domains.txt --registrar --> also adds the registrar column
    python domainStatus.py -f domains.txt --length 2 10 --> parses file from lines 2 to 10
  
  --print to stdout:
  
    python domainStatus.py -d nob.ro -r
    #  ** nob.ro ** 104.28.20.102 ** 200 -- OK ** ['Netim', 'http://www.netim.com']
  
HTML FILE:
  
  The html file generated to populate the results will use the the same core name as the 
  one used as argument + 'STATUS' + interval of lines parsed. It will be saved in a folder
  called 'generated_results' created where the script is located. It contains a table similar
  to the one below. 


<table id="myTable">
<thead>
  <tr>
    <th>Nr.</th>
    <th>Domain Name</th>
    <th>IP Address</th>
    <th>Status</th>
    <th>Registrar</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>1</td>
    <td><a href="http://www.example.com">www.example.com</a></td>
    <td>93.184.216.34</td>
    <td>200</td>
    <td>N/A &#8226; N/A</td>
  </tr>
  <tr>
    <td>2</td>
    <td><a href="http://www.example.org">www.example.org</a></td>
    <td>93.184.216.34</td>
    <td>200</td>
    <td>Internet Assigned Numbers Authority (IANA) (R193-LROR) &#8226; Domain Status: serverDeleteProhibited</td>
  </tr>
  <tr>
    <td>3</td>
    <td><a href="http://www.project10249.tk">www.project10249.tk</a></td>
    <td>79.170.43.200</td>
    <td>200</td>
    <td>N/A &#8226; N/A</td>
  </tr>
  <tr>
    <td>4</td>
    <td><a href="http://www.nob.ro">www.nob.ro</a></td>
    <td>85.9.53.130</td>
    <td>200</td>
    <td>Netim &#8226; http://www.netim.com</td>
  </tr>
</tbody>
</table>

The domainStatus.py script uses the pywhois library for getting domain name registrar
and referral url. The needed files are included. More about python-whois on: 
'https://code.google.com/p/pywhois/'
