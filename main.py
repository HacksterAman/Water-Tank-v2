from IO import *
from Global import *
import _thread

sleep(3)

def button(B, long_press_threshold=3):
    if not B.value():
        Buzzer.on()
        press_start_time = time.ticks_ms()  # Record the start time of the button press
        while not B.value():
            pass
        press_duration = time.ticks_ms() - press_start_time  # Calculate the duration of the button press
        Buzzer.off()

        if press_duration < long_press_threshold * 1000:
            return 1  # Short press
        else:
            return -1  # Long press
    else:
        return 0


def set_start(mode):
  global start
  start=mode
  file.seek(0)
  file.write(str(int(mode)))
  file.flush()

def set_min(level):
  global min
  min=level
  file.seek(1)
  file.write(str(level))
  file.flush()

def set_max(level):
  global max
  max=level
  file.seek(2)
  file.write(str(level))
  file.flush()
  
def set_over(mode):
  global over
  over=mode
  file.seek(3)
  file.write(str(int(mode)))
  file.flush()

def new_level():
  if not In_100.value():
    return 4
  elif not In_75.value():
    return 3
  elif not In_50.value():
    return 2
  elif not In_25.value():
    return 1
  else:
    return 0

def printlines(lines,invert=[0]):
  if len(lines[0])==9:
    font=Font_Thick
  else:
    font=Font_Thin
  for i in range(3):
    font.printstring(lines[i],i+1 in invert)
  oled.show()
  Writer.set_textpos(0,0)

def option(o):
  i=[1,2,3]
  O=[]
  selected=1
  for x in o:
    O+=[x+' '*(9-len(x))]
  printlines(O,[1])
  while not button(B_Select):
    if button(B_Next):
      i=i[1:]+i[:1]
      selected=i[0]
      printlines(O,[selected])
  return selected

async def task_indicator():
  if power:
    if overflowing:
      Led.toggle()
      asyncio.sleep_ms(250)
    elif filling:
      Led.toggle()
      asyncio.sleep_ms(500)
    else:
      Led.on()
  else:
    Led.off()

def options(o):
  if o==0:
    return ['Back','Controls','Limits']
  elif o==1:
    return ['Back','Stop' if start else 'Start','Overflow']
  elif o==2:
    return ['Back','Max  '+ str(max*25)+'%','Min  '+ str(min*25)+'%']
  elif o==3:
    return ['100%','75%','50%']
  elif o==4:
    return ['50%','25%','0%']

def screen_control():
  #options={0:['Back','Controls','Limits'],1:['Back','Stop' if start else 'Start','Overflow'],2:['Back','Max  '+ str(max*25)+'%','Min  '+ str(min*25)+'%'],3:['100%','75%','50%'],4:['50%','25%','0%']}
  while True:
    selected=option(options(0))
    # ['Back','Controls','Settings']
    if selected==2:
      selected=option(options(1))
      # ['Back','Stop' if start else 'Start','Overflow']
      if selected==2:
        set_start(not start)
        return
      elif selected==3:
        set_over(not over)
        return
    elif selected==3:
      while True:        
        selected=option(options(2))
        # ['Back','Max  '+ str(max*25)+'%','Min  '+ str(min*25)+'%']
        if selected==2:
          selected=option(options(3))
          # ['100%','75%','50%']
          if selected==1:
            set_max(4)
          elif selected==2:
            set_max(3)
          else:
            set_max(2)
          if max-min<=2:
            set_min(max-2)             
        elif selected==3:
          selected=option(options(4))
          # ['50%','25%','0%']
          if selected==1:
            set_min(2)
          elif selected==1:
            set_min(1)
          else:
            set_min(0)
          if max-min<=2:
            set_max(min+2)
        else:
          break
    else:
      oled.fill(0)
      oled.show()
      return
    
def task_screen_idle():
  count=10
  invert=[0]
  while True:
    if button(B_Select):
      screen_control()
    else:
      lines=[]
      filled=str(level*25)
      if starting:
        lines=['Starting Motor','Level'+' '*(12-2*len(filled))+filled+'%','']
      elif filling:
        if overflowing:
          lines=['  Overflowing  ',' '*(12-len(str(over_timer)))+str(over_timer)+' '*(12-len(str(over_timer))),'Filled'+' '*(12-2*len(filled))+filled+'%']
        else:
          lines=['  Motor is On   ','Filled'+' '*(12-2*len(filled))+filled+'%','']
      else:
        lines=['  Motor is Off  ','Level'+' '*(12-2*len(filled))+filled+'%','']
      
      if count==0:
        count=10
        if invert==[0]:
          invert=[1,2,3]
        else:
          invert=[0]
      printlines(lines,invert)
      count-=1
      sleep(1)

# For controlling motor
async def motor(mode):
  global starting
  starting=mode
  filling=mode
  if mode:
    await asyncio.sleep(3)
    Relay1.on()
    await asyncio.sleep(13)
    Relay2.on()
    await asyncio.sleep(3)
    Relay2.off()
    starting=False
  else:
    Relay2.off()
    Relay1.off()

# For overflowing tank for 100 seconds
async def overflow():
  global overflowing,over_timer
  overflowing=True  
  for i in range(100,-1,-1):
    over_timer=i
    await asyncio.sleep(1)    
  set_start(False)
  set_over(False)
  overflowing=False

async def task_main():
  global power,level
  while True:
    # For Indicating Status
    indicator=asyncio.create_task(task_indicator())
    
    power=In_Power.value()
    await asyncio.sleep(1)
    
    # For checking Changes in Tank Level
    if new_level()!=level:
      await asyncio.sleep(1)
      if new_level()!=level:
        await asyncio.sleep(1)
        if new_level()!=level:
          level=new_level()
          print('Tank Water Level is changed to',level)
          await asyncio.sleep(1)

    # For contolling Start/Stop according to Min and Max Limits
    if level<=min and not start:
      set_start(True)
    elif level>=max and start:
      # Checking for overflow setting
      if over:
        # Checking conditions for Overflowing
        if filling and over and level==4 and not overflowing:
          overflow_task=asyncio.create_task(overflow())
      else:
        set_start(False)

    # For checking conditions to Control Motor
    if start and power:
      if not filling:
        motor_task=asyncio.create_task(motor(True))                    
    elif filling:
      motor_task.cancel()
      await motor(False)
      if overflowing: 
        # Cancelling task if Overflowing
        overflow_task.cancel()
        overflowing=False   

_thread.start_new_thread(task_screen_idle,()) 
asyncio.run(task_main())
