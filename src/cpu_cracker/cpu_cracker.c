#include <cpu_cracker.h>
#include <generated.h>
#include <immintrin.h>
#include <intrin.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <windows.h>
#pragma intrinsic(_lrotl)



#define THREAD_DEPTH 3



LARGE_INTEGER tm_s;
LARGE_INTEGER tm_f;
HANDLE mx;
volatile uint32_t tc;
uint32_t sc=0;



DWORD _solve_single_thr(LPVOID lp){
	printf("Starting Thread: %u\n",*((uint32_t*)lp));
	uint32_t o0=*((uint32_t*)lp);
	for (uint32_t i=0;i<(1u<<(32-THREAD_DEPTH));i++){
		if (CHECK_HASH(4,(i<<THREAD_DEPTH)|o0)){
			LARGE_INTEGER e;
			QueryPerformanceCounter(&e);
			uint32_t v=(i<<THREAD_DEPTH)|o0;
			printf("Solution Found: %#.8x (%.6fs) => '%c%c%c%c'\n",v,(e.QuadPart-tm_s.QuadPart)*1e6/tm_f.QuadPart*1e-6,v>>24,(v>>16)&0xff,(v>>8)&0xff,v&0xff);
			if (WaitForSingleObject(mx,INFINITE)!=WAIT_OBJECT_0){
				printf("Unknown WaitForSingleObject Value!\n");
			}
			else{
				sc++;
				ReleaseMutex(mx);
			}
		}
	}
	printf("End Thread: %u\n",*((uint32_t*)lp));
	if (WaitForSingleObject(mx,INFINITE)!=WAIT_OBJECT_0){
		printf("Unknown WaitForSingleObject Value!\n");
	}
	else{
		tc--;
		ReleaseMutex(mx);
	}
	return 0;
}



int main(void){
	setup_hash(0x640ab2ba,0xe07bedc4,0xc163f679,0xa746f7ab,0x7fb5d1fa);
	SetPriorityClass(GetCurrentProcess(),ABOVE_NORMAL_PRIORITY_CLASS);
	uint32_t* t_dt=malloc(((1<<THREAD_DEPTH)-1)*sizeof(uint32_t));
	tc=(1u<<THREAD_DEPTH);
	mx=CreateMutexW(NULL,FALSE,NULL);
	QueryPerformanceFrequency(&tm_f);
	QueryPerformanceCounter(&tm_s);
	for (uint32_t i=1;i<(1u<<THREAD_DEPTH);i++){
		*(t_dt+i)=i;
		SetThreadPriority(CreateThread(NULL,0,_solve_single_thr,t_dt+i,0,NULL),THREAD_PRIORITY_ABOVE_NORMAL);
	}
	SetThreadPriority(GetCurrentThread(),THREAD_PRIORITY_ABOVE_NORMAL);
	uint32_t dt=0;
	_solve_single_thr(&dt);
	while (tc);
	LARGE_INTEGER e;
	QueryPerformanceCounter(&e);
	free(t_dt);
	CloseHandle(mx);
	printf("Complete: %u Solution(s) (%.6fs)\n",sc,(e.QuadPart-tm_s.QuadPart)*1e6/tm_f.QuadPart*1e-6);
}
