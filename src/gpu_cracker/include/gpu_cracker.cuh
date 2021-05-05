#ifndef __GPU_CRACKER_H__
#define __GPU_CRACKER_H__ 1
#include <immintrin.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#pragma intrinsic(_lrotl)



#ifndef NDEBUG
#define _str2(x) #x
#define _str(x) _str2(x)
#define CUDA_CALL(f) \
	do { \
		cudaError_t __e=f; \
		if (__e!=cudaSuccess){ \
			printf("%s: Line %i (%s): %s\n",__FILE__,__LINE__,__func__,cudaGetErrorString(__e)); \
			raise(SIGABRT); \
		} \
	} while (0)
#define CUDA_GPU_CALL(f,n,sz,...) \
	do { \
		(f)<<<(n),(sz)>>>(__VA_ARGS__); \
		cudaError_t __e=cudaGetLastError(); \
		if (__e!=cudaSuccess){ \
			printf("%s: Line %i (%s): %s<<<%lu,%lu>>>(...): %s\n",__FILE__,__LINE__,__func__,_str(f),n,sz,cudaGetErrorString(__e)); \
			raise(SIGABRT); \
		} \
		__e=cudaThreadSynchronize(); \
		if (__e!=cudaSuccess){ \
			printf("%s: Line %i (%s): %s<<<%lu,%lu>>>(...): %s\n",__FILE__,__LINE__,__func__,_str(f),n,sz,cudaGetErrorString(__e)); \
			raise(SIGABRT); \
		} \
	} while (0)
#else
#define CUDA_CALL(f) (f)
#define CUDA_GPU_CALL(f,n,sz,...) (f)<<<(n),(sz)>>>(__VA_ARGS__)
#endif
#define DEVICE_ID 0
#define BIT_ROT_FUNC_SETUP(a,b) _lrotl(a,b)
#define BIT_ROT_FUNC_CHECK(a,b) (((a)<<(b))|((a)>>(32-(b))))
#define LOCK() \
	do{ \
		__syncthreads(); \
		if (!threadIdx.x){ \
			while (atomicCAS((int*)(&lck),0,1)); \
		} \
		__syncthreads(); \
	} while (0)
#define UNLOCK() \
	do{ \
		__threadfence(); \
		__syncthreads(); \
		lck=0; \
		__threadfence(); \
		__syncthreads(); \
	} while (0)



typedef struct __SHA1{
	uint32_t h[5];
	uint8_t l;
} sha1_t;



typedef struct __SHA1_SOLUTION{
	uint8_t l;
	uint8_t c;
	uint8_t bf[2048];
} sha1_solution_t;



__device__ volatile int lck=0;



#endif
