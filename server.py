import math
import json
import time
import socket


send_msg_points = {
    "points": "",
    "move": ""
}
 
class Figure:
    def __init__(self,x,y,coloexr):
        self.x=x
        self.y=y
        self.color=0
        
 
    def __str__(self):
        return 'figure'
    
    def moveFigure(self,x,y):
        if (math.fabs(x-self.x)==200 and math.fabs(y-self.y)==100) or  (math.fabs(y-self.y)==200 and math.fabs(x-self.x)==100):
            self.setOffset(x, y)
            self.x=x
            self.y=y
        
        return 'figure'

def made_json_format(current_key, obj):
    
    d = {current_key: obj}
    return json.dumps(d)

def send_to_all_users(s, clients, message):
    for i in clients:
        s.sendto(message.encode("utf-8"), i)


def launch_game(s,clients):

    massHorses = []
    whiteEnter=True
    withHorse=False
    tempHorse=None
    
    sizeWhite=8
    sizeBlack=8
    
    for i in range(8): 
        for j in range(8):   
            if (8 - i + 1 + j ) % 2 == 0:
                if j>=0 and j<2 :
                    massHorses.append([i*100,j*100,0])  # 0 - это чёрные
                if j>=6 and j<8 :
                    massHorses.append([i*100,j*100,1])  # 1 - это белые
    startPos_msg = made_json_format("startPos", massHorses)
    send_to_all_users(s,clients, startPos_msg)       
    
    while True:
       # try:
        data, addr = s.recvfrom(1024)
        if(addr!=clients[0] and addr!=clients[1]):
            s.sendto(("Сервер заполнен").encode("utf-8"), addr)
        
        #except
        elif(data!=""):
            json_string = data.decode("utf-8")
            
            json_string = json.loads(json_string)
            dict_key = list(json_string.keys())[0] #ключ x0
            
            if dict_key=="pos":
                my_list_pos = list(json_string[dict_key])
               
                x0 = my_list_pos[0]
                y0 = my_list_pos[1]
                x1 = my_list_pos[2]
                y1 = my_list_pos[3]
           
            
                if(whiteEnter and addr==clients[0] or not whiteEnter and addr==clients[1]):
        
                    if (math.fabs(x0-x1)==200 and math.fabs(y0-y1)==100) or  (math.fabs(y0-y1)==200 and math.fabs(x0-x1)==100):
                        for i in massHorses:
                            if(i[0]==x0 and i[1] == y0):
                                if(i[2]==1 and  addr==clients[0]) or (i[2]==0 and addr==clients[1]):
                                    for j in massHorses:
                                        withHorse=False
                                        if(j[0]==x1 and j[1]==y1):
                                            if (j[2]==0 and i[2]==1 or j[2]==1 and i[2]==0): #print("съели лошадку")
                                                i[0]=x1
                                                i[1]=y1
                                                pos=[x0,y0,x1,y1]
                                               # pos_msg = made_json_format("pos", pos)
                                                send_msg_points['pos'] = pos
                                                if(addr==clients[1]):
                                                    send_msg_points['move'] = "(ход белых)"
                                                if(addr==clients[0]):
                                                    send_msg_points['move'] = "(ход чёрных)"
                                                s.sendto((json.dumps(send_msg_points)).encode("utf-8"), clients[0])
                                                s.sendto((json.dumps(send_msg_points)).encode("utf-8"), clients[1])
                                                
                                                tempHorse=j
                                                
                                                whiteEnter=not whiteEnter
                                                withHorse=True
                                                
                                                if(j[2]==0):
                                                    sizeBlack-=1
                                                elif(j[2]==1):
                                                    sizeWhite-=1
                                                break
                                            elif (j[2]==0 and i[2]==0 or j[2]==1 and i[2]==1):
                                             
                                                msg = made_json_format("message", "не ешь своих лошадок")
                                                s.sendto(msg.encode("utf-8"), addr)
                                                withHorse=True
                                                break
                                        
                                    if(not withHorse):
                                        i[0]=x1
                                        i[1]=y1
                                        pos=[x0,y0,x1,y1]
                                     
                                        send_msg_points['pos'] = pos
                                        if(addr==clients[1]):
                                            send_msg_points['move'] = "(ход белых)"
                                        if(addr==clients[0]):
                                            send_msg_points['move'] = "(ход чёрных)"
                                        s.sendto((json.dumps(send_msg_points)).encode("utf-8"), clients[0])
                                        s.sendto((json.dumps(send_msg_points)).encode("utf-8"), clients[1])
                                        
                                        
                                        whiteEnter=not whiteEnter
                                    break
                                    
                                else:
                                    msg = made_json_format("message", "не трогай чужих лошадок")
                                    s.sendto(msg.encode("utf-8"), addr)
                        if(tempHorse!=None):
                            massHorses.remove(tempHorse)
                            tempHorse=None
                                  
                                           
                    else:
                        msg = made_json_format("message", "лошадки так не ходят")
                        s.sendto(msg.encode("utf-8"), addr)
                else:
                    msg = made_json_format("message", "не ваш ход!")
                    s.sendto(msg.encode("utf-8"), addr)
            
            if dict_key=="message":
                if json_string['message']=="exit":
                    break
                
            if(sizeWhite<=4):
                msg = made_json_format("message", "чёрные выиграли")
                send_to_all_users(s,clients, msg)
                break
            if(sizeBlack<=4):
                msg = made_json_format("message", "белые выиграли")
                send_to_all_users(s,clients, msg)
                break
                               
                
def main():       
    host = socket.gethostbyname(socket.gethostname())
    port = 9090
    clients = []
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
   
    
    print("[ Server Started ]")
    print(socket.gethostname())
    
    
    
                
    while True:
        #try:
            data, addr = s.recvfrom(1024)
            
            if addr in clients: #проверяем, не вышел ли первый, пока не подключился второй
                json_string = data.decode("utf-8")
                json_string = json.loads(json_string)
                dict_key = list(json_string.keys())[0]
                if dict_key == "message":
                    if json_string['message']=="exit":
                        clients.remove(addr)
                    
                        
                        
    #                    addr.client_socket.close()
                        
            
            elif addr not in clients:
                
                clients.append(addr)
                if(len(clients)==1):
                    s.sendto(("Белые").encode("utf-8"), addr)
                if(len(clients)==2):
                    s.sendto(("Чёрные").encode("utf-8"), addr)
                    
    
            action_time = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())
    
            print("[" + addr[0] + "]=[" + str(addr[1]) + "]=[" + action_time + "]/", end="")
            print(data.decode("utf-8"))
            
            print(len(clients))
            if len(clients) == 2:
                launch_game(s, clients)
                s.close
                return
                
               
               
        #except Exception:
         #   print(Exception)
          #  print("\n[ Server Stopped ]")
           # return
    
    s.close()                    
                        
  
if __name__ == "__main__":
    main() 