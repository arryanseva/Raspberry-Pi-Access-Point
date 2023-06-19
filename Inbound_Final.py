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

counts_inbound = 1
sku_array_inbound = []
finds_inbound = 0

counts_outbound = 1
sku_array_outbound = []
finds_outbound = 0


while True:
    
    print("--------------------------------------------------------------------------------------------------------------------------------------------")
    print("#Gate Scanner Inbound Ready to Reading#")
    print("#PRESS THE BUTTON#")
    print("")
    print("Menunggu input dari scanner 1....")

    #Standby siap menerima data dari gatescanner 1
    data_inbound, addr_inbound = sock.recvfrom(4096)
    
    i_inbound = 0
    arry_inbound = []
    ### Fungsi Konversi bytes to string - Start
    for elemen in data_inbound:
        arry_inbound.append(elemen)
        
    j_inbound=0
    arry_bytes_inbound =[]

    for elemen in arry_inbound:
        
        data_decimal_inbound = elemen & 0xFF
        data_hex_inbound = hex(data_decimal_inbound)
        data_bytes_inbound = int(data_hex_inbound,16).to_bytes(1,byteorder='big')

        arry_bytes_inbound.append(data_bytes_inbound)
        j_inbound=j_inbound+1

    arry_bytes_str_inbound = []

    for elemen in arry_bytes_inbound:
        hex_x_inbound = hex(elemen[0])[2:]
        if len(hex_x_inbound) < 2:
            hex_x_inbound = '0'+ hex_x_inbound
        arry_bytes_str_inbound.append(hex_x_inbound)

    sku_inbound = ""

    for elemen_sku in arry_bytes_str_inbound:
        sku_inbound = sku_inbound + elemen_sku

    sku_inbound = sku_inbound.upper()
    print(f"sukses diterima awal inbound scanner 1 : {sku_inbound}")
  
    ### Fungsi Konversi bytes to string - End
    sku_send = []
    jumlah_sku = int((len(sku_inbound))/24)
    indeks_sku_awal = 0
    indeks_sku_akhir = 24

    for order_sku in range(jumlah_sku):
        
        sku_send.append(sku_inbound[indeks_sku_awal:indeks_sku_akhir])
        indeks_sku_awal = indeks_sku_awal + 24
        indeks_sku_akhir = indeks_sku_akhir + 24
    
    print("Menunggu input dari scanner 2....")
    
    #Standby siap menerima data dari gatescanner 2
    data_inbound, addr_inbound = sock.recvfrom(4096)

    ### Fungsi Konversi bytes to string - Start
    i_inbound = 0
    arry_inbound = []

    for elemen in data_inbound:
        arry_inbound.append(elemen)
        

    j_inbound=0
    arry_bytes_inbound =[]

    for elemen in arry_inbound:
        
        data_decimal_inbound = elemen & 0xFF
        data_hex_inbound = hex(data_decimal_inbound)
        data_bytes_inbound = int(data_hex_inbound,16).to_bytes(1,byteorder='big')

        arry_bytes_inbound.append(data_bytes_inbound)
        j_inbound=j_inbound+1

    arry_bytes_str_inbound = []

    for elemen in arry_bytes_inbound:
        hex_x_inbound = hex(elemen[0])[2:]
        if len(hex_x_inbound) < 2:
            hex_x_inbound = '0'+ hex_x_inbound
        arry_bytes_str_inbound.append(hex_x_inbound)

    sku_inbound = ""

    for elemen_sku in arry_bytes_str_inbound:
        sku_inbound = sku_inbound + elemen_sku

    sku_inbound = sku_inbound.upper()
    print(f"sukses diterima awal inbound scanner 2 : {sku_inbound}")
  
    ### Fungsi Konversi bytes to string - End
    sku_scanner2 = []
    jumlah_sku = int((len(sku_inbound))/24)
    indeks_sku_awal = 0
    indeks_sku_akhir = 24

    for order_sku in range(jumlah_sku):
        
        sku_scanner2.append(sku_inbound[indeks_sku_awal:indeks_sku_akhir])
        indeks_sku_awal = indeks_sku_awal + 24
        indeks_sku_akhir = indeks_sku_akhir + 24

    ### Fungsi Complement SKU - Start
    for order_sku in sku_scanner2:
        find_sku = 0
        
        for nyari in sku_send:
            if nyari == order_sku:
                find_sku = 1
                
        if find_sku == 0:
            sku_send.append(order_sku)
        
    ### Fungsi Complement SKU - End

    ### Fungsi Check SKU - Start
    for search in sku_array_inbound:
        
        if sku_send == search:
            finds_inbound = 1
    ### Fungsi Check SKU - End
  
    if finds_inbound == 1:
        
        print(f"SKU inbound : {sku_send} gagal dikirim karena sudah pernah diterima")
        
        data_send_inbound = "notsukses"
        data_send_inbound_encoding = data_send_inbound +"\0"
        GateIn_sock.sendto(data_send_inbound_encoding.encode(), (IP_GateIn, PORT_GateIn))
        
        data_send_inbound = "notsukses"
        data_send_inbound_encoding = data_send_inbound +"\0"
        GateOut_sock.sendto(data_send_inbound_encoding.encode(), (IP_GateOut, PORT_GateOut))
        
    else:
        #Buat trigger ngirim banyak, untuk sekarang ngirim satu per satu, kalo udah pernah ada ga bakal dikirim
        if sku_send != []:

            sku_array_inbound.append(sku_send)
            print(f"SKU inbound berhasil diterima : {sku_send} :",len(sku_send)," ",counts_inbound)
            print("")
            counts_inbound = counts_inbound + 1

            #Mencari tahu apakah SKU seragam atau tidak, jika tidak auto barang harus diisolasi
            count_qoly = 0
            one_sku = sku_send[0][0:6]
            for checker in sku_send:
                if one_sku == checker[0:6]:
                    count_qoly = count_qoly + 1
            
            if count_qoly == len(sku_send) :    
                #-----------------------------------------------------------------
                #Raspi to database, sending tags (untuk sekarang per nerima dari data akuisisi kirim)
                error = 0

                ## Fungsi Send SKU - Start
                for per_sku_send in sku_send:
                    
                    # URL endpoint API di Heroku
                    url_inbound = "https://octagonwms.herokuapp.com/inbound/rfid?text="
                        
                    # Mengirim data menggunakan metode GET dan headers yang sudah ditentukan
                    response_inbound = requests.get(url=url_inbound+per_sku_send)
                        
                    # Mengecek respons dari server
                    if response_inbound.status_code == 200:
                            
                        print(f"Data sku inbound {per_sku_send} berhasil dikirim ke server.")
                        
                        data_received = json.loads(response_inbound.text)
                        pprint.pprint(data_received)
                        print("")
                            
                    else:
                        print(f"Data sku inbound {per_sku_send} gagal dikirim ke server. Status code:", response_inbound.status_code)
                        print(response_inbound.text)
                        print("")
                        error = error + 1
                ## Fungsi Send SKU - End

                #Memastikan apakah ada eror selama pengiriman, jika ada maka isolasi barang 
                if error == 0 :

                    ## Fungsi Pull Respons - Start
                    url_done = "https://octagonwms.herokuapp.com/inbound/isdone"

                    # Data string yang akan dikirim ke server
                    data_done = {"id" : 1,
                                "check" : True}
                    
                    json_data_done = json.dumps(data_done)
                    headers_done ={'Content-type': 'application/json'}
                    response_done = requests.put(url=url_done, data=json_data_done, headers=headers_done)
                    
                    data_received_done = ""
                    # Mengecek respons dari server
                    if response_done.status_code == 200:
                        print("Data Pallet inbound telah berhasil dikirim")
                        
                        data_received_done = json.loads(response_done.text)
                        pprint.pprint(data_received_done)
                        print("")
                            
                    else:
                        print("Data Pallet inbound gagal dikirim ke server. Status code:", response_done.status_code)
                        print(response_done.text)
                    
                    if data_received_done == "":
                        
                        data_send_inbound = "notsukses"
                        data_send_inbound_encoding = data_send_inbound +"\0"
                        GateIn_sock.sendto(data_send_inbound_encoding.encode(), (IP_GateIn, PORT_GateIn))
                        
                        data_send_inbound = "notsukses"
                        data_send_inbound_encoding = data_send_inbound +"\0"
                        GateOut_sock.sendto(data_send_inbound_encoding.encode(), (IP_GateOut, PORT_GateOut))
                        
                        print(f"Data status inbound : Should be Isolated")
                    
                    else:
                        
                        complete = data_received_done["data"]
                        
                        if complete == []:
                            
                            #complete[0]["complete"] == True
                            data_send_inbound = "sukses\0"
                            GateIn_sock.sendto(data_send_inbound.encode(), (IP_GateIn, PORT_GateIn))
                            
                            data_send_inbound = "sukses\0"
                            GateOut_sock.sendto(data_send_inbound.encode(), (IP_GateOut, PORT_GateOut))
                            print(f"Data status inbound : {data_send_inbound[0:6]}")
                            
                        else:
                            
                            #complete[0]["complete"] == False: ga ada feedback true
                            data_send_inbound = "notsukses"
                            data_send_inbound_encoding = data_send_inbound +"\0"
                            GateIn_sock.sendto(data_send_inbound_encoding.encode(), (IP_GateIn, PORT_GateIn))
                            
                            data_send_inbound = "notsukses"
                            data_send_inbound_encoding = data_send_inbound +"\0"
                            GateOut_sock.sendto(data_send_inbound_encoding.encode(), (IP_GateOut, PORT_GateOut))
                            
                            print(f"Data status inbound : Should be Isolated")
                     
                    ## Fungsi Pull Respons - End
                else:
                    data_send_inbound = "notsukses"
                    data_send_inbound_encoding = data_send_inbound +"\0"
                    GateIn_sock.sendto(data_send_inbound_encoding.encode(), (IP_GateIn, PORT_GateIn))
                    
                    data_send_inbound = "notsukses"
                    data_send_inbound_encoding = data_send_inbound +"\0"
                    GateOut_sock.sendto(data_send_inbound_encoding.encode(), (IP_GateOut, PORT_GateOut))
                    
                    print(f"Data status inbound : Should be Isolated")
            else:
                data_send_inbound = "notsukses"
                data_send_inbound_encoding = data_send_inbound +"\0"
                GateIn_sock.sendto(data_send_inbound_encoding.encode(), (IP_GateIn, PORT_GateIn))
                
                data_send_inbound = "notsukses"
                data_send_inbound_encoding = data_send_inbound +"\0"
                GateOut_sock.sendto(data_send_inbound_encoding.encode(), (IP_GateOut, PORT_GateOut))
                
                print(f"Data status inbound : Should be Isolated")
                
        else:
            data_send_inbound = "notsukses"
            data_send_inbound_encoding = data_send_inbound +"\0"
            GateIn_sock.sendto(data_send_inbound_encoding.encode(), (IP_GateIn, PORT_GateIn))
            
            data_send_inbound = "notsukses"
            data_send_inbound_encoding = data_send_inbound +"\0"
            GateOut_sock.sendto(data_send_inbound_encoding.encode(), (IP_GateOut, PORT_GateOut))
            
            print(f"Data status inbound : Ulangi Inbound karena tidak terbaca")

    finds_inbound = 0
    print("")
    print("list palet inbound yang sudah diterima:",sku_array_inbound, " jumlah palet:",len(sku_array_inbound))
    print("--------------------------------------------------------------------------------------------------------------------------------------------")
    print("")
    print("")
    print("")
    print("")
