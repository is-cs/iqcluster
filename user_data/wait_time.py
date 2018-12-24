import time
import socket

hostname = socket.gethostname()

st = time.time()
print hostname, '- This program runs for 1 minute, wakes up every second and prints the time diff.'
while True:
  et = time.time()
  diff = et - st
  if diff < 60:
    print 'elapsed_time:', diff,'seconds'
    time.sleep(1)
  else:
    break


