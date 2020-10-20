import sys
import threading, time
import socket
import math
import json
import array
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

 
from threading import Thread 
from socketserver import ThreadingMixIn 



host = socket.gethostbyname(socket.gethostname())
port = 0
server = ("DESKTOP-5L3LMHT", 9090)

class Figure(QGraphicsPixmapItem):
    
    def __init__(self,x,y,color, parent = None):
        self.x=x
        self.y=y
        self.color=color
        QGraphicsPixmapItem.__init__(self, parent)
        self.setOffset(x,y)
        
 
    def __str__(self):
        return 'figure'
    
    def moveFigure(self,x,y):
        if (math.fabs(x-self.x)==200 and math.fabs(y-self.y)==100) or  (math.fabs(y-self.y)==200 and math.fabs(x-self.x)==100):
            self.setOffset(x, y)
            self.x=x
            self.y=y
        
        return 'figure'
    
class Gui(QMainWindow):
    SignalAdd = pyqtSignal(Figure)
    SignalRemove = pyqtSignal(Figure)
    SignalSetTitle = pyqtSignal(str)
    SignalSetQbox = pyqtSignal(str)
    def __init__(self,s):
        super().__init__()
      
        self.color="Белые"
        self.s=s
        self.countClick=0
        self.massPos=[]
        self.initUI()
        self.oldRect = 0
        self.flag = False
        self.first = True
        self.x = 0
        self.y = 0 
        self.scene = QGraphicsScene()
        self.graphics_view = QGraphicsView()
        self.graphics_view.setScene(self.scene)
        
        self.graphics_view.setSceneRect(0, 0, 800, 800)
        
        self.setCentralWidget(self.graphics_view)     
        self.SignalAdd.connect(self.scene.addItem)
        self.SignalRemove.connect(self.scene.removeItem)
        self.SignalSetTitle.connect(self.setWindowTitle)
        self.SignalSetQbox.connect(self.showMessageBox)
 
    def initUI(self):    
        self.setGeometry(300, 100, 802, 802)
        self.setWindowTitle('chess')
        self.show()
    
    def closeEvent(self, event):
        data_set = {"message":"exit"}
        try:
            self.s.sendto(json.dumps(data_set).encode("utf-8"), server)
            self.s.close
            return
        
        except (ConnectionAbortedError,
                    ConnectionResetError):
            print("неполадки с сервером")
            self.s.close
            return
        
        #reply = QMessageBox.question(self, 'Message',
         #   "Do you want to save?", QMessageBox.Yes, QMessageBox.No)

        #if reply == QMessageBox.Yes:
         #   event.accept()
        #else:
            #event.ignore()
 
    def paintEvent(self, e):                   
        if self.flag: #рисуем прямоугольник выделенную ячейку
            if self.oldRect != 0:
                self.scene.removeItem(self.oldRect)
            Rect = QGraphicsRectItem(self.x, self.y, 100, 100)
            Rect.setPen(QPen(Qt.red,  2,))
            self.scene.addItem(Rect)
            self.flag = False
            self.oldRect = Rect
 
        else:
            a=[]
            if self.first: #если первый запуск то рисуем шахматную доску  
                for i in range(8): 
                    for j in range(8):   
                        if (8 - i + 1 + j ) % 2 == 0:
                            Rect = QGraphicsRectItem(i*100, j*100, 100, 100)
                            Rect.setBrush(QColor(101, 67, 33))
                            self.scene.addItem(Rect)
                            if j>=0 and j<2 :
                                pawnW1 = Figure(i*100, j*100, 1,QPixmap('bHorse.png').scaled(99, 99)) # определяем первую фигуру вот ее хочу вынести в отдельный класс
                               # a.append(pawnW1)
                                
                               # pawnW1.setOffset(i*100, j*100)
                                
                            if j>=6 and j<8 :
                                pawnW1 = Figure(i*100, j*100,0,QPixmap('wHorse.png').scaled(99, 99)) # определяем первую фигуру вот ее хочу вынести в отдельный класс
                              #  a.append(pawnW1)
                         
                        
                        else:
                            Rect = QGraphicsRectItem(i*100, j*100, 100, 100)
                            Rect.setBrush(QColor(255, 255, 255)) 
                            Rect.setZvalue=-5
                            self.scene.addItem(Rect)
                    
               # for i in a:
                    #self.scene.addItem(i)
                self.first = False
                        
                        
    def mousePressEvent(self, event): 
        server = ("DESKTOP-5L3LMHT", 9090) 
        self.x = int(event.pos().x()/100)*100 
        self.y = int(event.pos().y()/100)*100
        self.flag = True
        if(self.countClick==0):
            it = self.graphics_view.items(self.x + 50, self.y + 50)
            for k in it:
                if str(type(k)) =="<class '__main__.Figure'>":
                    
                    self.massPos.append(self.x )
                    self.massPos.append(self.y )
                    self.countClick+=1
                    break
              
                else:
                    self.countClick=0
                    
        elif(self.countClick==1):
            self.massPos.append(self.x )
            self.massPos.append(self.y )
            self.countClick+=1
            
        if(self.countClick==2):
            data_set = {"pos":self.massPos}
            try:
                self.s.sendto(json.dumps(data_set).encode("utf-8"), server)
            except (ConnectionAbortedError,
                    ConnectionResetError):
                print("неполадки с сервером")
                self.s.close()
                return
            self.massPos.clear()
            self.countClick=0
            self.x = 0 
            self.y = 0
      
        self.update() 
        
    def get_color(self):
        return self.color
    
    def set_color(self,color):
        self.color=color
        
    def showMessageBox(self,mess):
        {
            QMessageBox.question(self, 'Message',
            mess, QMessageBox.Ok)
          #  if mess=="белые выиграли" or mess=="чёрные выиграли":
               
        }

 # отдельный поток
def run(s,gui,color):
      
     fullDesk=False
     mass=[]
     mass_old=[]
     while True:
             try:
                 data, addr = s.recvfrom(1024)
             except (ConnectionAbortedError,
             ConnectionResetError):
                 gui.SignalSetQbox.emit("неполадки с сервером")
                 return
                 
             
             if(data!=""):
                 
                 json_string = data.decode("utf-8")
                 json_string = json.loads(json_string)
                 mass_dict_key = list(json_string.keys())
                 
                 for dict_key in mass_dict_key:
                     if dict_key == "startPos":
                         
                    
                                 
                         mass = list(json_string[dict_key])
                        
                         for i in mass:
                             if(i[2]==0):
                                 pawnW1 = Figure(i[0], i[1], i[2] ,QPixmap('bHorse.png').scaled(99, 99))
                             if(i[2]==1):
                                 pawnW1 = Figure(i[0], i[1], i[2], QPixmap('wHorse.png').scaled(99, 99))
                             time.sleep(0.01)
                             gui.SignalAdd.emit(pawnW1)
                         fullDesk=True
                     
                     if dict_key == "pos":
                       
                        my_list_pos = list(json_string[dict_key])
                        x0 = my_list_pos[0]
                        x1 = my_list_pos[2]
                        y0 = my_list_pos[1]
                        y1 = my_list_pos[3]
                      
                        for i in gui.scene.items():
                             if(isinstance(i,Figure)):
                                 if(i.x==x0 and i.y==y0):
                                     intColor=i.color
                                     gui.SignalRemove.emit(i)
                                  
                                     if intColor ==1:
                                         pawnW1 = Figure(x1, y1,intColor,QPixmap('wHorse.png').scaled(99, 99))
                                     else:
                                         pawnW1 = Figure(x1, y1,intColor,QPixmap('bHorse.png').scaled(99, 99))
                                     gui.SignalAdd.emit(pawnW1)
                                 elif(i.x==x1 and i.y==y1):
                                     gui.SignalRemove.emit(i)
                                     
                     if dict_key == "message":
                         mess = json_string['message'] 
                         gui.SignalSetQbox.emit(mess)
                     
                     if dict_key == "move":
                        
                         gui.SignalSetTitle.emit(color+json_string['move'])
                     
def main():               

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((host, port))
    except (s.error, OverflowError):
        print("Неполадки с сервером")  
        s.close()
        return
    s.setblocking(1)
            
    app = QApplication(sys.argv)
    gui = Gui(s)        

    try:
        s.sendto(("player join the game ").encode("utf-8"), server)
        data, addr = s.recvfrom(1024)
    except (ConnectionAbortedError,
            ConnectionResetError):
        print("неполадки с сервером")
        s.close()
        return
             #time.sleep(5)
            
    msg = data.decode("utf-8")
    if(msg!="Сервер заполнен"):
        color = msg
        print("Ваши лошадки " + color)
    else:
        print(msg)
        s.close()
        return
    gui.set_color( color)
    gui.SignalSetTitle.emit(color+"(ход белых)")
    join = True       
               
    threading.Thread(target=run,args=(s, gui, color)).start()
    
    app.exec()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
