import pymongo
from pymongo import MongoClient
import pprint
import time
import socket
import threading
import subprocess

hostname = socket.gethostname()
status_key = hostname + "_status"

client = MongoClient('mongodb://isingh:FreePass123@ds155293.mlab.com:55293/iqcluster')


db = client['iqcluster']
nodec = db['nodestats']
if False:
  ncid = nodec.insert_one({"master" : 0, "node001" : 0, "node002":0, "node003" : 0}).inserted_id

ncpost = nodec.find_one();
print 'int or str', type(ncpost['node001'])
nodec.update({"_id" : ncpost["_id"]}, { "$set" : {"node001" : 0 }})

pprint.pprint(ncpost)

jobs = db.Jobs

counter_lock = threading.Lock()
status_lock = threading.Lock()
schedc = db['schedules']

class RunJobThread(threading.Thread):
  def __init__(self,job,myid):
    super(RunJobThread, self).__init__()
    self.job=job
    self.myid = myid

  def run(self):
    global jobs
    global nodec
    global hostname
    _id = self.job['_id']
    print 'running job:', _id
    my_status_key = hostname + "_status"
    with status_lock:
      myjob = jobs.find_one({"_id" : _id})
      if myjob[my_status_key] == 'pending':
        jobs.update({"_id" : _id}, { "$set" : {my_status_key : "running" }})
    with counter_lock:
      ncpost = nodec.find_one() # get current cluster state
      ncid = ncpost['_id']
      numprocs = ncpost[hostname] # get current counter value
      numprocs = numprocs + 1
      nodec.update({"_id" : ncid}, { "$set" : {hostname : numprocs }}) # update counter value
    command = self.job['cmd']
    command = command + ' > ' + '/home/iqadmin/meteor_projects/logs/' + hostname + '/' + _id  + '_' + str(self.myid) + '.log'
    ret = subprocess.call(command, shell=True)
    with status_lock:
      myjob = jobs.find_one({"_id" : _id})
      if 'error' not in myjob[my_status_key]:
        if ret == 0:
          jobs.update({"_id" : _id}, { "$set" : {my_status_key : "complete" }})
        else:
          final_status = 'error(' + str(ret) + ')'
          jobs.update({"_id" : _id}, { "$set" : {my_status_key : final_status }})
    with counter_lock:
      ncpost = nodec.find_one() # get current cluster state
      ncid = ncpost['_id']
      numprocs = ncpost[hostname] # get current counter value
      numprocs = numprocs - 1
      nodec.update({"_id" : ncid}, { "$set" : {hostname : numprocs }}) # update counter value


def RunJob(job):
  global schedc
  _id = job['_id']
  print 'RunJob called with job =',_id
  schedule = schedc.find_one({"job_id" : _id})
  numprocs = schedule[hostname]
  for i in range(numprocs):
    RunJobThread(job,i).start()



while True:
  foundJob=False
  for job in jobs.find({"queue": "priority", "scheduled" : "yes", status_key : "pending"}).sort('createdAt', pymongo.ASCENDING):
    foundJob=True
    print 'helo'
    print 'job=',job
    RunJob(job)
   
  for job in jobs.find({"queue": "standard", "scheduled" : "yes", status_key : "pending"}).sort('createdAt', pymongo.ASCENDING):
    foundJob=True
    RunJob(job)
    break # breaks just after executing the first available job in standard queue to check for priority queue again
  if not foundJob: # if not found Job
    time.sleep(5) # no job to run right now, re-check after 5 seconds


