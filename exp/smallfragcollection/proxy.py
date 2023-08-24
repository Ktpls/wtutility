from scapy.all import *
def dns_spoof(pkt):
    send(pkt)
    print ('Sent:', pkt.summary())
sniff(filter='', iface='wlan0', store=0, prn=dns_spoof)