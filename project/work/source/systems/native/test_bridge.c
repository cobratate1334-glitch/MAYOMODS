/* Host-side API doubles exercise only read-only capture; no phone claim. */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "bridge.c"
static int dummyClass, stringClass,gm,life,hero,fin,box,ageValue=32;
static double balance=12345.0;
static struct {int n;uint16_t chars[64];} idText={6,{'h','e','r','o','-','1'}},nameText={4,{'A','l','e','x'}},jobText={8,{'P','r','o','d','u','c','e','r'}};
static int noHero,throws;
static void*klass(void*o){return o==&idText||o==&nameText||o==&jobText?&stringClass:&dummyClass;}
static void*meth(void*k,const char*n,int count){return(void*)n;}
static void*flookup(void*k,const char*n){return(void*)n;}
static void stat(void*f,void*out){*(void**)out=&gm;}
static void fld(void*o,void*f,void*out){*(void**)out=eq(f,"Life")?&life:0;}
static void*boxed(void*v){return v;}
static int length(void*s){return *(int*)s;}
static uint16_t*chars(void*s){return(uint16_t*)((char*)s+4);}
static unsigned char yes=1;
static void*runtime(void*m,void*o,void**args,void**e){if(throws){*e=&box;return &box;}
 if(eq(m,"get_Hero"))return noHero?0:&hero;if(eq(m,"get_MetaHeroID"))return &idText;
 if(eq(m,"get_Finances"))return &fin;if(eq(m,"get_Age"))return &ageValue;
 if(eq(m,"get_BankBalance"))return &balance;if(eq(m,"FullName"))return &nameText;if(eq(m,"CareerName"))return &jobText;
 if(eq(m,"CurrentlyInSchool")||eq(m,"CurrentlyHasAJob")||eq(m,"get_Alive"))return &yes;return 0;}
int main(void){game_class=&dummyClass;string_class=&stringClass;instance_field="Inst";life_field="Life";
 object_class=klass;method_from=meth;field_from=flookup;static_get=stat;field_get=fld;invoke=runtime;unbox=boxed;string_length=length;string_chars=chars;
 capture();char s[1024];for(int i=0;i<snapshot_len;i++)s[i]=(char)snapshot[i];s[snapshot_len]=0;
 if(strcmp(s,"hero-1\t32\t11\t12345\tAlex\tProducer"))return 1;
 nameText.chars[0]=0x0391;capture();int found=0;for(int i=0;i<snapshot_len;i++)if(snapshot[i]==0x0391)found=1;if(!found)return 5;nameText.chars[0]='A';
 noHero=1;capture();if(snapshot_len!=0)return 2;noHero=0;throws=1;capture();if(snapshot_len!=0)return 3;
 throws=0;balance=-99;capture();if(snapshot_len<10)return 4;
 printf("Read-only bridge capture passed: identity, age, school/job/alive flags, balance, Unicode string path, absent hero, managed exception, negative balance.\n");return 0;}
