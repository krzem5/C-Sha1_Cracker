#ifndef __GENERATED_H__
#define __GENERATED_H__ 1
#include <cpu_cracker.h>
#include <stdint.h>



#define _CHECK_HASH_CONCAT(l) _chk_ ## l
#define CHECK_HASH(l,...) _CHECK_HASH_CONCAT(l)(__VA_ARGS__)



void setup_hash(uint32_t h0,uint32_t h1,uint32_t h2,uint32_t h3,uint32_t h4);



uint8_t _chk_1(uint32_t o0);



uint8_t _chk_2(uint32_t o0);



uint8_t _chk_3(uint32_t o0);



uint8_t _chk_4(uint32_t o0);



#endif