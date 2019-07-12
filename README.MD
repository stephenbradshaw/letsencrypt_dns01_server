Simple DNS Server that facilitates authentication using DNS-01 for Letsencrypt wildcard certificate generation


Install the files in /opt/letsencrypt_dns01/, run the server component and get a certificate for your domain like so: 

    certbot certonly --manual --server https://acme-v02.api.letsencrypt.org/directory --preferred-challenges=dns --manual-auth-hook /opt/letsencrypt_dns01/letsencrypt_dns01_authhook.py -d *.d.exmample.com


Afterwards, renew your cert like so:

    certbot renew


You can change the bind address and port of the DNS server by editing the source in the noted place, if you want to combine with a DNS proxy to also do other things with your DNS server...
