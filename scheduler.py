import pymongo
from pymongo import MongoClient
import pprint
import time

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

def canSchedule(job):
  _id = job['_id']
  print '\n###\nscheduling job:'
  pprint.pprint(job)
  ncpost = nodec.find_one() # get current cluster state
  jcap = 4  # max 4 procs on any node
  vm = jcap - ncpost['master']
  v1 = jcap - ncpost['node001']
  v2 = jcap - ncpost['node002']
  v3 = jcap - ncpost['node003']
  bm = False
  b1 = False
  b2 = False
  b3 = False
  vsum=0
  if job['master_status'] != 'excluded':
    vsum = vsum + vm
    bm = True
  if job['node001_status'] != 'excluded':
    vsum = vsum + v1
    b1 = True
  if job['node002_status'] != 'excluded':
    vsum = vsum + v2
    b2 = True
  if job['node003_status'] != 'excluded':
    vsum = vsum + v3
    b3 = True
  needsum = int(job['numprocs'])
  if needsum > vsum:
    return False
  # schedule and wait for launchers to start running the job
  schedule = {"job_id" : _id, "master" : 0, "node001" : 0, "node002" : 0, "node003": 0}
  needed = {"master" : False, "node001" : False, "node002" : False, "node003" : False };
  bNotExcluded = {"master" : bm, "node001" : b1, "node002" : b2, "node003" : b3 };
  if bm and needsum > 0:
    slots = min(needsum, vm)
    schedule['master'] = slots
    needsum = needsum - slots
    needed['master'] = True
  if b1 and needsum > 0:
    slots = min(needsum, v1)
    schedule['node001'] = slots
    needsum = needsum - slots
    needed['node001'] = True
  if b2 and needsum > 0:
    slots = min(needsum, v2)
    schedule['node002'] = slots
    needsum = needsum - slots
    needed['node002'] = True
  if b3 and needsum > 0:
    slots = min(needsum, v3)
    schedule['node003'] = slots
    needsum = needsum - slots
    needed['node003'] = True

  job_updates = {}
  for key in needed.keys():
    if not needed[key] and bNotExcluded[key]:
      job_updates[key + '_status'] = 'no need'
  job_updates['scheduled'] = 'yes'
  print '\n---\nbNotExcluded:'
  pprint.pprint(bNotExcluded)
  print '\n---\nneeded:'
  pprint.pprint(needed)
  print '\n---\njob_updates:'
  pprint.pprint(job_updates)
  print '\n---\nschedule:'
  pprint.pprint(schedule)
  schedc = db['schedules']
  schedc.insert_one(schedule)
  jobs.update({"_id" : _id}, { "$set" : job_updates})
  # now we need to wait for all launchers to start executing
  bWait = True
  while bWait:
    updatedJob = jobs.find_one({"_id" : _id})
    sm = updatedJob['master_status']
    s1 = updatedJob['node001_status']
    s2 = updatedJob['node002_status']
    s3 = updatedJob['node003_status']
    # v_s = ['complete','excluded','running','no need'] # valid statuses
    if (sm != 'pending') and (s1 != 'pending') and (s2 != 'pending') and (s3 != 'pending'):
      bWait=False
      print '\n---\nwait over!'
    else:
      bWait=True 
      print '\n---\nhave to wait. sm=',sm,', s1=',s1,', s2=',s2,', s3=',s3
      time.sleep(1) # sleep for one second, and then check again whether everyone started executing
  return True

while True:
  foundJob=False
  bCanSchedule=False
  for job in jobs.find({"queue": "priority", "scheduled" : "no"}).sort('createdAt', pymongo.ASCENDING):
    foundJob=True
    pprint.pprint(job)
    bCanSchedule = canSchedule(job)
    if not bCanSchedule:
      break
  
  if not foundJob:
    for job in jobs.find({"queue": "standard", "scheduled" : "no"}).sort('createdAt', pymongo.ASCENDING):
      foundJob=True
      pprint.pprint(job)
      bCanSchedule = canSchedule(job)
      if not bCanSchedule:
        break
  if not foundJob or (foundJob and not bCanSchedule): # if not found Job, or, did find Job but could not schedule it
    time.sleep(5) # jobs are running, can't schedule anything now due to constraints. Retry scheduling after 5 seconds.


