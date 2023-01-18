from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from threading import Thread, Lock
from time import sleep
from pyModbusTCP.client import ModbusClient
from kivy.core.window import Window
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
from kivy.lang.builder import Builder
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivy_garden.graph import Graph
from kivy_garden.graph import LinePlot
from timeseriesgraph import TimeSeriesGraph 
from lib import Soft,Inversor,Direta
from datetime import datetime

class MyWidget(MDScreen):

    IP = '192.168.0.13'
    Port = 502

    #Constantes
    Driver = 1324 #Indereço do Driver
    DriverI= 3 #Valor inicial do Driver

    _UpdateWidgets = True

    Seguranca = True

    Soft = 1316  #Partida Soft
    Inver = 1312 #Partida Inversa
    Direta = 1319 #Partida direta

    _Escrita = {}
    
    Endereços = {'Temperatura_R':{'addr':700,'tag':'FP','Div':10},
             'Temperatura_S':{'addr':702,'tag':'FP','Div':10},         
             'Temperatura_T':{'addr':704,'tag':'FP','Div':10},
             'Temperatura_CARC':{'addr':706,'tag':'FP','Div':10},
             'Tensão_RS':{'addr':847,'tag':'HR','Div':10},
             'Tensão_ST':{'addr':848,'tag':'HR','Div':10},         
             'Tensão_TR':{'addr':849,'tag':'HR','Div':10},
             'Corrente_R':{'addr':840,'tag':'FP','Div':100},
             'Corrente_S':{'addr':841,'tag':'FP','Div':100},         
             'Corrente_T':{'addr':842,'tag':'FP','Div':100},
             'Corrente_N':{'addr':843,'tag':'FP','Div':100},
             'Corrente_MED':{'addr':845,'tag':'FP','Div':100},

             'RPM':{'addr':727,'tag':'FP','Div':1},
             'Torque':{'addr':1334,'tag':'FP','Div':1},
             'Pressao':{'addr':710,'tag':'FP','Div':1},
             'Vazao':{'addr':712,'tag':'FP','Div':1},
             'Porcentagem do reservatorio':{'addr':714,'tag':'FP','Div':1}, 
            }
    
    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._modbusClient = ModbusClient()
        self.Soft =  Soft()
        self.Inversor = Inversor()
        self.Direta = Direta()
        self._meas = {}
        self.inicio = False

        self.ids.hostname.text = self.IP
        self.ids.port.text = self.Port
        
    def lerdado(self,tipo):
        """
        Método para leitura de um dado da Tabela MODBUS
        """
        self._meas['timestamp'] = datetime.now()
        for key,value in self.Endereços.items():
            if value[key]['tag'] == 'HR':
                self._meas[key]=self._modbusClient.read_holding_registers(value[key]['addr'],1)[0]/value[key]['Div']
            if self.Dados[key]['tag'] == 'FP':
                result = self._modbusClient.read_holding_registers(value[key]['addr'], 2)
                decoder = BinaryPayloadDecoder.fromRegisters(result,Endian.Big,Endian.Little) 
                self._meas[key]=decoder.decode_32bit_float()/value[key]['Div']
    
    
    def escreverdado(self,tipo):
        """
        Método para escrita de um dado da Tabela MODBUS
        """
        for key, value in self._Escrita.items():
            self._modbusClient.write_single_register(int(key),value[key])
        
       
            
    def conectar(self):
        """
        Metodo para conectar em um servidor ModBus
        """
        self._modbusClient.port = self.ids.hostname.text
        self._modbusClient.host = int(self.ids.port.text)
        try:
            self._modbusClient.open()
            if self._modbusClient.is_open:
                self.updateThread = Thread(target=self.updater)
                self._modbusClient.write_single_register(self.Driver,self.DriverI)
                self.updateThread.start()
            else:
                print("Error 1: Falha na Conexao")
        except Exception as e:
            print("Error 2: ",e.args)
    
    def updater(self):
        """
        Metodo que repete as funções para uma função continua
        """
        try:
            while self._UpdateWidgets:
                self.lerdado()
                self.UpdadteGUI()
                self.escreverdado()
                sleep(1)

        except Exception as e:
            print("Error 3: ",e.args)
            self.conectar()

    def UpdadteGUI(self):
        #Atualiza as Labels
        for key, value in self.Endereços.items():
            self.ids[key].text = str(round(self._meas[key],2))

        #Atualiza o grafico
        self.ids.graph.updateGraph((self._meas['timestamp'],self._meas['Porcentagem do reservatorio']),0)
    
    def alternar(self):
        if self.inicio == True:
            if self.ids.ligar.text == "Ligar":
                self.ids.ligar.text= "Desligar"
            else:
                self.ids.ligar.text= "Ligar"

            
    def modo_init(self,modo):
        self.inicio = True
        self.ids.modo_init.clear_widgets()
        if modo == 1:
            self.ids.modo_init.add_widget(self.Soft)
        if modo == 2:
            self.ids.modo_init.add_widget(self.Inversor)
        if modo == 3:
            self.ids.modo_init.add_widget(self.Direta)

    def Partida(self): #da a partida do motor
        try:
            if self.ids.ST.text == "START":
                self.ids.ST.text = "STOP"
                self.Seguranca = False
                if self.Start == 1:
                    self._Escrita[str(self.Soft)] = 1
                    self._Escrita[str(self.Inver)] = 0
                    self._Escrita[str(self.Direta)] = 0
                elif self.Start == 2:
                    self._Escrita[str(self.Inver)] = 1
                    self._Escrita[str(self.Soft)] = 0
                    self._Escrita[str(self.Direta)] = 0
                elif self.Start == 3:
                    self._Escrita[str(self.Direta)] = 1
                    self._Escrita[str(self.Soft)] = 0
                    self._Escrita[str(self.Inver)] = 0
                else:
                    self._Escrita[str(self.Soft)] = 0
                    self._Escrita[str(self.Inver)] = 0
                    self._Escrita[str(self.Direta)] = 0
                    self.Seguranca = True

            else:
                self.ids.ST.text = "START"
                self._Escrita[str(self.Soft)] = 0
                self._Escrita[str(self.Inver)] = 0
                self._Escrita[str(self.Direta)] = 0
                self.Seguranca = True
        except Exception as e:
            print("Error 4: ",e.args) 
    
    def On_Start(self,Start):
        if self.Seguranca:
            self.Start = Start
            self._modbusClient.write_single_register(self.Driver,self.Start)
        
class BasicApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette= "Blue"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.accent_palette = "Blue"
        return MyWidget()

class Tab(MDFloatLayout,MDTabsBase):
    pass


if __name__ == "__main__":
    Builder.load_string(open("mywidget.kv",encoding="utf-8").read(),rulesonly=True)
    BasicApp().run()
    
    
