import socket
import requests
import json
import pprint
import time
import threading

global UDP_IP
global UDP_PORT_1
global UDP_PORT_2
global sock1 
global sock2 
global ip_sock 
global ip_status

global first_sock
global second_sock
global coordinate_rack

global counts_stocking
global sku_array_stocking
global finds_stocking

global ip_coor
global addr_sku
global ip_port
global coor_ip
global coor_coorId
global port_socket
global state_stocking

UDP_IP = "192.168.4.1"
UDP_PORT_1 = 49153
sock1 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock1.settimeout(5)
sock1.bind((UDP_IP,UDP_PORT_1))

UDP_PORT_2 = 49154
sock2 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock2.settimeout(5)
sock2.bind((UDP_IP,UDP_PORT_2))

ip_sock = {"192.168.4.7" : sock1,
           "192.168.4.8" : sock2}
ip_status = {"192.168.4.7" : "OFF",
           "192.168.4.8" : "OFF"}

first_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #keep dulu perhatiin file 2esp32,10esp32non dan filtered
second_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #keep dulu 

coordinate_rack = ["A11","A21"]

counts_stocking = 1
sku_array_stocking = []
finds_stocking = 0

ip_coor = {"192.168.4.7" : "A11",
           "192.168.4.8" : "A21"}
addr_sku = {"192.168.4.7" : "",
           "192.168.4.8" : ""}
ip_port = {"192.168.4.7" : 1236,
           "192.168.4.8" : 1237}
coor_ip = {"A11" : "192.168.4.7",
           "A21" : "192.168.4.8"}
coor_coorId = {"A11" : "1",
               "A21" : "2"}
port_socket = {"1236" : first_sock,
               "1237" : second_sock}
state_stocking = []

### Fungsi Finding State Stocking - Start
def searching():
    while True :
        time.sleep(1)
        print(f"state stocking : {state_stocking}")
        
        # URL endpoint API di Heroku Log Activity
        url_log_stocking = "https://octagonwms.herokuapp.com/coord"

        # Mengirim data menggunakan metode GET dan headers yang sudah ditentukan
        response_log_stocking = requests.get(url=url_log_stocking)

        # Mengecek respons dari server
        if response_log_stocking.status_code == 200:
            print("Data berhasil dikirim ke server.")
                        
            data_received_log_stocking = json.loads(response_log_stocking.text)
            pprint.pprint(data_received_log_stocking)
            print("")
            
            for data in data_received_log_stocking:
                if (data["isFull"] == True and data["isUp"] == True and data["isChecked"] == False and data["isRequested"] == False and data["isDown"] == False):
                    ### Fungsi Pull Data Barang - Start
                    coordinat_stocking = data["blok"] + str(data["level"]) + str(data["nomor_rak"])
                    coordinat_id_stocking = str(data["id"])
                    add_state_stocking = {"coordinat_stocking" : coordinat_stocking,
                                          "coordinat_id_stocking" : coordinat_id_stocking,
                                          "status" : "ON",
                                          "unique_key_stocking": ""}
                    
                     # URL endpoint API di Heroku
                    url_cd_stocking = "https://octagonwms.herokuapp.com/opname"
                    response_cd_stocking = requests.get(url=url_cd_stocking)
                    
                    # Mengecek respons dari server
                    if response_cd_stocking.status_code == 200:
                        
                        print("Data berhasil dikirim ke server.")
                            
                        data_received_cd_stocking = json.loads(response_cd_stocking.text)
                        pprint.pprint(data_received_cd_stocking)
                        print("")
                        
                        for data_opname in data_received_cd_stocking["data"] :
                            if str(data_opname["coordinate_id"]) == str(add_state_stocking["coordinat_id_stocking"]):
                                    add_state_stocking["unique_key_stocking"] = data_opname["unique_key"]
                    else:
                        print("Data gagal dikirim ke server. Status code:", response_cd_stocking.status_code)
                        print(response_cd_stocking.text)
                        
                    print("")
                    ### Fungsi Pull Data Barang - End
                           
                    find = 0 
                    for i in range (5):
                        
                        url_log_stocking2 = "https://octagonwms.herokuapp.com/coord"
                        response_log_stocking2 = requests.get(url=url_log_stocking2)
                        
                        if response_log_stocking2.status_code == 200:
                            print("Data berhasil dikirim ke server.")
                                        
                            data_received_log_stocking2 = json.loads(response_log_stocking2.text)
                            pprint.pprint(data_received_log_stocking2)
                            print("")
                            
                            for data2 in data_received_log_stocking2 :
                                if data2 == data:
                                    find = find + 1
                                    
                        else:
                            print("Data gagal dikirim ke server. Status code:", response_log_stocking2.status_code)
                            print(response_log_stocking2.text)
                    
                    if find == 5 :
                            
                        if len(state_stocking) == 0:
                            state_stocking.append(add_state_stocking)
                        else:
                            found_state = 0 
                            for elemen in state_stocking :
                                if elemen == add_state_stocking:
                                    found_state = 1
                            
                            if found_state == 0:
                                state_stocking.append(add_state_stocking)
                    else:
                        find = 0
                #Pembatalan Proses Stocking    
                if (data["isFull"] == True and data["isUp"] == False and data["isChecked"] == False and data["isRequested"] == False and data["isDown"] == False):
                    coordinat_stocking_cancel = data["blok"] + str(data["level"]) + str(data["nomor_rak"])
                    coordinat_id_stocking_cancel = str(data["id"])
                    add_state_stocking_cancel = {"coordinat_stocking" : coordinat_stocking_cancel,
                                          "coordinat_id_stocking" : coordinat_id_stocking_cancel,
                                          "status" : "OFF",
                                          "unique_key_stocking": ""}
                    
                     # URL endpoint API di Heroku
                    url_cd_stocking = "https://octagonwms.herokuapp.com/opname"
                    response_cd_stocking = requests.get(url=url_cd_stocking)
                    
                    # Mengecek respons dari server
                    if response_cd_stocking.status_code == 200:
                        
                        print("Data berhasil dikirim ke server.")
                            
                        data_received_cd_stocking = json.loads(response_cd_stocking.text)
                        pprint.pprint(data_received_cd_stocking)
                        print("")
                        
                        for data_opname in data_received_cd_stocking["data"] :
                            if str(data_opname["coordinate_id"]) == str(add_state_stocking_cancel["coordinat_id_stocking"]):
                                    add_state_stocking_cancel["unique_key_stocking"] = data_opname["unique_key"]
                    else:
                        print("Data gagal dikirim ke server. Status code:", response_cd_stocking.status_code)
                        print(response_cd_stocking.text)
                        
                    print("")
                    
                    
                    if len(state_stocking) > 0:
                        for data_state_stocking in state_stocking :
                            print(f"data_state_stocking : {data_state_stocking}")
                            print(f"add_state_stocking_cancel : {add_state_stocking_cancel}")
                            if (data_state_stocking["coordinat_stocking"] == add_state_stocking_cancel["coordinat_stocking"] and data_state_stocking["coordinat_id_stocking"] == add_state_stocking_cancel["coordinat_id_stocking"] and data_state_stocking["unique_key_stocking"] == add_state_stocking_cancel["unique_key_stocking"] and data_state_stocking["status"] == "ON"):
                                data_state_stocking["status"] = add_state_stocking_cancel["status"]                    
                                
        else:
            print("Data gagal dikirim ke server. Status code:", response_log_stocking.status_code)
            print(response_log_stocking.text)
            
        print("")
### Fungsi Finding State Stocking - End

def rack1():
    while True :
        
        if len(state_stocking) != 0:
            # State Stocking ditemukan di rak 1
            for coordinate in state_stocking:
                
                if coordinate["coordinat_stocking"] == "A11":
                
                    match_stocking = 0
                    
                    while match_stocking != 1 :
                        time.sleep(1)
                        ### Fungsi Rack Scanner Mode Control - Start
                        data_send_stocking = str(1) #Menyalakan Rack Scanner
                        data_send_encode_stocking = data_send_stocking + "\0"
                        port_socket[str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])].sendto(data_send_encode_stocking.encode(), (coor_ip[coordinate["coordinat_stocking"]], ip_port[coor_ip[coordinate["coordinat_stocking"]]]))
                        print("Data "+str(data_send_stocking)+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_stocking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])+" untuk menyalakan Rack Scanner. (Stocking)")
                        ### Fungsi Rack Scanner Mode Control - End
                        try:
                            data_stocking, addr_stocking = ip_sock[coor_ip[coordinate["coordinat_stocking"]]].recvfrom(4096)
                            
                            #data bytes dari ESP32 diubah menjadi array of integer
                            ### Fungsi Konversi bytes to string - Start
                            i_stocking = 0
                            arry_stocking = []

                            
                            for elemen in data_stocking:
                                #print("data byte ke ",i+1,": ",elemen,end="")
                                arry_stocking.append(elemen)
                                #print(", tipe data",type(arry[i]))
                                i_stocking=i_stocking+1
                                
                            j_stocking=0
                            arry_bytes_stocking =[]
                            
                            for elemen in arry_stocking:
                                data_decimal_stocking = elemen & 0xFF
                                data_hex_stocking = hex(data_decimal_stocking)
                                data_bytes_stocking = int(data_hex_stocking,16).to_bytes(1,byteorder='big')
                                arry_bytes_stocking.append(data_bytes_stocking)
                                j_stocking=j_stocking+1
                            
                            arry_bytes_str_stocking = []

                            for elemen in arry_bytes_stocking:
                                hex_x_stocking = hex(elemen[0])[2:]
                                if len(hex_x_stocking) < 2:
                                    hex_x_stocking = '0'+ hex_x_stocking
                                arry_bytes_str_stocking.append(hex_x_stocking)
                            
                            sku_stocking = ""
                            
                            for elemen_sku in arry_bytes_str_stocking:
                                sku_stocking = sku_stocking + elemen_sku
                            
                            sku_stocking = sku_stocking.upper() #cuma nerima dan ngirim 1 SKU
                            print(f"SKU tocking : {sku_stocking}")
                            ### Fungsi Konversi bytes to string - End
                                   
                            ### Fungsi Stocking Behavioral - Start
                            if sku_stocking != "00":
                                
                                sku_send = []
                                jumlah_sku = int((len(sku_stocking))/24)
                                indeks_sku_awal = 0
                                indeks_sku_akhir = 24
                                
                                for order_sku in range(jumlah_sku):
                                    
                                    sku_send.append(sku_stocking[indeks_sku_awal:indeks_sku_akhir])
                                    indeks_sku_awal = indeks_sku_awal + 24
                                    indeks_sku_akhir = indeks_sku_akhir + 24
                                    
                                print(f"SKU : {sku_send}")
                                
                                count_qoly = 0
                                
                                for per_sku in sku_send:
                                    
                                    if per_sku[0:6] == coordinate["unique_key_stocking"]:
                                        count_qoly = count_qoly + 1
                                
                                print(f"qoly : {count_qoly}")
                                nyamain = int(per_sku[12:16])
                                print(f"qtt pallet : {nyamain}")
                                
                                if coordinate["status"] == "OFF":
                                    match_stocking = 1
                                    
                                else:
                                    
                                    if count_qoly == int(per_sku[12:16]) :
                                        
                                        if coordinate["status"] == "OFF":
                                            match_stocking = 1
                                        else:
                                            match_stocking = 1
                                    
                                    else:
                                        if coordinate["status"] == "OFF":
                                            match_stocking = 1
                                        else:
                                            reply_stocking = "notsukses"
                                            reply_encode_stocking = reply_stocking + "\0"
                                            port_socket[str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])].sendto(reply_encode_stocking.encode(), (coor_ip[coordinate["coordinat_stocking"]], ip_port[coor_ip[coordinate["coordinat_stocking"]]]))
                                            print("Data "+str(reply_stocking)+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_stocking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])+" untuk menunggu stocking. (Stocking)")
                                            
                                
                            else:
                                if coordinate["status"] == "OFF":
                                    match_stocking = 1             
                                    
                                else: #sku_stocking == "00" and coordinate["status"] == "ON": #buat sku kosong
                                    
                                    print("Stocking for rack ("+coordinate["coordinat_stocking"]+") with SKU ("+coordinate["unique_key_stocking"]+ ") still on going......")
                                    
                                    reply_stocking = "standby"
                                    reply_encode_stocking = reply_stocking + "\0"
                                    port_socket[str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])].sendto(reply_encode_stocking.encode(), (coor_ip[coordinate["coordinat_stocking"]], ip_port[coor_ip[coordinate["coordinat_stocking"]]]))
                                    print("Data "+str(reply_stocking)+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_stocking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])+" untuk menunggu stocking. (Stocking)")
                                    
                            ### Fungsi Stocking Behavioral - End    
                            print("")
                    
                        except socket.timeout:
                            
                            reply_stocking = "notsukses"
                            reply_encode_stocking = reply_stocking + "\0"
                            port_socket[str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])].sendto(reply_encode_stocking.encode(), (coor_ip[coordinate["coordinat_stocking"]], ip_port[coor_ip[coordinate["coordinat_stocking"]]]))
                            print("Data "+str(reply_stocking)+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_stocking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])+" untuk menunggu stocking. (Stocking)")
                            
                            continue
                
                    reply_stocking = "sukses"
                    reply_encode_stocking = reply_stocking + "\0"
                    port_socket[str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])].sendto(reply_encode_stocking.encode(), (coor_ip[coordinate["coordinat_stocking"]], ip_port[coor_ip[coordinate["coordinat_stocking"]]]))
                    print("Data "+str(reply_stocking)+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_stocking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])+" telah berhasil stocking. (Stocking)")
                    
                    if (match_stocking == 1 and coordinate["status"] == "ON"):

                        ### Fungsi Status Updater - Start
                        # URL endpoint API di Heroku
                        url_stocking = "https://octagonwms.herokuapp.com/coord/check"

                        # Data string yang akan dikirim ke server
                        data_stocking = { 'id' : int(coordinate["coordinat_id_stocking"]),
                                 'check' : True}

                        json_data_stocking = json.dumps(data_stocking)
                        headers_stocking ={'Content-type': 'application/json'}
                        # Mengirim data menggunakan metode POST dan headers yang sudah ditentukan
                        response_stocking = requests.put(url=url_stocking, data=json_data_stocking, headers=headers_stocking )
                        ### Fungsi Status Updater - End
           
                        # Mengecek respons dari server
                        if response_stocking.status_code == 200:
                            state_stocking.remove(coordinate)
                            print("")
                            print("Data berhasil dikirim ke server dan stocking berhasil.")
                            

                        else:
                            print("Data gagal dikirim ke server. Status code:", response_stocking.status_code)
                            state_stocking.remove(coordinate)
                            print(response_stocking.text)
                                   

                        print("")
                        
                           
                    if (match_stocking == 1 and coordinate["status"] == "OFF"):
                        state_stocking.remove(coordinate)
                        
def rack2():
    while True :
        
        if len(state_stocking) != 0:
            #State Stocking ditemukan di rak 2
            for coordinate in state_stocking:
                
                if coordinate["coordinat_stocking"] == "A21":
                
                    match_stocking = 0
                    
                    while match_stocking != 1 :
                        time.sleep(1)
                        ### Fungsi Rack Scanner Mode Control - Start
                        data_send_stocking = str(1) #Menyalakan Rack Scanner
                        data_send_encode_stocking = data_send_stocking + "\0"
                        port_socket[str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])].sendto(data_send_encode_stocking.encode(), (coor_ip[coordinate["coordinat_stocking"]], ip_port[coor_ip[coordinate["coordinat_stocking"]]]))
                        print("Data "+str(data_send_stocking)+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_stocking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])+" untuk menyalakan Rack Scanner. (Stocking)")
                        ### Fungsi Rack Scanner Mode Control - End
                               
                        try:
                            data_stocking, addr_stocking = ip_sock[coor_ip[coordinate["coordinat_stocking"]]].recvfrom(4096)
                            
                            #data bytes dari ESP32 diubah menjadi array of integer
                            ### Fungsi Konversi bytes to string - Start
                            i_stocking = 0
                            arry_stocking = []

                            
                            for elemen in data_stocking:
                                #print("data byte ke ",i+1,": ",elemen,end="")
                                arry_stocking.append(elemen)
                                #print(", tipe data",type(arry[i]))
                                i_stocking=i_stocking+1
                                
                            j_stocking=0
                            arry_bytes_stocking =[]
                            
                            for elemen in arry_stocking:
                                data_decimal_stocking = elemen & 0xFF
                                data_hex_stocking = hex(data_decimal_stocking)
                                data_bytes_stocking = int(data_hex_stocking,16).to_bytes(1,byteorder='big')
                                arry_bytes_stocking.append(data_bytes_stocking)
                                j_stocking=j_stocking+1
                            
                            arry_bytes_str_stocking = []

                            for elemen in arry_bytes_stocking:
                                hex_x_stocking = hex(elemen[0])[2:]
                                if len(hex_x_stocking) < 2:
                                    hex_x_stocking = '0'+ hex_x_stocking
                                arry_bytes_str_stocking.append(hex_x_stocking)
                            
                            sku_stocking = ""
                            
                            for elemen_sku in arry_bytes_str_stocking:
                                sku_stocking = sku_stocking + elemen_sku
                            
                            sku_stocking = sku_stocking.upper() #cuma nerima dan ngirim 1 SKU
                            print(f"SKU tocking : {sku_stocking}")
                            ### Fungsi Konversi bytes to string - End

                            ### Fungsi Stocking Behavioral - Start
                            if sku_stocking != "00":
                                
                                sku_send = []
                                jumlah_sku = int((len(sku_stocking))/24)
                                indeks_sku_awal = 0
                                indeks_sku_akhir = 24
                                
                                for order_sku in range(jumlah_sku):
                                    
                                    sku_send.append(sku_stocking[indeks_sku_awal:indeks_sku_akhir])
                                    indeks_sku_awal = indeks_sku_awal + 24
                                    indeks_sku_akhir = indeks_sku_akhir + 24
                                    
                                print(f"SKU : {sku_send}")
                                
                                count_qoly = 0
                                
                                for per_sku in sku_send:
                                    
                                    if per_sku[0:6] == coordinate["unique_key_stocking"]:
                                        count_qoly = count_qoly + 1
                                
                                print(f"qoly : {count_qoly}")
                                nyamain = int(per_sku[12:16])
                                print(f"qtt pallet : {nyamain}")
                                
                                if coordinate["status"] == "OFF":
                                    match_stocking = 1
                                    
                                else:
                                    if count_qoly == int(per_sku[12:16]) :
                                        
                                        if coordinate["status"] == "OFF":
                                            match_stocking = 1
                                        else:
                                            match_stocking = 1
                                    
                                    else:
                                        if coordinate["status"] == "OFF":
                                            match_stocking = 1
                                        else:
                                            reply_stocking = "notsukses"
                                            reply_encode_stocking = reply_stocking + "\0"
                                            port_socket[str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])].sendto(reply_encode_stocking.encode(), (coor_ip[coordinate["coordinat_stocking"]], ip_port[coor_ip[coordinate["coordinat_stocking"]]]))
                                            print("Data "+str(reply_stocking)+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_stocking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])+" untuk menunggu stocking. (Stocking)")
                                               
                            else:
                                if coordinate["status"] == "OFF":
                                    match_stocking = 1             
                                    
                                else: #sku_stocking == "00" and coordinate["status"] == "ON": #buat sku kosong
                                    
                                    print("Stocking for rack ("+coordinate["coordinat_stocking"]+") with SKU ("+coordinate["unique_key_stocking"]+ ") still on going......")
                                    
                                    reply_stocking = "standby"
                                    reply_encode_stocking = reply_stocking + "\0"
                                    port_socket[str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])].sendto(reply_encode_stocking.encode(), (coor_ip[coordinate["coordinat_stocking"]], ip_port[coor_ip[coordinate["coordinat_stocking"]]]))
                                    print("Data "+str(reply_stocking)+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_stocking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])+" untuk menunggu stocking. (Stocking)")
                                    
                                
                            print("")
                            ### Fungsi Stocking Behavioral - End
                               
                        except socket.timeout:
                            
                            reply_stocking = "notsukses"
                            reply_encode_stocking = reply_stocking + "\0"
                            port_socket[str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])].sendto(reply_encode_stocking.encode(), (coor_ip[coordinate["coordinat_stocking"]], ip_port[coor_ip[coordinate["coordinat_stocking"]]]))
                            print("Data "+str(reply_stocking)+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_stocking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])+" untuk menunggu stocking. (Stocking)")
                            
                            continue
                
                    reply_stocking = "sukses"
                    reply_encode_stocking = reply_stocking + "\0"
                    port_socket[str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])].sendto(reply_encode_stocking.encode(), (coor_ip[coordinate["coordinat_stocking"]], ip_port[coor_ip[coordinate["coordinat_stocking"]]]))
                    print("Data "+str(reply_stocking)+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_stocking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_stocking"]]])+" telah berhasil stocking. (Stocking)")
                    
                    if (match_stocking == 1 and coordinate["status"] == "ON"):
                               
                        ### Fungsi Status Updater - Start
                        # URL endpoint API di Heroku
                        url_stocking = "https://octagonwms.herokuapp.com/coord/check"

                        # Data string yang akan dikirim ke server
                        data_stocking = { 'id' : int(coordinate["coordinat_id_stocking"]),
                                 'check' : True}

                        json_data_stocking = json.dumps(data_stocking)
                        headers_stocking ={'Content-type': 'application/json'}
                        # Mengirim data menggunakan metode POST dan headers yang sudah ditentukan
                        response_stocking = requests.put(url=url_stocking, data=json_data_stocking, headers=headers_stocking )
                        ### Fungsi Status Updater - End

                        # Mengecek respons dari server
                        if response_stocking.status_code == 200:
                            state_stocking.remove(coordinate)
                            print("")
                            print("Data berhasil dikirim ke server dan stocking berhasil.")
                            

                        else:
                            print("Data gagal dikirim ke server. Status code:", response_stocking.status_code)
                            state_stocking.remove(coordinate)
                            print(response_stocking.text)

                        print("")
                        
                    if (match_stocking == 1 and coordinate["status"] == "OFF"):
                        state_stocking.remove(coordinate)


t1 = threading.Thread(target=searching)
t1.start()
           
t2 = threading.Thread(target=rack1)
t2.start()

t3 = threading.Thread(target=rack2)
t3.start()





