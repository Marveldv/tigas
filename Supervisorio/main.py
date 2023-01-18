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

class MyWidget(MDScreen):
    
    
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
        
    def lerdado(self,tipo):
        """
        Método para leitura de um dado da Tabela MODBUS
        """
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
        # addr=int(self.ids.addr2)
        # pass
        
       
            
    def conectar(self):
        """
        Metodo para conectar em um servidor ModBus
        """
        pass
    
    def updater(self):
        """
        Metodo que repete as funções para uma função continua
        """
        pass
    
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
    