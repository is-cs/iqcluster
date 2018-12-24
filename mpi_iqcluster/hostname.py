import socket
hostname = socket.gethostname()
print hostname


with open('/home/iqadmin/meteor_projects/mpi_iqcluster/logs/' + hostname + '.txt', 'w') as f:
  f.write('I am running on ' + hostname)


