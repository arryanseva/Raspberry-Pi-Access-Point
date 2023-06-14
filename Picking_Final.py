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

global counts_picking
global sku_array_picking
global finds_picking

global ip_coor
global addr_sku
global ip_port
global coor_ip
global coor_coorId
global port_socket
global state_picking

UDP_IP = "192.168.4.1"
UDP_PORT_1 = 49157
sock1 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock1.settimeout(5)
sock1.bind((UDP_IP,UDP_PORT_1))

UDP_PORT_2 = 49158
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

counts_picking = 1
sku_array_picking = []
finds_picking = 0

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
state_picking = []

def searching():
    while True :
        time.sleep(3)
        
        print(f"state picking : {state_picking}")
        # URL endpoint API di Heroku Log Activity
        url_log_picking = "https://octagonwms.herokuapp.com/coord"

        # Mengirim data menggunakan metode GET dan headers yang sudah ditentukan
        response_log_picking = requests.get(url=url_log_picking)

        # Mengecek respons dari server
        if response_log_picking.status_code == 200:
            print("Data berhasil dikirim ke server.")
                        
            data_received_log_picking = json.loads(response_log_picking.text)
            pprint.pprint(data_received_log_picking)
            print("")
            
            ####CUMA 1 picking yang harus isfull :true  dan ischecked :false
            for data in data_received_log_picking:
                if (data["isFull"] == True and data["isUp"] == True and data["isChecked"] == True and data["isRequested"] == True and data["isDown"] == True):
                    coordinat_picking = data["blok"] + str(data["level"]) + str(data["nomor_rak"])
                    coordinat_id_picking = str(data["id"])
                    add_state_picking = {"coordinat_picking" : coordinat_picking,
                                          "coordinat_id_picking" : coordinat_id_picking,
                                          "status" : "ON",
                                          "unique_key_picking": ""}
                    
                     # URL endpoint API di Heroku
                    url_cd_picking = "https://octagonwms.herokuapp.com/opname"
                    response_cd_picking = requests.get(url=url_cd_picking)
                    
                    # Mengecek respons dari server
                    if response_cd_picking.status_code == 200:
                        
                        print("Data berhasil dikirim ke server.")
                            
                        data_received_cd_picking = json.loads(response_cd_picking.text)
                        pprint.pprint(data_received_cd_picking)
                        print("")
                        
                        for data_opname in data_received_cd_picking["data"] :
                            if str(data_opname["coordinate_id"]) == str(add_state_picking["coordinat_id_picking"]):
                                    add_state_picking["unique_key_picking"] = data_opname["unique_key"]
                    else:
                        print("Data gagal dikirim ke server. Status code:", response_cd_picking.status_code)
                        print(response_cd_picking.text)
                        
                    print("")
                    
                    find = 0 
                    for i in range (5):
                        url_log_picking2 = "https://octagonwms.herokuapp.com/coord"
                        response_log_picking2 = requests.get(url=url_log_picking2)
                        
                        if response_log_picking2.status_code == 200:
                            print("Data berhasil dikirim ke server.")
                                        
                            data_received_log_picking2 = json.loads(response_log_picking2.text)
                            pprint.pprint(data_received_log_picking2)
                            print("")
                            
                            for data2 in data_received_log_picking2 :
                                if data2 == data:
                                    find = find + 1
                        else:
                            print("Data gagal dikirim ke server. Status code:", response_log_picking2.status_code)
                            print(response_log_picking2.text)
                    
                    if find == 5:
                        if len(state_picking) == 0:
                            state_picking.append(add_state_picking)
                        else:
                            found_state = 0 
                            for elemen in state_picking :
                                if elemen == add_state_picking:
                                    found_state = 1
                            
                            if found_state == 0:
                                state_picking.append(add_state_picking)
                    else:
                        find = 0 
                
                if (data["isFull"] == True and data["isUp"] == True and data["isChecked"] == True and data["isRequested"] == True and data["isDown"] == False):
                    coordinat_picking_cancel = data["blok"] + str(data["level"]) + str(data["nomor_rak"])
                    coordinat_id_picking_cancel = str(data["id"])
                    add_state_picking_cancel = {"coordinat_picking" : coordinat_picking_cancel,
                                          "coordinat_id_picking" : coordinat_id_picking_cancel,
                                          "status" : "OFF",
                                          "unique_key_picking": ""}
                    
                     # URL endpoint API di Heroku
                    url_cd_picking = "https://octagonwms.herokuapp.com/opname"
                    response_cd_picking = requests.get(url=url_cd_picking)
                    
                    # Mengecek respons dari server
                    if response_cd_picking.status_code == 200:
                        
                        print("Data berhasil dikirim ke server.")
                            
                        data_received_cd_picking = json.loads(response_cd_picking.text)
                        pprint.pprint(data_received_cd_picking)
                        print("")
                        
                        for data_opname in data_received_cd_picking["data"] :
                            if str(data_opname["coordinate_id"]) == str(add_state_picking_cancel["coordinat_id_picking"]):
                                    add_state_picking_cancel["unique_key_picking"] = data_opname["unique_key"]
                    else:
                        print("Data gagal dikirim ke server. Status code:", response_cd_picking.status_code)
                        print(response_cd_picking.text)
                        
                    print("")
                
                    if len(state_picking) > 0:
                        for data_state_picking in state_picking :
                            print(f"data_state_picking : {data_state_picking}")
                            print(f"add_state_picking_cancel : {add_state_picking_cancel}")
                            
                            if (data_state_picking["coordinat_picking"] == add_state_picking_cancel["coordinat_picking"] and data_state_picking["coordinat_id_picking"] == add_state_picking_cancel["coordinat_id_picking"] and data_state_picking["unique_key_picking"] == add_state_picking_cancel["unique_key_picking"] and data_state_picking["status"] == "ON"):
                                data_state_picking["status"] = add_state_picking_cancel["status"]
        else:
            print("Data gagal dikirim ke server. Status code:", response_log_picking.status_code)
            print(response_log_picking.text)
            
        print("")

def rack1():
    while True :
        print(f"State_picking rack1 awal : {state_picking} ")
        time.sleep(5)
        if len(state_picking) != 0:
            
            for coordinate in state_picking:
                
                if coordinate["coordinat_picking"] == "A11":
                    
                    status_picking = 0

                    while status_picking != 1:
                        
                        compare = 0
                        read_sku_picking = []
                        countsss = 0
                        must_sku = coordinate["unique_key_picking"]
                        
                        while (compare != 1):
                            
                            time.sleep(1)
                            data_send_picking = str(3) #Menyalakan Rack Scanner
                            data_send_encode_picking = data_send_picking + "\0"
                            port_socket[str(ip_port[coor_ip[coordinate["coordinat_picking"]]])].sendto(data_send_encode_picking.encode(), (coor_ip[coordinate["coordinat_picking"]], ip_port[coor_ip[coordinate["coordinat_picking"]]]))
                            print("Data "+str(data_send_picking)+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_picking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_picking"]]])+" untuk menyalakan Rack Scanner. (Picking)")
                            
                            try:
                                data_picking, addr_picking = ip_sock[coor_ip[coordinate["coordinat_picking"]]].recvfrom(1200)
                                
                                #data bytes dari ESP32 diubah menjadi array of integer
                                i_picking = 0
                                arry_picking = []

                                
                                for elemen in data_picking:
                                    #print("data byte ke ",i+1,": ",elemen,end="")
                                    arry_picking.append(elemen)
                                    #print(", tipe data",type(arry[i]))
                                    i_picking=i_picking+1
                                    
                                j_picking=0
                                arry_bytes_picking =[]
                                
                                for elemen in arry_picking:
                                    data_decimal_picking = elemen & 0xFF
                                    data_hex_picking = hex(data_decimal_picking)
                                    data_bytes_picking = int(data_hex_picking,16).to_bytes(1,byteorder='big')
                                    arry_bytes_picking.append(data_bytes_picking)
                                    j_picking=j_picking+1
                                
                                arry_bytes_str_picking = []

                                for elemen in arry_bytes_picking:
                                    hex_x_picking = hex(elemen[0])[2:]
                                    if len(hex_x_picking) < 2:
                                        hex_x_picking = '0'+ hex_x_picking
                                    arry_bytes_str_picking.append(hex_x_picking)
                                
                                sku_picking = ""
                                
                                
                                for elemen_sku in arry_bytes_str_picking:
                                    sku_picking = sku_picking + elemen_sku
                                
                                sku_picking = sku_picking.upper() #cuma nerima dan ngirim 1 SKU
                                
                                print(f"SKU yang terbaca di rak A11 :{sku_picking}")
                                print(f"SKU yang dipicking di rak A11:{read_sku_picking}")
                                print(f"SKU yang seharusnya dipicking di rak A11:{must_sku}")
                
                                if sku_picking != "00" :
                                    
                                    sku_send = []
                                    jumlah_sku = int((len(sku_picking))/24)
                                    indeks_sku_awal = 0
                                    indeks_sku_akhir = 24
                                    
                                    for order_sku in range(jumlah_sku):
                                        
                                        sku_send.append(sku_picking[indeks_sku_awal:indeks_sku_akhir])
                                        indeks_sku_awal = indeks_sku_awal + 24
                                        indeks_sku_akhir = indeks_sku_akhir + 24
                                        
                                    print(f"SKU : {sku_send}")
                                    
                                    if coordinate["status"] == "OFF":
                                        compare = 1
                                    
                                    else: #coordinate["status"] == "ON"
                                        
                                        for sku_real in sku_send:
                                            found = 0 
                                            for sku_storage in read_sku_picking:
                                                if sku_real == sku_storage:
                                                    found = 1
                                            if found == 0:
                                                read_sku_picking.append(sku_real)
                                        
                                        if coordinate["status"] == "OFF":
                                            compare = 1
                                        else:    
                                            reply_picking = "standby"
                                            reply_encode_picking = reply_picking + "\0"
                                            port_socket[str(ip_port[coor_ip[coordinate["coordinat_picking"]]])].sendto(reply_encode_picking.encode(), (coor_ip[coordinate["coordinat_picking"]], ip_port[coor_ip[coordinate["coordinat_picking"]]]))
                                            print("Data "+reply_picking+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_picking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_picking"]]])+" untuk menyalakan Rack Scanner. (Picking)")
                                        
                                
                                else: #sku_picking == "00" and coordinate["status"] == "ON" and read_sku_picking == "":
                                    
                                    if read_sku_picking == [] :
                                        
                                        if coordinate["status"] == "ON":
                                        
                                            reply_picking = "glitch"
                                            reply_encode_picking = reply_picking + "\0"
                                            port_socket[str(ip_port[coor_ip[coordinate["coordinat_picking"]]])].sendto(reply_encode_picking.encode(), (coor_ip[coordinate["coordinat_picking"]], ip_port[coor_ip[coordinate["coordinat_picking"]]]))
                                            print("Data "+reply_picking+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_picking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_picking"]]])+" untuk menyalakan Rack Scanner. (Picking)")
                                        
                                        else: #off
                                            
                                            compare = 1
                                        
                                    else: #tag sukses picking komparasi
                                        
                                        count_qoly = 0
                                    
                                        for per_sku in read_sku_picking:
                                            if per_sku[0:6] == coordinate["unique_key_picking"]:
                                                count_qoly = count_qoly + 1
                                                
                                        print(f"qoly rack1 : {count_qoly}")
                                        nyamain = int(per_sku[12:16])
                                        print(f"qtt pallet rack1: {nyamain}")
                                        
                                        if count_qoly == int(per_sku[12:16]) :
                                        
                                            if coordinate["status"] == "ON":
                                                
                                                compare = 1
                                                
                                            else:
                                                compare = 1
                                            
                                        else:
                                            if coordinate["status"] == "ON":
                                                
                                                reply_picking = "notsukses"
                                                reply_encode_picking = reply_picking + "\0"
                                                port_socket[str(ip_port[coor_ip[coordinate["coordinat_picking"]]])].sendto(reply_encode_picking.encode(), (coor_ip[coordinate["coordinat_picking"]], ip_port[coor_ip[coordinate["coordinat_picking"]]]))
                                                print("Data "+reply_picking+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_picking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_picking"]]])+" untuk menyalakan Rack Scanner. (Picking)")
                                                
                                                read_sku_picking = []
                                                
                                            else:
                                                
                                                compare = 1   
                                    
                                print(countsss)
                                countsss = countsss + 1
                                print("")
                            
                            
                            except socket.timeout:
                                
                                reply_picking = "notsukses"
                                reply_encode_picking = reply_picking + "\0"
                                port_socket[str(ip_port[coor_ip[coordinate["coordinat_picking"]]])].sendto(reply_encode_picking.encode(), (coor_ip[coordinate["coordinat_picking"]], ip_port[coor_ip[coordinate["coordinat_picking"]]]))
                                print("Data "+reply_picking+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_picking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_picking"]]])+" untuk menyalakan Rack Scanner. (Picking)")
                            
                                continue
                            
                            
                        reply_picking = "sukses"
                        reply_encode_picking = reply_picking + "\0"
                        port_socket[str(ip_port[coor_ip[coordinate["coordinat_picking"]]])].sendto(reply_encode_picking.encode(), (coor_ip[coordinate["coordinat_picking"]], ip_port[coor_ip[coordinate["coordinat_picking"]]]))
                        print("Data "+reply_picking+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_picking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_picking"]]])+" untuk menyalakan Rack Scanner. (Picking)")
                                
                        
                        if (compare == 1 and coordinate["status"] == "ON"):
                        
                            # URL endpoint API di Heroku
                            url_picking = "https://octagonwms.herokuapp.com/coord/request"

                            # Data string yang akan dikirim ke server
                            data_picking = { 'id' : int(coordinate["coordinat_id_picking"]),
                                     'request' : False}
                
                            json_data_picking = json.dumps(data_picking)
                            headers_picking ={'Content-type': 'application/json'}
                            # Mengirim data menggunakan metode POST dan headers yang sudah ditentukan
                            response_picking = requests.put(url=url_picking, data=json_data_picking, headers=headers_picking)

                            # Mengecek respons dari server
                            if response_picking.status_code == 200:
                                print("Data berhasil dikirim ke server dan Picking berhasil.")
                                state_picking.remove(coordinate)
                                print(f"state picking removed rack 1: {state_picking}")
                                status_picking = 1
                                print(f"Rack 1 : State_Picking {state_picking}")

                            else:
                                print("Data gagal dikirim ke server. Status code:", response_picking.status_code)
                                print(response_picking.text)
                                
                    
                            print("")
                            
                        if (compare == 1 and coordinate["status"] == "OFF"):
                            state_picking.remove(coordinate)
                            status_picking = 1
def rack2():
    while True :
        print(f"State_picking rack2 awal : {state_picking} ")
        time.sleep(5)
        if len(state_picking) != 0:
            
            for coordinate in state_picking:
                
                if coordinate["coordinat_picking"] == "A21":
                    
                    status_picking = 0

                    while status_picking != 1:
                        
                        compare = 0
                        read_sku_picking = []
                        countsss = 0
                        must_sku = coordinate["unique_key_picking"]
                        
                        while (compare != 1):
                            
                            time.sleep(1)
                            data_send_picking = str(3) #Menyalakan Rack Scanner
                            data_send_encode_picking = data_send_picking + "\0"
                            port_socket[str(ip_port[coor_ip[coordinate["coordinat_picking"]]])].sendto(data_send_encode_picking.encode(), (coor_ip[coordinate["coordinat_picking"]], ip_port[coor_ip[coordinate["coordinat_picking"]]]))
                            print("Data "+str(data_send_picking)+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_picking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_picking"]]])+" untuk menyalakan Rack Scanner. (Picking)")
                            
                            try:
                                data_picking, addr_picking = ip_sock[coor_ip[coordinate["coordinat_picking"]]].recvfrom(1200)
                                
                                #data bytes dari ESP32 diubah menjadi array of integer
                                i_picking = 0
                                arry_picking = []

                                
                                for elemen in data_picking:
                                    #print("data byte ke ",i+1,": ",elemen,end="")
                                    arry_picking.append(elemen)
                                    #print(", tipe data",type(arry[i]))
                                    i_picking=i_picking+1
                                    
                                j_picking=0
                                arry_bytes_picking =[]
                                
                                for elemen in arry_picking:
                                    data_decimal_picking = elemen & 0xFF
                                    data_hex_picking = hex(data_decimal_picking)
                                    data_bytes_picking = int(data_hex_picking,16).to_bytes(1,byteorder='big')
                                    arry_bytes_picking.append(data_bytes_picking)
                                    j_picking=j_picking+1
                                
                                arry_bytes_str_picking = []

                                for elemen in arry_bytes_picking:
                                    hex_x_picking = hex(elemen[0])[2:]
                                    if len(hex_x_picking) < 2:
                                        hex_x_picking = '0'+ hex_x_picking
                                    arry_bytes_str_picking.append(hex_x_picking)
                                
                                sku_picking = ""
                                
                                
                                for elemen_sku in arry_bytes_str_picking:
                                    sku_picking = sku_picking + elemen_sku
                                
                                sku_picking = sku_picking.upper() #cuma nerima dan ngirim 1 SKU
                                
                                print(f"SKU yang terbaca di rak A21 :{sku_picking}")
                                print(f"SKU yang dipicking di rak A21:{read_sku_picking}")
                                print(f"SKU yang seharusnya dipicking di rak A21:{must_sku}")
                
                                if sku_picking != "00" :
                                    
                                    sku_send = []
                                    jumlah_sku = int((len(sku_picking))/24)
                                    indeks_sku_awal = 0
                                    indeks_sku_akhir = 24
                                    
                                    for order_sku in range(jumlah_sku):
                                        
                                        sku_send.append(sku_picking[indeks_sku_awal:indeks_sku_akhir])
                                        indeks_sku_awal = indeks_sku_awal + 24
                                        indeks_sku_akhir = indeks_sku_akhir + 24
                                        
                                    print(f"SKU : {sku_send}")
                                    
                                    if coordinate["status"] == "OFF":
                                        compare = 1
                                    
                                    else: #coordinate["status"] == "ON"
                                        
                                        for sku_real in sku_send:
                                            found = 0 
                                            for sku_storage in read_sku_picking:
                                                if sku_real == sku_storage:
                                                    found = 1
                                            if found == 0:
                                                read_sku_picking.append(sku_real)
                                        
                                        if coordinate["status"] == "OFF":
                                            compare = 1
                                        else:    
                                            reply_picking = "standby"
                                            reply_encode_picking = reply_picking + "\0"
                                            port_socket[str(ip_port[coor_ip[coordinate["coordinat_picking"]]])].sendto(reply_encode_picking.encode(), (coor_ip[coordinate["coordinat_picking"]], ip_port[coor_ip[coordinate["coordinat_picking"]]]))
                                            print("Data "+reply_picking+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_picking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_picking"]]])+" untuk menyalakan Rack Scanner. (Picking)")
                                
                                else: #sku_picking == "00" and coordinate["status"] == "ON" and read_sku_picking == "":
                                    
                                    if read_sku_picking == [] :
                                        
                                        if coordinate["status"] == "ON":
                                        
                                            reply_picking = "glitch"
                                            reply_encode_picking = reply_picking + "\0"
                                            port_socket[str(ip_port[coor_ip[coordinate["coordinat_picking"]]])].sendto(reply_encode_picking.encode(), (coor_ip[coordinate["coordinat_picking"]], ip_port[coor_ip[coordinate["coordinat_picking"]]]))
                                            print("Data "+reply_picking+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_picking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_picking"]]])+" untuk menyalakan Rack Scanner. (Picking)")
                                        
                                        else: #off
                                            
                                            compare = 1
                                        
                                    else: #tag sukses picking komparasi
                                        
                                        count_qoly = 0
                                    
                                        for per_sku in read_sku_picking:
                                            if per_sku[0:6] == coordinate["unique_key_picking"]:
                                                count_qoly = count_qoly + 1
                                                
                                        print(f"qoly rack1 : {count_qoly}")
                                        nyamain = int(per_sku[12:16])
                                        print(f"qtt pallet rack1: {nyamain}")
                                        
                                        if count_qoly == int(per_sku[12:16]) :
                                        
                                            if coordinate["status"] == "ON":
                                                
                                                compare = 1
                                                
                                            else:
                                                compare = 1
                                            
                                        else:
                                            if coordinate["status"] == "ON":
                                                
                                                reply_picking = "notsukses"
                                                reply_encode_picking = reply_picking + "\0"
                                                port_socket[str(ip_port[coor_ip[coordinate["coordinat_picking"]]])].sendto(reply_encode_picking.encode(), (coor_ip[coordinate["coordinat_picking"]], ip_port[coor_ip[coordinate["coordinat_picking"]]]))
                                                print("Data "+reply_picking+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_picking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_picking"]]])+" untuk menyalakan Rack Scanner. (Picking)")
                                                
                                                read_sku_picking = []
                                                
                                            else:
                                                
                                                compare = 1   
                                    
                                print(countsss)
                                countsss = countsss + 1
                                print("")
                            
                            
                            except socket.timeout:
                                
                                reply_picking = "notsukses"
                                reply_encode_picking = reply_picking + "\0"
                                port_socket[str(ip_port[coor_ip[coordinate["coordinat_picking"]]])].sendto(reply_encode_picking.encode(), (coor_ip[coordinate["coordinat_picking"]], ip_port[coor_ip[coordinate["coordinat_picking"]]]))
                                print("Data "+reply_picking+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_picking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_picking"]]])+" untuk menyalakan Rack Scanner. (Picking)")
                            
                                continue
                            
                            
                        reply_picking = "sukses"
                        reply_encode_picking = reply_picking + "\0"
                        port_socket[str(ip_port[coor_ip[coordinate["coordinat_picking"]]])].sendto(reply_encode_picking.encode(), (coor_ip[coordinate["coordinat_picking"]], ip_port[coor_ip[coordinate["coordinat_picking"]]]))
                        print("Data "+reply_picking+" telah dikirim ke ESP32 dengan addr "+str(coor_ip[coordinate["coordinat_picking"]])+" port "+str(ip_port[coor_ip[coordinate["coordinat_picking"]]])+" untuk menyalakan Rack Scanner. (Picking)")
                                
                        
                        if (compare == 1 and coordinate["status"] == "ON"):
                        
                            # URL endpoint API di Heroku
                            url_picking = "https://octagonwms.herokuapp.com/coord/request"

                            # Data string yang akan dikirim ke server
                            data_picking = { 'id' : int(coordinate["coordinat_id_picking"]),
                                     'request' : False}
                
                            json_data_picking = json.dumps(data_picking)
                            headers_picking ={'Content-type': 'application/json'}
                            # Mengirim data menggunakan metode POST dan headers yang sudah ditentukan
                            response_picking = requests.put(url=url_picking, data=json_data_picking, headers=headers_picking)

                            # Mengecek respons dari server
                            if response_picking.status_code == 200:
                                print("Data berhasil dikirim ke server dan Picking berhasil.")
                                state_picking.remove(coordinate)
                                print(f"state picking removed rack 2: {state_picking}")
                                status_picking = 1
                                print(f"Rack 2 : State_Picking {state_picking}")

                            else:
                                print("Data gagal dikirim ke server. Status code:", response_picking.status_code)
                                print(response_picking.text)
                                
                    
                            print("")
                            
                        if (compare == 1 and coordinate["status"] == "OFF"):
                            state_picking.remove(coordinate)
                            status_picking = 1


t1 = threading.Thread(target=searching)
t1.start()
           
t2 = threading.Thread(target=rack1)
t2.start()

t3 = threading.Thread(target=rack2)
t3.start()







