## Domain Status Info

The `domain_status_info.py` script verifies the status of domain names based on a provided file
or command line input. Additionally it gets the Domain Name Registrar and referral URL.
The results are stored in an automatically generated html file or printed to stdout
depending on the options used.

### Requirements

The script depends on the `whois` library for getting domain name registrar and referral url. It is however optional, and if not installed the `-r` or `--registrar` flag will be ignored. Use `pip install python-whois` in case you want this information.

### Usage

* Feeding from file and saving to html

```bash
> python domain_status_info.py -f domains.txt
> python domain_status_info.py -f domains.txt --registrar # also adds the registrar column
> python domain_status_info.py -f domains.txt --length 2 10 # parses file from lines 2 to 10
```

* Print to stdout

```bash
> python domain_status_info.py -d nob.ro skamsie.ro example.org -r

> ** nob.ro ** 104.28.21.102 ** 200 -- OK ** ['Netim', 'http://www.netim.com']
> ** skamsie.ro ** 104.27.160.159 ** 200 -- OK ** ['EuroDomenii', 'http://www.domenii.eu']
> ** example.org ** 93.184.216.34 ** 200 -- OK ** ['ICANN', 'N/A']
```

### Status codes

The status codes returned are similar with the ones returned by the <code>curl -I</code> command on *nix systems. Because it is a script it will sometimes get <code>406 -- Not  Acceptable</code> from some domains. Note that it does not follow redirects.

### Html file

The html file generated to populate the results will use the the same core name as the
one used as argument + 'STATUS' + interval of lines parsed. It will be saved in a folder
called 'generated_results' created where the script is located. It contains a table like
the one below.

![screenshot](https://github.com/skamsie/Domain-Status-Checker/raw/master/screenshot.png)
