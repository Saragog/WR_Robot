# ROBOT realizowany w ramach zajęć z przedmiotu Wstęp do robotyki
# Wydział Elektroniki I Technik Informacyjnych
# Twórcy:
# Andrzej Dackiewicz
# Mateusz Jarzemski
# Data 14.04.2016

#!/usr/bin/python 
# coding=utf-8   

# Importy
import sys, argparse, time
from ev3dev import *

# ZMIENNE DO PAMIETANIA CZY OBIEKT O KONKRETNYM KOLORZE ZOSTAŁ JUZ PRZENIESIONY CZY TEZ NIE:
# ____________________________________________________________________________
#
red_collected = 0
yellow_collected = 0
object_color = 0 # jesli mamy jakis obiekt to tutaj zapisujemy jego kolor
                 # 0 - puste
                 # 1 - czerwone
                 # 2 - zolte
# ____________________________________________________________________________

number = 0

# _____________________________________________________________________________
# ostatnio wybrany skret ( pomocne przy wychodzeniu z procesu odbierania / odkladania obiektu )

turn = 0
# 1 - lewo
# 2 - prawo

# Deklaracje motorów i sensorów
#______________________________________________________________________________
lmotor = large_motor(OUTPUT_B); assert lmotor.connected    # motor do napędzania lewego koła
rmotor = large_motor(OUTPUT_A); assert rmotor.connected    # motor do napędzania prawego koła
arm = medium_motor(OUTPUT_C); assert arm.connected         # ramie do zamykania / otwierania
cs     = color_sensor();        assert cs.connected        # czujnik koloru do wykrywania koloru zielonego / czerwonego / żółtego
ts     = touch_sensor();        assert ts.connected        # czujnik dotyku do włączania / wyłączania robota
ir_sensor = infrared_sensor();   assert ir_sensor.connected # czujnik do wykrywania odległości wykorzystywany przy wykrywaniu piłki
ls = light_sensor();             assert ls.connected       # czujnik światła do podążania za linią
#______________________________________________________________________________

arm.set(speed_regulation_enabled='on', stop_command='brake') # ustalenie motora z ramieniem aby można było nim sterować
cs.mode = 'RGB-RAW'    # ustawienie trybu na wykrywanie RGB
arm.speed_sp = 200     # ustalenie prędkości ramienia

def openArm():         # funkcja do otwierania ramienia przechowującego obiekt
   global arm
   arm.position_sp = -100
   arm.run_to_abs_pos()

def closeArm():        # funkcja do zamykania ramienia przechowującego obiekt
   global arm
   arm.position_sp = 0
   arm.run_to_abs_pos()

white = 525            # pobrane wartości kolorów i wyznaczenie wartości zadanej
black = 273
mid   = 0.5 * (white + black)

last_error = 0         # nadawanie wartości początkowych dla zmiennych globalnych wykorzystywanych w regulatorze PID
integral   = 0
pid_state = 0
i = 0
speed_mod = 100
correction = 0

def return_object():   # funkcja do zwracania obiektu
   global rmotor       # wykorzystywane zmienne globalne
   global lmotor
   global ts
   global ir_sensor
   global integral
   global pid_state
   global i
   global speed_mod
   global cs
   global red_collected
   global yellow_collected
   global turn
   global last_error
   global object_color

   integral = 0
   pid_state = 0
   i = 0
   speed_mod = 100

   while 1:
      if (cs.value(0) > 90 and cs.value(0) < 200 and cs.value(1) < 60 and cs.value(1) > 10 and cs.value(2) < 40 and cs.value(2) > 5) or (cs.value(0) > 180 and cs.value(0) < 240 and cs.value(1) < 295 and cs.value(1) > 255 and cs.value(2) < 60 and cs.value(2) > 30): # czerwony
         lmotor.stop() # jesli wykryje ktorys kolor to zatrzymaj i ustaw zmienna przechowywania obiektu na puste ( 0 )
         rmotor.stop()
         object_color = 0         
         break

      if ts.value():            # jesli wcisniemy przycisk to reset robota
         lmotor.reset()
         rmotor.reset()
         object_color = 0
         red_collected = 0
         yellow_collected = 0
         return

      pid(0)
      time.sleep(0.01)


   lmotor.run_timed(time_sp = 700, speed_sp = 200)
   rmotor.run_timed(time_sp = 700, speed_sp = 200)
   time.sleep(1.6)

   openArm()          # otwarcie ramienia - wypuszczenie obiektu

   time.sleep(0.6)
                      # wycofanie

   lmotor.run_timed(time_sp = 900, speed_sp = -250)
   rmotor.run_timed(time_sp = 900, speed_sp = -250)
   time.sleep(0.8)
   closeArm()
   # skręt o 180 stopni

   # wykonanie ruchów niezbędnych do poprawnego wyjścia robota z pola
   lmotor.run_timed(time_sp = 550, speed_sp = 400)
   rmotor.run_timed(time_sp = 550, speed_sp = -400)
   time.sleep(1.3)

   lmotor.run_timed(time_sp = 150, speed_sp = 300)
   rmotor.run_timed(time_sp = 150, speed_sp = 300)
   time.sleep(1.3)

   lmotor.run_timed(time_sp = 550, speed_sp = 400)
   rmotor.run_timed(time_sp = 550, speed_sp = -400)
   time.sleep(1.3)

   # jesli wykryty jakis kolor
   if (cs.value(0) > 90 and cs.value(0) < 200 and cs.value(1) < 60 and cs.value(1) > 10 and cs.value(2) < 40 and cs.value(2) > 5) or (cs.value(0) > 180 and cs.value(0) < 240 and cs.value(1) < 295 and cs.value(1) > 255 and cs.value(2) < 60 and cs.value(2) > 30): # czerwony
      lmotor.run_timed(time_sp = 300, speed_sp = 200)
      rmotor.run_timed(time_sp = 300, speed_sp = 200)
      time.sleep(1.3)

      # to zaleznie od wykonanego wczesniej skrętu teraz tez skrecamy aby robot podążał w odpowiednim kierunku
      if turn == 1: # w lewo
         lmotor.run_timed(time_sp = 200, speed_sp = 200)
         rmotor.run_timed(time_sp = 200, speed_sp = 200)
         time.sleep(0.4)
         
         lmotor.run_timed(time_sp = 530, speed_sp = -400)
         rmotor.run_timed(time_sp = 530, speed_sp = 400)
         time.sleep(1.2)
      else:         # w prawo
         lmotor.run_timed(time_sp = 550, speed_sp = 200)
         rmotor.run_timed(time_sp = 550, speed_sp = 200)
         time.sleep(0.6)
         lmotor.run_timed(time_sp = 580, speed_sp = 400)
         rmotor.run_timed(time_sp = 580, speed_sp = -400)
         time.sleep(0.7)

   else:
      # powrot na linie czarno/biala
      while 1:      
         if (cs.value(0) > 90 and cs.value(0) < 200 and cs.value(1) < 60 and cs.value(1) > 10 and cs.value(2) < 40 and cs.value(2) > 5) or (cs.value(0) > 180 and cs.value(0) < 240 and cs.value(1) < 295 and cs.value(1) > 255 and cs.value(2) < 60 and cs.value(2) > 30): # czerwony

            lmotor.run_timed(time_sp = 1350, speed_sp = 200)
            rmotor.run_timed(time_sp = 1350, speed_sp = 200)
            time.sleep(1.35)
            if turn == 1:
               lmotor.run_timed(time_sp = 600, speed_sp = -400)
               rmotor.run_timed(time_sp = 600, speed_sp = 400)
               time.sleep(1.2)
            else: 
               lmotor.run_timed(time_sp = 300, speed_sp = 200)
               rmotor.run_timed(time_sp = 300, speed_sp = 200)
               time.sleep(0.3)
               lmotor.run_timed(time_sp = 600, speed_sp = 400)
               rmotor.run_timed(time_sp = 600, speed_sp = -400)
               time.sleep(0.6)

            turn = 0
            break
         pid(0)
         time.sleep(0.01)

         if ts.value():            # jesli wcisniemy przycisk to reset robota
            lmotor.reset()
            rmotor.reset()
            object_color = 0
            red_collected = 0
            yellow_collected = 0
            return

   lmotor.run_timed(time_sp = 400, speed_sp = 300)
   rmotor.run_timed(time_sp = 400, speed_sp = 300)
   time.sleep(0.4)

   last_error = 0
   integral = 0
   pid_state = 0
   speed_mod = 100
   i = 0

def find_object():     # funkcja do pobierania obiektu
   global rmotor       # zmienne globalne wykorzystane w funkcji
   global lmotor
   global ts
   global ir_sensor
   global integral
   global pid_state
   global i
   global speed_mod
   global cs
   global red_collected
   global yellow_collected
   global turn
   global last_error
   global object_color

   integral = 0
   pid_state = 0
   i = 0
   speed_mod = 100

   armClosed = 0
   zmienna = 0

   while 1:
      if (cs.value(0) > 90 and cs.value(0) < 200 and cs.value(1) < 60 and cs.value(1) > 10 and cs.value(2) < 40 and cs.value(2) > 5): # czerwony
         lmotor.stop()
         rmotor.stop()
         if red_collected == 0: # jesli czerwony jeszcze nie pobrany
            object_color = 1    # ustawiamy aktualny obiekt na czerwony i ze czerwony pobrany
            red_collected = 1
         else:                  # operacja powrotu
            lmotor.run_timed(time_sp = 550, speed_sp = 400)
            rmotor.run_timed(time_sp = 550, speed_sp = -400)
            time.sleep(1.3)

            lmotor.run_timed(time_sp = 150, speed_sp = 300)
            rmotor.run_timed(time_sp = 150, speed_sp = 300)
            time.sleep(1.3)

            lmotor.run_timed(time_sp = 550, speed_sp = 400)
            rmotor.run_timed(time_sp = 550, speed_sp = -400)
            time.sleep(1.3)
            zmienna = 1
            closeArm()

            time.sleep(0.6)
         
         break
      elif (cs.value(0) > 180 and cs.value(0) < 240 and cs.value(1) < 295 and cs.value(1) > 255 and cs.value(2) < 60 and cs.value(2) > 30): # zolty
         lmotor.stop()
         rmotor.stop()
         if yellow_collected == 0: # jesli zolty jeszcze nie pobrany
            object_color = 2       # to ustawiamy aktualny obiekt na zolty i ze zolty pobrany
            yellow_collected = 1
         else:                     # operacja powrotu
            lmotor.run_timed(time_sp = 550, speed_sp = 400)
            rmotor.run_timed(time_sp = 550, speed_sp = -400)
            time.sleep(1.3)

            lmotor.run_timed(time_sp = 150, speed_sp = 300)
            rmotor.run_timed(time_sp = 150, speed_sp = 300)
            time.sleep(1.3)

            lmotor.run_timed(time_sp = 550, speed_sp = 400)
            rmotor.run_timed(time_sp = 550, speed_sp = -400)
            time.sleep(1.3)
            zmienna = 1
            closeArm()

            time.sleep(0.6)
         break
      if ir_sensor.value() < 6: # zamykanie ramienia jesli odpowiednio blisko obiekt jest
         armClosed = 1
         closeArm()

      if ts.value():            # jesli wcisniemy przycisk to reset robota
         lmotor.reset()
         rmotor.reset()
         object_color = 0
         red_collected = 0
         yellow_collected = 0
         return

      pid(0)
      time.sleep(0.01)

   if zmienna == 0:
      
      if armClosed == 0:        # jesli nie wykryto obiektu to do przodu az wykryjemy
         lmotor.run_forever(speed_sp = 100)
         rmotor.run_forever(speed_sp = 100)
         while ir_sensor.value() > 6:
            armClosed += 1      # potem wiemy o ile się cofnąć aby z powrotem pojawić się na linii
            time.sleep(0.01)
         lmotor.stop()
         rmotor.stop()
         closeArm()

         time.sleep(0.6)


      lmotor.run_timed(time_sp = 550, speed_sp = 400)  # operacje manewru aby pojawić się na linii tak by czujnik był w odpowiednim położeniu
      rmotor.run_timed(time_sp = 550, speed_sp = -400)
      time.sleep(1.3)

      lmotor.run_timed(time_sp = 150, speed_sp = 300)
      rmotor.run_timed(time_sp = 150, speed_sp = 300)
      time.sleep(1.3)

      lmotor.run_timed(time_sp = 550, speed_sp = 400)
      rmotor.run_timed(time_sp = 550, speed_sp = -400)
      time.sleep(1.3)

      lmotor.run_forever(speed_sp = 100)
      rmotor.run_forever(speed_sp = 100)
      while armClosed > 0:
         armClosed -= 1
         time.sleep(0.01)
   
      lmotor.stop()
      rmotor.stop()
      time.sleep(0.3)

   speed_mod = 100   
   integral = 0
   pid_state = 0
   i = 0
   last_error = 0

   while 1:
      pid(0)
      if cs.value(0) > 5 and cs.value(0) < 50 and cs.value(1) < 145 and cs.value(1) > 80 and cs.value(2) < 75 and cs.value(2) > 15: # zielone
         lmotor.run_timed(time_sp = 1350, speed_sp = 200)
         rmotor.run_timed(time_sp = 1350, speed_sp = 200)
         time.sleep(1.35)
         if turn == 1: # zaleznie od zapisanego skretu teraz skrecamy tak by jechac w odpowiednim kierunku
            lmotor.run_timed(time_sp = 600, speed_sp = -400)
            rmotor.run_timed(time_sp = 600, speed_sp = 400)
            time.sleep(1.2)
         else: 
            lmotor.run_timed(time_sp = 180, speed_sp = 200)
            rmotor.run_timed(time_sp = 180, speed_sp = 200)
            time.sleep(0.3)
            lmotor.run_timed(time_sp = 600, speed_sp = 400)
            rmotor.run_timed(time_sp = 600, speed_sp = -400)
            time.sleep(0.6)
           
            

         turn = 0
         break
      time.sleep(0.01)

      if ts.value():       # resetowanie robota pod wpływem wciśnięcia przycisku
         lmotor.reset()
         rmotor.reset()
         object_color = 0
         red_collected = 0
         yellow_collected = 0
         return

   lmotor.run_timed(time_sp = 400, speed_sp = 300)
   rmotor.run_timed(time_sp = 400, speed_sp = 300)
   time.sleep(0.4)

   last_error = 0
   integral = 0
   pid_state = 0
   speed_mod = 100
   i = 0

def find_green():       # metoda znajduje pole zielone i jesli nic nie mamy w ramieniu to mozna pojechac i cos wziac
   
   global rmotor
   global lmotor
   global ts
   global ir_sensor
   global integral
   global pid_state
   global i
   global speed_mod
   global cs
   global turn
   global last_error

   #___________
   # WYKRYCIE KOLORU ZIELONEGO OZNACZAJACEGO OBECNOSC OBIEKTU DO ZEBRANIA
   if cs.value(0) > 10 and cs.value(0) < 45 and cs.value(1) < 135 and cs.value(1) > 85 and cs.value(2) <65 and cs.value(2) > 25:
     
      if object_color != 0:  # jesli cos mamy w ramieniu to pomijamy poprzez przejechanie prosto
         lmotor.run_forever(speed_sp=200)
         rmotor.run_forever(speed_sp=200)
         time.sleep(0.4)
         return 0;

      lmotor.stop()
      rmotor.stop()
      openArm() # otworzenie ramienia w celu pobrania obiektu
      number = 0
  
      time.sleep(0.5)

      speed_mod = 100   
      integral = 0
      pid_state = 0
      i = 0
      last_error = 0

      lmotor.run_timed(time_sp = 300, speed_sp = 300)
      rmotor.run_timed(time_sp = 300, speed_sp = -150)
      time.sleep(0.8)

      if cs.value(0) > 10 and cs.value(0) < 45 and cs.value(1) < 140 and cs.value(1) > 80 and cs.value(2) < 70 and cs.value(2) > 20: # wykrycie koloru aby sprawdzic w która strone skrecic
         lmotor.run_timed(time_sp = 300, speed_sp = -300)
         rmotor.run_timed(time_sp = 300, speed_sp = 150)
         time.sleep(0.8)

         lmotor.run_timed(time_sp = 1200, speed_sp = 400)
         rmotor.run_timed(time_sp = 1200, speed_sp = -50)
         time.sleep(1.0)

         turn = 2 # zapisanie skretu jako w prawo

      else:
         lmotor.run_timed(time_sp = 300, speed_sp = -300)
         rmotor.run_timed(time_sp = 300, speed_sp = 150)
         time.sleep(0.8)
         
         lmotor.run_timed(time_sp = 875, speed_sp = -150)
         rmotor.run_timed(time_sp = 875, speed_sp = 350)
         time.sleep(1.0)

         turn = 1 # zapisanie skretu jako w lewo

      lmotor.run_timed(time_sp = 700, speed_sp = 200)
      rmotor.run_timed(time_sp = 700, speed_sp = 200)

      time.sleep(0.8)

      find_object() # uruchomienie wyszukiwania obiektu

      lmotor.stop()
      rmotor.stop()
      return 0;

def find_red(): # wyrkycie koloru czerwonego
                # jesli mamy obiekt czerwony to oddajemy go / jesli nie to pomijamy
   global rmotor
   global lmotor
   global ts
   global ir_sensor
   global integral
   global pid_state
   global i
   global speed_mod
   global cs
   global turn
   global last_error

   #___________
   # WYKRYCIE KOLORU CZERWONEGO OZNACZAJACEGO OBECNOSC OBIEKTU DO ODDANIA
   if cs.value(0) > 90 and cs.value(0) < 200 and cs.value(1) < 60 and cs.value(1) > 10 and cs.value(2) < 40 and cs.value(2) > 5:
      # chodzenie za linia CZERWONA
      if object_color != 1:
         lmotor.run_forever(speed_sp=200)
         rmotor.run_forever(speed_sp=200)
         time.sleep(0.4)
         return 0;

      lmotor.stop()
      rmotor.stop()
      number = 0
      time.sleep(0.5)

      speed_mod = 100   
      integral = 0
      pid_state = 0
      i = 0
      last_error = 0

      lmotor.run_timed(time_sp = 300, speed_sp = 300)
      rmotor.run_timed(time_sp = 300, speed_sp = -150)
      time.sleep(0.8)

      if cs.value(0) > 90 and cs.value(0) < 200 and cs.value(1) < 60 and cs.value(1) > 10 and cs.value(2) < 40 and cs.value(2) > 5: # wykrycie koloru aby sprawdzic w która strone skrecic
         lmotor.run_timed(time_sp = 300, speed_sp = -300)
         rmotor.run_timed(time_sp = 300, speed_sp = 150)
         time.sleep(0.8)

         lmotor.run_timed(time_sp = 1200, speed_sp = 400)
         rmotor.run_timed(time_sp = 1200, speed_sp = -50)
         time.sleep(1.0)
         turn = 2 # zapisanie jako skret w prawo
      else:
         lmotor.run_timed(time_sp = 300, speed_sp = -300)
         rmotor.run_timed(time_sp = 300, speed_sp = 150)
         time.sleep(0.8)
         
         lmotor.run_timed(time_sp = 875, speed_sp = -150)
         rmotor.run_timed(time_sp = 875, speed_sp = 350)
         time.sleep(1.0)
         turn = 1 # zapisanie jako skret w lewo

      lmotor.run_timed(time_sp = 750, speed_sp = 200)
      rmotor.run_timed(time_sp = 750, speed_sp = 200)

      time.sleep(0.8)
      return_object() # uruchomienie operacji oddawania obiektu

      lmotor.stop()
      rmotor.stop()
	  
      return 0;


def find_yellow():  # podobnie jak w przypadku wykrycia koloru czerwonego
   
   global rmotor # wykorzystane zmienne globalne
   global lmotor
   global ts
   global ir_sensor
   global integral
   global pid_state
   global i
   global speed_mod
   global cs
   global turn
   global last_error
   global object_color

   #___________
   # WYKRYCIE KOLORU ZOLTEGO OZNACZAJACEGO OBECNOSC OBIEKTU DO ZEBRANIA
   if cs.value(0) > 175 and cs.value(0) < 245 and cs.value(1) < 300 and cs.value(1) > 250 and cs.value(2) < 65 and cs.value(2) > 25:
      

      print object_color

      if object_color != 2: # pominiecie koloru zoltego jesli nie mamy nic lub mamy czerwony obiekt a nie zolty
         lmotor.run_forever(speed_sp=200)
         rmotor.run_forever(speed_sp=200)
         time.sleep(0.4)
         return 0;

      lmotor.stop()
      rmotor.stop()
      number = 0
      time.sleep(0.7)

      lmotor.run_timed(time_sp = 300, speed_sp = 300)
      rmotor.run_timed(time_sp = 300, speed_sp = -150)
      time.sleep(0.8)

      if cs.value(0) > 180 and cs.value(0) < 240 and cs.value(1) < 295 and cs.value(1) > 255 and cs.value(2) < 60 and cs.value(2) > 30: # wykrycie koloru aby sprawdzic w która strone skrecic
         lmotor.run_timed(time_sp = 300, speed_sp = -300)
         rmotor.run_timed(time_sp = 300, speed_sp = 150)
         time.sleep(0.8)

         lmotor.run_timed(time_sp = 1150, speed_sp = 400)
         rmotor.run_timed(time_sp = 1150, speed_sp = -50)
         time.sleep(1.3)
         turn = 2 # zapisanie jako skret w prawo
      else:
         lmotor.run_timed(time_sp = 300, speed_sp = -300)
         rmotor.run_timed(time_sp = 300, speed_sp = 150)
         time.sleep(0.8)
         
         lmotor.run_timed(time_sp = 875, speed_sp = -150)
         rmotor.run_timed(time_sp = 875, speed_sp = 350)
         time.sleep(1.0)
         turn = 1 # zapisanie jako skret w lewo

      lmotor.run_timed(time_sp = 700, speed_sp = 200)
      rmotor.run_timed(time_sp = 700, speed_sp = 200)

      time.sleep(0.8)

      return_object() # operacja oddawania obiektu

      lmotor.stop()
      rmotor.stop()
      return 0;


def pid(speed_m): # funkcja obslugujaca regulator PID
   
   global integral # zmienne globalne wykorzystywane w funkcji
   global last_error
   global pid_state
   global i
   global rmotor
   global lmotor
   global cs
   global ls
   global mid
   global correction

   color_sum = ls.value()
   error      = mid - color_sum
   if error > 0 :error_i = error * 1.0
   else: error_i = error
   integral   = integral + error_i
   derivative = error - last_error
   last_error = error

   speed_mod = speed_m
   
   correction = int(1.0*( 1.4*3.6* error + (0.34) * integral + 0.8*9.7* derivative)) # wyliczenie korekty

   if pid_state == 0:
      speed_mod = speed_m  
      if correction < 0 : i = i + 1
      else: 
         i = 0
         pid_state = 1
      if i > 6:             
         speed_mod = 0 
         pid_state = 2
   
   elif pid_state == 1:
      speed_mod = speed_m
      if correction >= 0 : i = i + 1
      else: 
         i = 0
         pid_state = 0   
      if i > 6:
         speed_mod = 0 
         pid_state = 3

   elif pid_state == 2:
      speed_mod = 0
      if correction >= 0 : 
         pid_state = 1
         i = 0
   elif pid_state == 3:
      speed_mod = 0 
      if correction < 0 : 
         pid_state = 0
         i = 0
                    
   if correction > (700 - speed_mod):
      correction = 699 - speed_mod
   elif correction < -(700 - speed_mod):
      correction = -699 + speed_mod
     
   lmotor.run_forever(speed_sp=200+speed_mod-correction) # nadawanie predkosci silnikom na podstawie wyliczonej korekty
   rmotor.run_forever(speed_sp=200+speed_mod+correction)

# koniec funkcji pid


while 1:  # główna petla programu
   lmotor.speed_regulation_enabled = 'on' # ustalenie trybów działania motorów aby można było nadawać im prędkość
   rmotor.speed_regulation_enabled = 'on'
   lmotor.stop_command='brake'
   rmotor.stop_command='brake'

   closeArm()  # na początku działania programu zamykamy ramię

   time.sleep(0.6)  
   while ts.value() == 0:  # oczekiwanie na włączenie robota
      time.sleep(0.6)
   time.sleep(0.7)

   last_error = 0
   integral   = 0
   pid_state = 0
   i = 0
   speed_mod = 0


   while 1: # pętla sterująca regulatorem PID i wykrywajaca kolory
      pid(0)
      time.sleep(0.01)

# ______________________________________________________________________________________
#
# WYKRYWANIE KOLOROW OZNACZAJACYCH OBECNOSC OBIEKTOW DO TRANSPORTU
# ______________________________________________________________________________________


      if find_green() == 1:
         break

      if find_red() == 1:
         break

      if find_yellow() == 1:
         break
         
      if ts.value(): # można w każdej chwili zatrzymać robota
         lmotor.reset()
         rmotor.reset()
         object_color = 0
         red_collected = 0
         yellow_collected = 0
         break
		 