#The domainStatus.py script uses the python-whois library for getting domain name 
#registrar and referral url. The needed files are included. More about python-whois on: 
#'https://code.google.com/p/pywhois/'

"""Domain Status Verifier.

This module verifies the status of domain names based on a provided file or command line
input. Additionally it gets the Domain Name Registrar and referral URL. The results are
stored in an automatically generated html file or printed to stdout depending on the
options used.

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
    python domainStatus.py -f domains.txt --length 2 10 --> parses file from lines 2 to 10
  
  --print to stdout:
  
    python domainStatus.py -d example.org -r
  
HTML FILE:
  
  The html file generated to populate the results will use the the same core name as the 
  one used as argument + 'STATUS' + interval of lines parsed. It will be saved in a folder
  called 'generated_results' created where script is executing. The file uses the
  jQuery for table sorting. Click on headers to sort.

"""

import os
import httplib
import socket
import re
import urllib
import urllib2
import time
import pythonwhois
import argparse
import sys


TIMEOUT = 5
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
VALUES = {'name' : 'John Doe',
          'location' : 'Northampton',
          'language' : 'English'}

parser = argparse.ArgumentParser()
parser.add_argument('--registrar','-r', help='If used, checks domain name registrar.', 
                    action='store_true')
parser.add_argument('--length', '-l', help='Two integers: the line where file parsing '
                    'should start and where it should stop. It does nothing when used '
                    'along with --display', nargs=2, default=0, type=int)
parser.add_argument('--file', '-f', help='Filename with domain names. This option is '
                    'mutually exclusive with --display')
parser.add_argument('--display', '-d', help='Display results to stdout instead of '
                    'creating html file', nargs='*')
args = parser.parse_args()


class Error(Exception):
  """Container class for exceptions in this module."""
  pass

class InvalidArgument(Error):
  """Raise if argument is not of correct type / len."""
  pass

class DomainStatus(object):
  """Checks status of domain URLs."""

  def __init__(self, domains_container):
    self.domains_container = domains_container
    self.html_file = ''

  def left_strip_url(self, host):
    """Prepare host address string."""

    if (host.startswith('http://www.')) or (host.startswith('https://www.')):
      host = host.lstrip('https://')
    return host

  def get_IP(self, host):
    """ Translate a host name to IPv4 address format. The IPv4 address is returned as a 
      string, such as '100.50.200.5'. If the host name is an IPv4 address itself it is 
      returned unchanged.

      Returns the IP string for success and 'IP N/A' if it fails to get it.
    """
    host_name = self.left_strip_url(host)
    try:
      return socket.gethostbyname(host_name)
    except socket.gaierror:
      return 'N/A'

  def get_status_code(self, host):
    """Gets status code or Error message after a HTTP 'GET' request.
    
      Returns:
        string: http code  and reason if succesful
        string: timeout after (TIMEOUT value in ms) if socket.timeout
        string: exception message for everything else 
    """

    host_name = self.left_strip_url(host)
    headers = { 'User-Agent' : USER_AGENT }
    params = urllib.urlencode(VALUES)
    conn = httplib.HTTPConnection(host_name, timeout=TIMEOUT)
    try:
      conn.request("HEAD", "/", params, headers)
      response = conn.getresponse()
      if response.status in [400, 403]:
        status = self.status_code_helper(host_name)
      else:
        status = '%i -- %s' %(response.status, response.reason)
    except socket.timeout:
      return 'timed out (%i ms)' %(TIMEOUT * 1000)
    except Exception as e:
      status = e
    conn.close()
    return status
  
  def status_code_helper(self, host):
    """Helper method for 'get_status_code()'.
    
      Sometimes when using the 'httplib.request('GET', ...)' method, the response
      is erroneously returned as '400 or 403'. Using urllib2.getcode() returns the
      correct code.
    """

    headers = { 'User-Agent' : USER_AGENT }
    data = urllib.urlencode(VALUES)
    if not (host.startswith('http://www.')) or (host.startswith('https://www.')):
      if host.startswith('www.'):
        host = 'http://%s' %host
      else:
        host = 'http://www.%s' %host
    req = urllib2.Request(host, data, headers)
    try:
      response = urllib2.urlopen(url=req, timeout=TIMEOUT)
      status = response.getcode()
      if status == 200:
        status = '200 -- OK'
    except urllib2.HTTPError, e:
      status = '%i -- %s' %(e.code, e.reason)
    except urllib2.URLError, e:
      status = e.reason
    except socket.timeout:
      return 'timed out (%i ms)' %(TIMEOUT * 1000)
    except Exception as e:
      status = e
    return status

  def get_domain_name_registrar(self, host):
    """Get domain name registrar using python-whois."""

    try:
      w = pythonwhois.whois(host)
      w.text
      a = [w.registrar, w.referral_url]
      new_a = ['N/A' if i == [] else i for i in a]
      return new_a
    except Exception:
      return ['N/A', 'N/A']

  def add_status_to_html(self, parse_length=0, name_registrar=False):
    """Adds the domain status as table entries in the created html file.
    
      parse_length: integer 0 / list with two integers
      name_registrar: boolean (if True, also adds the domain name registrar value)

      Example: self.add_status_to_html() --> parses whole file & no registrar
               self.add_status_to_html(parse_length=[3, 10], name_registrar=True) --> 
                 parses lines 3 to 10 (including)
    """
    row_nr = 1
    feed_list = [line.strip() for line in open(self.domains_container)]
    if parse_length == 0:
      url_list = feed_list
    elif type(parse_length) == list and len(parse_length) == 2 and \
                              type(parse_length[0]) == int and type(parse_length[1]) == int:
      url_list = [feed_list[i] for i in range(parse_length[0] - 1, parse_length[1])]
    else: 
      raise InvalidArgument('The \'parse_length\' argument must be a list with two integers!')
    self._create_html_template(parse_length, name_registrar)
    with open (self.html_file, 'a') as my_file:
      for url in url_list:
        status_code = self.get_status_code(url)
        ip_value = str(self.get_IP(url))
        if name_registrar:
          registrar =  self.get_domain_name_registrar(url)
          registrar_entry = '    <td>%s &bullet; %s</td>\n' %(registrar[0], registrar[1])
        else:
          registrar_entry = ''
        host_domain = self.left_strip_url(url)
        my_file.write('  <tr>\n'
                      '    <td>%s</td>\n'
                      '    <td><a href="http://%s">%s</a></td>\n'
                      '    <td>%s</td>\n'
                      '    <td>%s</td>\n'
                      '%s'
                      '  </tr>\n' % (row_nr, host_domain, host_domain, ip_value, status_code,
                                     registrar_entry))
        row_nr += 1
        print '%s ** %s ** line %s' % (url, status_code, feed_list.index(url) + 1)
      my_file.write('</tbody>\n'
                  '</table>\n'
                  '</body>\n'
                  '</html>\n')

  def print_status(self, name_registrar=False):
    """Prints results to stdout.
    if name_registrar is True, domain name registrar info is included
    Example output: ** example.org ** 93.184.216.34 ** 200 -- OK.
    """

    for domain in self.domains_container:
      domain_status = self.get_status_code(domain)
      IP = self.get_IP(domain)
      if name_registrar:
        domain_registrar = self.get_domain_name_registrar(domain)
        print '** %s ** %s ** %s ** %s' % (domain, IP, domain_status, domain_registrar)
      else:
        print '** %s ** %s ** %s' % (domain, IP, domain_status)

  def _create_html_template(self, parse_length, name_registrar):
    """Creates a html template file with a table."""

    if name_registrar:
      registrar_column = '    <th>Registrar</th>\n'
    else:
      registrar_column = ''

    html_head = ('<!doctype html>\n'
                 '<html>\n<head>\n  <title>Domain Status</title>\n' 
                 '  <meta charset="utf-8" />\n  <meta http-equiv="Content-type" content="text/html; charset=utf-8" />\n'
                 '  <meta name="viewport" content="width=device-width, initial-scale=1" />\n'
                 '  <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>\n'
                 '  <script type="text/javascript" src="../scripts/jquery.tablesorter.js"></script>\n'
                 '  <script type="text/javascript" src="../scripts/sortit.js"></script>\n'
                 '</head>\n')

    html_style = ('<style>\n\n'
                  '  body {\n'
                  '    font-family: Verdana, Geneva, sans-serif;\n'
                  '  }\n\n'
                  '  th, td {\n'
                  '    padding: 6px;\n'
                  '    background-color: #F2F2F2;\n'
                  '    max-width: 500px;\n'
                  '    overflow: hidden;\n'
                  '    border-radius: 3%;\n  }\n\n'
                  '  th:hover {\n'
                  '    background-color: #40E0D0;\n'
                  '  }\n\n'
                  '  th {\n'
                  '    background-color: #7FFFD4;\n  }\n'
                  '</style>\n')

    html_paragraph = ('<body>\n'
                      '<h3>Get Domain Status</h3>\n'
                      '<p>This document was generated automatically on <i>%s</i> by <i>%s</i></p>\n'
                      '<p>Click on headers to sort</p>\n\n') %(
                          time.strftime("%c"), os.path.basename(sys.argv[0]))

    domains_table = ('<table id="myTable">\n'
                     '<thead>\n'
                     '  <tr>\n'
                     '    <th>Nr.</th>\n'
                     '    <th>Domain Name</th>\n'
                     '    <th>IP Address</th>\n'
                     '    <th>Status</th>\n'
                     '%s'
                     '  </tr>\n'
                     '</thead>\n'
                     '<tbody>\n') %(registrar_column)

    #create name for the save file
    core_name = os.path.basename(os.path.splitext(self.domains_container)[0])
    executing_file_path = os.path.dirname(sys.argv[0])
    self.html_file = os.path.join(executing_file_path, 'generated_results',
                                  '%s_STATUS_%s.html' %(core_name, str(parse_length)))
    #check if 'generated_results' folder exists. if not create it
    if not os.path.exists(os.path.dirname(self.html_file)):
      os.makedirs(os.path.dirname(self.html_file))

    with open (self.html_file, 'w') as my_file:
      my_file.write(html_head)
      my_file.write(html_style)
      my_file.write(html_paragraph)
      my_file.write(domains_table)


def main():
  """Parse options / arguments and instantiate class DomainStatus."""

  mutually_exclusive = [option for option in[args.file, args.display] if option]
  if len(mutually_exclusive) != 1:
    parser.error('Invalid options / args usage. Use -h for help\nEXAMPLE: '
                 '--file my_file.txt OR --display domain1.com domain2.com etc...')
  if args.file:
    print args.file
    save_test = DomainStatus(args.file)
    save_test.add_status_to_html(parse_length=args.length, name_registrar=args.registrar)
  if args.display:
    display_test = DomainStatus(args.display)
    display_test.print_status(name_registrar=args.registrar)


if __name__ == "__main__":
  main()
