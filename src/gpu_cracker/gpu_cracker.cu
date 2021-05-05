#include <gpu_cracker.cuh>
#include <generated.cuh>
#include <cuda_runtime.h>
#include <curand.h>
#include <curand_kernel.h>
#include <device_launch_parameters.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>



__device__ sha1_solution_t _d_o;



__global__ void _solver_single1(void){
	uint8_t v=blockIdx.x*blockDim.x+threadIdx.x;
	if (CHECK_HASH(1,v)){
		LOCK();
		*(_d_o.bf+_d_o.c*_d_o.l)=v;
		_d_o.c++;
		UNLOCK();
	}
}



__global__ void _solver_single2(void){
	uint16_t v=blockIdx.x*blockDim.x+threadIdx.x;
	if (CHECK_HASH(2,v)){
		LOCK();
		*(_d_o.bf+_d_o.c*_d_o.l)=v>>8;
		*(_d_o.bf+_d_o.c*_d_o.l+1)=v&0xff;
		_d_o.c++;
		UNLOCK();
	}
}



__global__ void _solver_single3(void){
	uint32_t v=blockIdx.x*blockDim.x+threadIdx.x;
	if (CHECK_HASH(3,v)){
		LOCK();
		*(_d_o.bf+_d_o.c*_d_o.l)=v>>16;
		*(_d_o.bf+_d_o.c*_d_o.l+1)=(v>>8)&0xff;
		*(_d_o.bf+_d_o.c*_d_o.l+2)=v&0xff;
		_d_o.c++;
		UNLOCK();
	}
}



__global__ void _solver_single4(void){
	uint32_t v=blockIdx.x*blockDim.x+threadIdx.x;
	if (CHECK_HASH(4,v)){
		LOCK();
		*(_d_o.bf+_d_o.c*_d_o.l)=v>>24;
		*(_d_o.bf+_d_o.c*_d_o.l+1)=(v>>16)&0xff;
		*(_d_o.bf+_d_o.c*_d_o.l+2)=(v>>8)&0xff;
		*(_d_o.bf+_d_o.c*_d_o.l+3)=v&0xff;
		_d_o.c++;
		UNLOCK();
	}
}



void solve_hash(sha1_t sha1,sha1_solution_t* o){
	o->l=sha1.l;
	o->c=0;
	if (!sha1.l){
		return;
	}
	CUDA_CALL(cudaMemcpyToSymbol(_d_o,o,sizeof(sha1_solution_t)));
	if (sha1.l==1){
		SETUP_HASH(1,sha1);
		printf("Starting 256 Threads...\n");
		CUDA_GPU_CALL(_solver_single1,1,256);
		CUDA_CALL(cudaDeviceSynchronize());
	}
	else if (sha1.l==2){
		SETUP_HASH(2,sha1);
		printf("Starting 65536 Threads...\n");
		CUDA_GPU_CALL(_solver_single2,64,1024);
		CUDA_CALL(cudaDeviceSynchronize());
	}
	else if (sha1.l==3){
		SETUP_HASH(3,sha1);
		printf("Starting 16777216 Threads...\n");
		CUDA_GPU_CALL(_solver_single3,16384,1024);
		CUDA_CALL(cudaDeviceSynchronize());
	}
	else if (sha1.l==4){
		SETUP_HASH(4,sha1);
		printf("Starting 4294967296 Threads...\n");
		CUDA_GPU_CALL(_solver_single4,4194304,1024);
		CUDA_CALL(cudaDeviceSynchronize());
	}
	else{
		printf("Unsupported Length!\n");
	}
	CUDA_CALL(cudaMemcpyFromSymbol(o,_d_o,sizeof(sha1_solution_t)));
}



void print_hash(uint32_t h0,uint32_t h1,uint32_t h2,uint32_t h3,uint32_t h4,uint8_t l){
	printf("Hash: %.8x%.8x%.8x%.8x%.8x (Input Length: %u)\n",h0,h1,h2,h3,h4,l);
	sha1_t sha1={{h0,h1,h2,h3,h4},l};
	sha1_solution_t o;
	solve_hash(sha1,&o);
	if (!o.c){
		printf("No Solutions!\n");
	}
	else{
		for (uint16_t i=0;i<(uint16_t)(o.l*o.c);i+=o.l){
			putchar('0');
			putchar('x');
			for (uint16_t j=0;j<o.l;j++){
				if ((o.bf[i+j]>>4)>9){
					putchar(87+(o.bf[i+j]>>4));
				}
				else{
					putchar(48+(o.bf[i+j]>>4));
				}
				if ((o.bf[i+j]&0xf)>9){
					putchar(87+(o.bf[i+j]&0xf));
				}
				else{
					putchar(48+(o.bf[i+j]&0xf));
				}
			}
			printf(" => '");
			for (uint16_t j=0;j<o.l;j++){
				putchar(o.bf[i+j]);
			}
			putchar('\'');
			putchar('\n');
		}
	}
}



int main(void){
	cudaSetDevice(DEVICE_ID);
	cudaDeviceProp p;
	CUDA_CALL(cudaGetDeviceProperties(&p,DEVICE_ID));
	printf("Detected Device: '%s' (total_mem: %.1fGb, multiprocessor_count: %lu, clock_rate: %.1fGHz, hardware_version: %lu.%lu)\n",p.name,p.totalGlobalMem*1e-9,p.multiProcessorCount,p.clockRate*1e-6,p.major,p.minor);
	print_hash(0x6dcd4ce2,0x3d88e2ee,0x9568ba54,0x6c007c63,0xd9131c1b,1);
	print_hash(0x1f43cf7b,0xe94816f2,0xa2c7cc9a,0xc8a65b1a,0x4db8e65d,2);
	print_hash(0x915858af,0xa2278f25,0x527f1920,0x38108346,0x164b47f2,3);
	print_hash(0xc6c42be0,0x07971599,0x963573d1,0xef39aa5f,0x6939b5dd,4);
}
