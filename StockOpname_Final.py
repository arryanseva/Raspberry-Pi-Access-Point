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

global counts_stockopname
global sku_array_stockopname
global finds_stockopname

global ip_coor
global addr_sku
global ip_port
global coor_ip
global coor_coorId
global port_socket
global state_stockopname

UDP_IP = "192.168.4.1"
UDP_PORT_1 = 49155
sock1 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock1.settimeout(15)
sock1.bind((UDP_IP,UDP_PORT_1))

UDP_PORT_2 = 49156
sock2 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock2.settimeout(15)
sock2.bind((UDP_IP,UDP_PORT_2))

ip_sock = {"192.168.4.7" : sock1,
           "192.168.4.8" : sock2}
ip_status = {"192.168.4.7" : "OFF",
           "192.168.4.8" : "OFF"}

first_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #keep dulu perhatiin file 2esp32,10esp32non dan filtered
second_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #keep dulu 

coordinate_rack = [["A11","notsukses"],["A21","notsukses"]]

counts_stockopname = 1
sku_array_stockopname = []
finds_stockopname = 0

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
state_stockopname = []

def searching():
    while True :
        
        print(f"state stockopname : {state_stockopname}")
        
        # URL endpoint API di Heroku Log Activity
        url_log_stockopname = "https://octagonwms.herokuapp.com/stockopname"

        # Mengirim data menggunakan metode GET dan headers yang sudah ditentukan
        response_log_stockopname = requests.get(url=url_log_stockopname)

        # Mengecek respons dari server
        if response_log_stockopname.status_code == 200:
            print("Data berhasil dikirim ke server.")
                        
            data_received_log_stockopname = json.loads(response_log_stockopname.text)
            pprint.pprint(data_received_log_stockopname)
            print("")
            
            ####Diambil yang terakhir kondisinya true
            for data in data_received_log_stockopname:
                if (data["check"] == True ):
                    add_state_stockopname = {"found": 1,
                                              "count": 0}
                    
                    
                    
                    if len(state_stockopname) == 0:
                        state_stockopname.append(add_state_stockopname)
                        
                        url_cd_stockopname = "https://octagonwms.herokuapp.com/clreal"
                        response_cd_stockopname = requests.get(url=url_cd_stockopname)
                        
                        if response_cd_stockopname.status_code == 200:
                            print("Data berhasil dikirim ke server (clear).")    
                        else:
                            print("Data gagal dikirim ke server. Status code:", response_cd_stockopname.status_code)
                            print(response_cd_stockopname.text)

                        print("")
                        
                    else:
                        if (state_stockopname[0]["count"] == len(coordinate_rack)):
                            
                            
                            value_send_stockopname = {"data" : []}
                            counts_send_stockopname = 1
                            
                            for key in addr_sku:
                                if addr_sku[key] != "00" :
                                    for per_sku in addr_sku[key]:
                                        sku_send_stockopname_temp = per_sku
                                        exp_date_year = sku_send_stockopname_temp[16:20]
                                        exp_date_month = sku_send_stockopname_temp[20:22]
                                        exp_date_day = sku_send_stockopname_temp[22:24]
                                        exp_date = exp_date_year + '-' + exp_date_month + '-' + exp_date_day + "T00:00:00.000Z"

                                        add = {"id": counts_send_stockopname,
                                                "coordinate_id": int(coor_coorId[ip_coor[key]]),
                                                "qty": int(sku_send_stockopname_temp[12:16]),
                                                "batch": int(sku_send_stockopname_temp[6:9]),
                                                "unique_key": sku_send_stockopname_temp[0:6],
                                                "exp_date": exp_date,
                                                "product_id": int(sku_send_stockopname_temp[9:12])}
                                        print(add)
                                        value_send_stockopname["data"].append(add)
                                        counts_send_stockopname = counts_send_stockopname + 1
                            
                            print("")
                            print(value_send_stockopname)
                            
                        
                            # URL endpoint API di Heroku
                            url_stockopname_update = "https://octagonwms.herokuapp.com/realdata"

                            json_data_stockopname_update = json.dumps(value_send_stockopname)
                            headers_stockopname_update ={'Content-type': 'application/json'}
                            # Mengirim data menggunakan metode get params body dan headers yang sudah ditentukan
                            response_stockopname_update = requests.get(url=url_stockopname_update, data=json_data_stockopname_update, headers=headers_stockopname_update)

                            # Mengecek respons dari server
                            if response_stockopname_update.status_code == 200:
                                
                                print("Data Real Stock berhasil dikirimkan (update).")
                                
                                data_received_stockopname_update = json.loads(response_stockopname_update.text)
                                pprint.pprint(data_received_stockopname_update)
                                print("")
                                # URL endpoint API di Heroku
                                url_stockopname_change = "https://octagonwms.herokuapp.com/stockopname"

                                # Data string yang akan dikirim ke server
                                data_change = {"id" : 1,
                                        "check" : False}
                                
                                json_data_stockopname_change = json.dumps(data_change)
                                headers_stockopname_change ={'Content-type': 'application/json'}
                                response_stockopname_change = requests.put(url=url_stockopname_change, data=json_data_stockopname_change, headers=headers_stockopname_change)

                                # Mengecek respons dari server
                                if response_stockopname_change.status_code == 200:
                                
                                    print("Data Stock Opname telah berhasil dilakukan (change).")
                                    
                                    state_stockopname.remove(state_stockopname[0])
                                    
                                    for elemen_rack in coordinate_rack :
                                        elemen_rack[1] = "notsukses"
                                        
                            
                                else:
                                    print("Data gagal dikirim ke server. Status code:", response_stockopname_change.status_code)
                                    print(response_stockopname_change.text)

                            else:
                                print("Data gagal dikirim ke server. Status code:", response_stockopname_update.status_code)
                                print(response_stockopname_update.text)
                            print("")
                                   
        else:
            print("Data gagal dikirim ke server. Status code:", response_log_stockopname.status_code)
            print(response_log_stockopname.text)
            
        print("")

def rack1():
    while True :
        
        if len(state_stockopname) == 1:
            
            for coordinate in coordinate_rack:
                
                if coordinate[0] == "A11" and coordinate[1] == "notsukses":
                    
                    data_send_stockopname = str(2) #Menyalakan Rack Scanner
                    data_send_encode_stockopname = data_send_stockopname + "\0"
                    port_socket[str(ip_port[coor_ip[coordinate[0]]])].sendto(data_send_encode_stockopname.encode(), (coor_ip[coordinate[0]], ip_port[coor_ip[coordinate[0]]]))
                    print(f"Data {data_send_stockopname} telah dikirim ke ESP32 dengan addr {coor_ip[coordinate[0]]} port {ip_port[coor_ip[coordinate[0]]]} untuk menyalakan Rack Scanner. (StockOpname)")
                    
                    try:
                        data_stockopname, addr_stockopname = ip_sock[coor_ip[coordinate[0]]].recvfrom(4096)
                        reply_stockopname = "sukses"
                        reply_encode_stockopname = reply_stockopname + "\0"
                        port_socket[str(ip_port[addr_stockopname[0]])].sendto(reply_encode_stockopname.encode(), (addr_stockopname[0], ip_port[addr_stockopname[0]]))

                        #data bytes dari ESP32 diubah menjadi array of integer
                        i_stockopname = 0
                        arry_stockopname = []

                        
                        for elemen in data_stockopname:
                            #print("data byte ke ",i+1,": ",elemen,end="")
                            arry_stockopname.append(elemen)
                            #print(", tipe data",type(arry[i]))
                            i_stockopname=i_stockopname+1
                            
                        j_stockopname=0
                        arry_bytes_stockopname =[]
                        
                        for elemen in arry_stockopname:
                            data_decimal_stockopname = elemen & 0xFF
                            data_hex_stockopname = hex(data_decimal_stockopname)
                            data_bytes_stockopname = int(data_hex_stockopname,16).to_bytes(1,byteorder='big')
                            arry_bytes_stockopname.append(data_bytes_stockopname)
                            j_stockopname=j_stockopname+1
                        
                        arry_bytes_str_stockopname = []

                        for elemen in arry_bytes_stockopname:
                            hex_x_stockopname = hex(elemen[0])[2:]
                            if len(hex_x_stockopname) < 2:
                                hex_x_stockopname = '0'+ hex_x_stockopname
                            arry_bytes_str_stockopname.append(hex_x_stockopname)
                        
                        sku_stockopname = ""

                        for elemen_sku in arry_bytes_str_stockopname:
                            sku_stockopname = sku_stockopname + elemen_sku
                        
                        sku_stockopname = sku_stockopname.upper() #cuma nerima dan ngirim 1 SKU
                        jumlah_sku = len(sku_stockopname)/24
                        print(f"sku stockopname 1 : {sku_stockopname} jumlah : {jumlah_sku}")
                        if sku_stockopname != "00":
                            
                            sku_send = []
                            jumlah_sku = int((len(sku_stockopname))/24)
                            indeks_sku_awal = 0
                            indeks_sku_akhir = 24
                            
                            for order_sku in range(jumlah_sku):
                                
                                sku_send.append(sku_stockopname[indeks_sku_awal:indeks_sku_akhir])
                                indeks_sku_awal = indeks_sku_awal + 24
                                indeks_sku_akhir = indeks_sku_akhir + 24
                            
                            addr_sku[addr_stockopname[0]] = sku_send
                        
                        else:
                            addr_sku[addr_stockopname[0]] = sku_stockopname
                        
                        coordinate[1] = "sukses"
                        print("A11 no count")
                        
                        if (len(state_stockopname) == 1):
                            state_stockopname[0]["count"] = state_stockopname[0]["count"] + 1
                            print("A11")
                        
                        time.sleep(20)
                        
                    except socket.timeout:
                        
                            reply_stockopname = "sukses"
                            reply_encode_stockopname = reply_stockopname + "\0"
                            port_socket[str(ip_port[addr_stockopname[0]])].sendto(reply_encode_stockopname.encode(), (addr_stockopname[0], ip_port[addr_stockopname[0]]))

                            addr_sku[addr_stockopname[0]] = "00"
                            coordinate[1] = "sukses"
                            print("A11 no count")
                            
                            if (len(state_stockopname) == 1):
                                state_stockopname[0]["count"] = state_stockopname[0]["count"] + 1
                                print("A11")
                            
                            time.sleep(20)
                            
                            continue
def rack2():
    while True :
        
        if len(state_stockopname) == 1:
            
            for coordinate in coordinate_rack:
                
                if coordinate[0] == "A21" and coordinate[1] == "notsukses":
                    
                    data_send_stockopname = str(2) #Menyalakan Rack Scanner
                    data_send_encode_stockopname = data_send_stockopname + "\0"
                    port_socket[str(ip_port[coor_ip[coordinate[0]]])].sendto(data_send_encode_stockopname.encode(), (coor_ip[coordinate[0]], ip_port[coor_ip[coordinate[0]]]))
                    print(f"Data {data_send_stockopname} telah dikirim ke ESP32 dengan addr {coor_ip[coordinate[0]]} port {ip_port[coor_ip[coordinate[0]]]} untuk menyalakan Rack Scanner. (StockOpname)")
                    
                    try:
                        data_stockopname, addr_stockopname = ip_sock[coor_ip[coordinate[0]]].recvfrom(4096)
                        reply_stockopname = "sukses"
                        reply_encode_stockopname = reply_stockopname + "\0"
                        port_socket[str(ip_port[addr_stockopname[0]])].sendto(reply_encode_stockopname.encode(), (addr_stockopname[0], ip_port[addr_stockopname[0]]))

                        #data bytes dari ESP32 diubah menjadi array of integer
                        i_stockopname = 0
                        arry_stockopname = []

                        
                        for elemen in data_stockopname:
                            #print("data byte ke ",i+1,": ",elemen,end="")
                            arry_stockopname.append(elemen)
                            #print(", tipe data",type(arry[i]))
                            i_stockopname=i_stockopname+1
                            
                        j_stockopname=0
                        arry_bytes_stockopname =[]
                        
                        for elemen in arry_stockopname:
                            data_decimal_stockopname = elemen & 0xFF
                            data_hex_stockopname = hex(data_decimal_stockopname)
                            data_bytes_stockopname = int(data_hex_stockopname,16).to_bytes(1,byteorder='big')
                            arry_bytes_stockopname.append(data_bytes_stockopname)
                            j_stockopname=j_stockopname+1
                        
                        arry_bytes_str_stockopname = []

                        for elemen in arry_bytes_stockopname:
                            hex_x_stockopname = hex(elemen[0])[2:]
                            if len(hex_x_stockopname) < 2:
                                hex_x_stockopname = '0'+ hex_x_stockopname
                            arry_bytes_str_stockopname.append(hex_x_stockopname)
                        
                        sku_stockopname = ""

                        for elemen_sku in arry_bytes_str_stockopname:
                            sku_stockopname = sku_stockopname + elemen_sku
                        
                        sku_stockopname = sku_stockopname.upper() #cuma nerima dan ngirim 1 SKU
                        jumlah_sku = len(sku_stockopname)/24
                        print(f"sku stockopname 2 : {sku_stockopname} jumlah : {jumlah_sku}")
                        if sku_stockopname != "00":
                            
                            sku_send = []
                            jumlah_sku = int((len(sku_stockopname))/24)
                            indeks_sku_awal = 0
                            indeks_sku_akhir = 24
                            
                            for order_sku in range(jumlah_sku):
                                
                                sku_send.append(sku_stockopname[indeks_sku_awal:indeks_sku_akhir])
                                indeks_sku_awal = indeks_sku_awal + 24
                                indeks_sku_akhir = indeks_sku_akhir + 24
                            
                            addr_sku[addr_stockopname[0]] = sku_send
                        
                        else:
                            addr_sku[addr_stockopname[0]] = sku_stockopname
                        
                        coordinate[1] = "sukses"
                        print("A21 no count")
                        
                        if (len(state_stockopname) == 1):
                            state_stockopname[0]["count"] = state_stockopname[0]["count"] + 1
                            print("A21")
                        
                        time.sleep(20)
                        
                    except socket.timeout:
                        
                            reply_stockopname = "sukses"
                            reply_encode_stockopname = reply_stockopname + "\0"
                            port_socket[str(ip_port[addr_stockopname[0]])].sendto(reply_encode_stockopname.encode(), (addr_stockopname[0], ip_port[addr_stockopname[0]]))

                            addr_sku[addr_stockopname[0]] = "00"
                            coordinate[1] = "sukses"
                            print("A21 no count")
                            
                            if (len(state_stockopname) == 1):
                                state_stockopname[0]["count"] = state_stockopname[0]["count"] + 1
                                print("A21")
                            
                            time.sleep(20)

t1 = threading.Thread(target=searching)
t1.start()
           
t2 = threading.Thread(target=rack1)
t2.start()

t3 = threading.Thread(target=rack2)
t3.start()






