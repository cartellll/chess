import math
import json
import time
import socket
import game

JSON_FILE_PATH="state.json"
send_msg_points = {
    "pos": "",
    "move": ""
}

send_start_msg_points = {
    "startPos": "",
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
    move=0
    withHorse=False
    tempHorse=None
    sizeWhite=0
    sizeBlack=0
    gameEnd=False
    

    success, data = game.load_game_state_from_json(JSON_FILE_PATH)

    if success:
        massHorses,move = game.parse_data(data)
        for i in massHorses:
            if(i['color']==0):
                sizeBlack+=1
            else:
                sizeWhite+=1
    else:
        move = 1
        sizeWhite=8
        sizeBlack=8
        for i in range(8): 
            for j in range(8): 
                horse_state_format = {
                        "x": "",
                        "y": "",
                        "color": ""
                }
                if (8 - i + 1 + j ) % 2 == 0:
                    if j>=0 and j<2 :
                        horse_state_format['x']=i*100
                        horse_state_format['y']=j*100
                        horse_state_format['color']=0
                        massHorses.append(horse_state_format)  # 0 - это чёрные
                    if j>=6 and j<8 :
                        horse_state_format['x']=i*100
                        horse_state_format['y']=j*100
                        horse_state_format['color']=1
                        massHorses.append(horse_state_format)  # 1 - это белые 
    send_start_msg_points["startPos"] = massHorses               
    send_start_msg_points["move"]=move
    s.sendto((json.dumps(send_start_msg_points)).encode("utf-8"), clients[0])
    s.sendto((json.dumps(send_start_msg_points)).encode("utf-8"), clients[1])
        
    
    while True:
       
        data, addr = s.recvfrom(1024)
        if(addr!=clients[0] and addr!=clients[1]):
            s.sendto(("Сервер заполнен").encode("utf-8"), addr)
        
        
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
           
            
                if(move==1 and addr==clients[0] or move==0 and addr==clients[1]): #Если ваш ход
        
                    if (math.fabs(x0-x1)==200 and math.fabs(y0-y1)==100) or  (math.fabs(y0-y1)==200 and math.fabs(x0-x1)==100): #Если походили правильно
                        for i in massHorses:
                            if(i['x']==x0 and i['y'] == y0): #если взяли коня
                                if(i['color']==1 and  addr==clients[0]) or (i['color']==0 and addr==clients[1]): #если конь того цвета
                                    for j in massHorses:
                                        withHorse=False
                                        if(j['x']==x1 and j['y']==y1):
                                            if (j['color']==0 and i['color']==1 or j['color']==1 and i['color']==0): #если съели лошадь
                                                i['x']=x1
                                                i['y']=y1
                                                
                                                pos=[x0,y0,x1,y1]
                                                send_msg_points['pos'] = pos
                                                if(addr==clients[1]):
                                                    move=1
                                                    send_msg_points['move'] = move
                                                if(addr==clients[0]):
                                                    move=0
                                                    send_msg_points['move'] = move
                                                s.sendto((json.dumps(send_msg_points)).encode("utf-8"), clients[0])
                                                s.sendto((json.dumps(send_msg_points)).encode("utf-8"), clients[1])
                                                
                                                tempHorse=j
                                                
                                                withHorse=True
                                                
                                                if(j['color']==0):
                                                    sizeBlack-=1
                                                elif(j['color']==1):
                                                    sizeWhite-=1
                                                break
                                            elif (j['color']==0 and i['color']==0 or j['color']==1 and i['color']==1): #если хотим съесть свою лошадь
                                             
                                                msg = made_json_format("message", "не ешь своих лошадок")
                                                s.sendto(msg.encode("utf-8"), addr)
                                                withHorse=True
                                                break
                                        
                                    if(not withHorse): #если просто походили 
                                        i['x']=x1
                                        i['y']=y1
                                        pos=[x0,y0,x1,y1]
                                     
                                        send_msg_points['pos'] = pos
                                        if(addr==clients[1]):
                                            move = 1
                                            send_msg_points['move'] = move
                                        if(addr==clients[0]):
                                            move = 0
                                            send_msg_points['move'] = move
                                        s.sendto((json.dumps(send_msg_points)).encode("utf-8"), clients[0])
                                        s.sendto((json.dumps(send_msg_points)).encode("utf-8"), clients[1])
                                        
                                        
                                        
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
                gameEnd=True
                send_to_all_users(s,clients, msg)
            
                break
            if(sizeBlack<=4):
                msg = made_json_format("message", "белые выиграли")
                gameEnd=True
                send_to_all_users(s,clients, msg)
                break
    
    game.save_game_state_to_json(massHorses,move,gameEnd,JSON_FILE_PATH)
 
        
        
                               
                
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
                    
        
            elif addr not in clients:
                
                clients.append(addr)
                if(len(clients)==1):
                    s.sendto(("Белые").encode("utf-8"), addr)
                if(len(clients)==2):
                    s.sendto(("Чёрные").encode("utf-8"), addr)
                    
    
            action_time = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())
    
            print("[" + addr[0] + "]=[" + str(addr[1]) + "]=[" + action_time + "]/", end="")
            print(data.decode("utf-8"))
            

            if len(clients) == 2:
                launch_game(s, clients)
                s.close
                return
            
               
               
        #except Exception:
            #print(Exception)
           # print("\n[ Server Stopped ]")
            #return
    
            #s.close()                    
                            
  
if __name__ == "__main__":
    main() 