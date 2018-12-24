#include <mpi.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>



int main(int argc, char** argv) {
    int i;
    // Initialize the MPI environment
    MPI_Init(NULL, NULL);

    // Get the number of processes
    int world_size;
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);

    // Get the rank of the process
    int world_rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);

    // Get the name of the processor
    char processor_name[MPI_MAX_PROCESSOR_NAME];
    int name_len;
    MPI_Get_processor_name(processor_name, &name_len);

    for(i=0;i<10;i++) {
    MPI_Barrier(MPI_COMM_WORLD);
    //usleep(1000000);
    // Print off a hello world message
    printf("Hello world from processor %s, rank %d out of %d processors, ts = %d\n",
           processor_name, world_rank, world_size, i);
    }

    // Finalize the MPI environment.
    MPI_Finalize();
}
