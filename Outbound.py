import socket
import requests
import json
import pprint
import time

UDP_IP = "192.168.4.1"
UDP_PORT = 49152
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP_IP,UDP_PORT))

IP_GateIn = "192.168.4.10"
PORT_GateIn = 1235
GateIn_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

IP_GateOut = "192.168.4.20"
PORT_GateOut = 1238
GateOut_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

addr_sock = {"192.168.4.10": GateIn_sock,
             "192.168.4.20": GateOut_sock}

addr_port = {"192.168.4.10": PORT_GateIn,
             "192.168.4.20": PORT_GateOut}

counts_outbound = 1
sku_array_outbound = []
finds_outbound = 0


while True:
    print("--------------------------------------------------------------------------------------------------------------------------------------------")
    print("#Gate Scanner Outbound Ready to Reading#")
    print("#PRESS THE BUTTON#")
    print("")
    print("Menunggu input dari scanner 1....")
    data_outbound, addr_outbound = sock.recvfrom(1200)
    
    i_outbound = 0
    arry_outbound = []


    for elemen in data_outbound:
        
        arry_outbound.append(elemen)
        
        i_outbound=i_outbound+1

    j_outbound=0
    arry_bytes_outbound =[]

    for elemen in arry_outbound:
        
        data_decimal_outbound = elemen & 0xFF
        data_hex_outbound = hex(data_decimal_outbound)
        data_bytes_outbound = int(data_hex_outbound,16).to_bytes(1,byteorder='big')
    
        arry_bytes_outbound.append(data_bytes_outbound)
        j_outbound=j_outbound+1
    
    arry_bytes_str_outbound = []

    for elemen in arry_bytes_outbound:
        hex_x_outbound = hex(elemen[0])[2:]
        if len(hex_x_outbound) < 2:
            hex_x_outbound = '0'+ hex_x_outbound
        arry_bytes_str_outbound.append(hex_x_outbound)
    
    sku_outbound = ""

    for elemen_sku in arry_bytes_str_outbound:
        sku_outbound = sku_outbound + elemen_sku
    
    sku_outbound = sku_outbound.upper()
    print(f"sukses diterima awal outbound scanner 1 : {sku_outbound}")
    
    sku_send = []
    jumlah_sku = int((len(sku_outbound))/24)
    indeks_sku_awal = 0
    indeks_sku_akhir = 24
    
    for order_sku in range(jumlah_sku):
        
        sku_send.append(sku_outbound[indeks_sku_awal:indeks_sku_akhir])
        indeks_sku_awal = indeks_sku_awal + 24
        indeks_sku_akhir = indeks_sku_akhir + 24
        
    print("Menunggu input dari scanner 2....")
    data_outbound, addr_outbound = sock.recvfrom(1200)
    
    i_outbound = 0
    arry_outbound = []


    for elemen in data_outbound:
        
        arry_outbound.append(elemen)
        
        i_outbound=i_outbound+1

    j_outbound=0
    arry_bytes_outbound =[]

    for elemen in arry_outbound:
        
        data_decimal_outbound = elemen & 0xFF
        data_hex_outbound = hex(data_decimal_outbound)
        data_bytes_outbound = int(data_hex_outbound,16).to_bytes(1,byteorder='big')
    
        arry_bytes_outbound.append(data_bytes_outbound)
        j_outbound=j_outbound+1
    
    arry_bytes_str_outbound = []

    for elemen in arry_bytes_outbound:
        hex_x_outbound = hex(elemen[0])[2:]
        if len(hex_x_outbound) < 2:
            hex_x_outbound = '0'+ hex_x_outbound
        arry_bytes_str_outbound.append(hex_x_outbound)
    
    sku_outbound = ""

    for elemen_sku in arry_bytes_str_outbound:
        sku_outbound = sku_outbound + elemen_sku
    
    sku_outbound = sku_outbound.upper()
    print(f"sukses diterima awal inbound scanner 2 : {sku_outbound}")
    
    sku_scanner2 = []
    jumlah_sku = int((len(sku_outbound))/24)
    indeks_sku_awal = 0
    indeks_sku_akhir = 24
    
    for order_sku in range(jumlah_sku):
        
        sku_scanner2.append(sku_outbound[indeks_sku_awal:indeks_sku_akhir])
        indeks_sku_awal = indeks_sku_awal + 24
        indeks_sku_akhir = indeks_sku_akhir + 24
    
    for order_sku in sku_scanner2:
        find_sku = 0
        
        for nyari in sku_send:
            if nyari == order_sku:
                find_sku = 1
                
        if find_sku == 0:
            sku_send.append(order_sku)
         
        
    for search in sku_array_outbound:
    
        if sku_send == search:
            finds_outbound = 1

    if finds_outbound == 1:
        
        print(f"SKU outbound : {sku_send} gagal dikirim karena sudah pernah diterima")
        data_send_outbound = "notsukses"
        data_send_outbound_encoding = data_send_outbound +"\0"
        GateOut_sock.sendto(data_send_outbound_encoding.encode(), (IP_GateOut, PORT_GateOut))
        
        data_send_outbound = "notsukses"
        data_send_outbound_encoding = data_send_outbound +"\0"
        GateIn_sock.sendto(data_send_outbound_encoding.encode(), (IP_GateIn, PORT_GateIn))
        
    else:
        #Buat trigger ngirim banyak, untuk sekarang ngirim satu per satu, kalo udah pernah ada ga bakal dikirim
        if sku_send != []:

            sku_array_outbound.append(sku_send)
            print(f"SKU outbound berhasil diterima {sku_send} :",len(sku_send)," ",counts_outbound)
            print("")
            counts_outbound = counts_outbound + 1
        
            #-----------------------------------------------------------------
            #Raspi to database, sending tags (untuk sekarang per baca kirim)
            data_status = ""
            for per_sku_send in sku_send:
                
                # URL endpoint API di Heroku
                url_outbound = "https://octagonwms.herokuapp.com/outbound/rfid?text="
                    
                # Mengirim data menggunakan metode GET dan headers yang sudah ditentukan
                response_outbound = requests.get(url=url_outbound+per_sku_send)
                    
                # Mengecek respons dari server
                if response_outbound.status_code == 200:
                        
                    print(f"Data sku outbound {per_sku_send} berhasil dikirim ke server.")
                    
                    data_received = json.loads(response_outbound.text)
                    data_status = data_received
                    pprint.pprint(data_received)
                    print("")
                        
                else:
                    print(f"Data sku outbound {per_sku_send} gagal dikirim ke server. Status code:", response_outbound.status_code)
                    print(response_outbound.text)
                    print("")
                    
            
            complete = data_status["data"]
            
            if complete["complete"] == True:
                
                #complete[0]["complete"] == True
                data_send_outbound = "sukses\0"
                GateOut_sock.sendto(data_send_outbound.encode(), (IP_GateOut, PORT_GateOut))
                
                data_send_outbound = "sukses\0"
                GateIn_sock.sendto(data_send_outbound.encode(), (IP_GateIn, PORT_GateIn))
                
                print(f"Data status outbound : {data_send_outbound[0:6]}")
                
            else:
                
                #complete[0]["complete"] == False: ga ada feedback true
                data_send_outbound = "notsukses"
                data_send_outbound_encoding = data_send_outbound +"\0"
                GateOut_sock.sendto(data_send_outbound_encoding.encode(), (IP_GateOut, PORT_GateOut))
                
                data_send_outbound = "notsukses"
                data_send_outbound_encoding = data_send_outbound +"\0"
                GateIn_sock.sendto(data_send_outbound_encoding.encode(), (IP_GateIn, PORT_GateIn))
                print(f"Data status outbound : Should be Isolated")
            
        else:
            
            data_send_outbound = "notsukses"
            data_send_outbound_encoding = data_send_outbound +"\0"
            GateOut_sock.sendto(data_send_outbound_encoding.encode(), (IP_GateOut, PORT_GateOut))
            data_send_outbound = "notsukses"
            data_send_outbound_encoding = data_send_outbound +"\0"
            GateIn_sock.sendto(data_send_outbound_encoding.encode(), (IP_GateIn, PORT_GateIn))
            print(f"Data status outbound : Ulangi Outbound karena tidak terbaca")
          
    finds_outbound = 0
    print("")
    print("list sku outbound yang sudah diterima:",sku_array_outbound, " jumlah:",len(sku_array_outbound))
    print("--------------------------------------------------------------------------------------------------------------------------------------------")
    print("")
    print("")
    print("")
    print("")






