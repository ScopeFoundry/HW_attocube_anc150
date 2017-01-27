import time
import u3

lj = u3.U3()

try:

	lj.configIO(EnableCounter0=True, EnableCounter1=True, NumberOfTimersEnabled = 2, TimerCounterPinOffset=4, FIOAnalog=0x0F)
	lj.getFeedback(u3.TimerConfig(timer = 0, TimerMode = 10)) # system timer LSW
	lj.getFeedback(u3.TimerConfig(timer = 1, TimerMode = 11)) # system timer MSW

	feedback_req = [
		u3.Timer(timer=1, UpdateReset = False, Value = 0, Mode = None),
		u3.Timer(timer=0, UpdateReset = False, Value = 0, Mode = None),
		u3.Counter(counter = 0, Reset=True),
		u3.Counter(counter = 1, Reset=False)
		]

	for i in range(1000):
		print lj.getFeedback(feedback_req)
		time.sleep(1)
finally:
    lj.close()
