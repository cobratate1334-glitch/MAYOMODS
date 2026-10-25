/* Read-only Unity-thread bridge. JNI table slots follow Oracle JNI 17 spec.
 * Never mutates base saves, cash, paid entitlements, game collections or RNG. */
#include <stdint.h>
#include <stddef.h>
extern void *dlopen(const char *,int);
extern void *dlsym(void *,const char *);
extern int mprotect(void *,size_t,int);
extern int pthread_mutex_lock(void *);
extern int pthread_mutex_unlock(void *);
static unsigned char mutex[64] __attribute__((aligned(8)));
static void *handle;
static uintptr_t base;
static int installed;
#define EXPORT __attribute__((visibility("default")))
#define SLOT_VA 0x6344000UL
#define TRAMP_VA 0x6340480UL
static void *(*domain_get)(void);
static void **(*assemblies)(void *,size_t *);
static void *(*image_get)(void *);
static const char *(*image_name)(void *);
static void *(*class_from)(void *,const char *,const char *);
static void *(*field_from)(void *,const char *);
static void (*static_get)(void *,void *);
static void (*field_get)(void *,void *,void *);
static void *(*object_class)(void *);
static void *(*method_from)(void *,const char *,int);
static void *(*invoke)(void *,void *,void **,void **);
static void *(*unbox)(void *);
static int (*string_length)(void *);
static uint16_t *(*string_chars)(void *);
static void *game_class,*instance_field,*life_field;
static uint16_t snapshot[1024]; static int snapshot_len;
static unsigned frame;
static int eq(const char*a,const char*b){while(*a&&*a==*b){a++;b++;}return *a==*b;}
static void *call(void*obj,const char*name){if(!obj)return 0;void*k=object_class(obj),*m=method_from(k,name,0),*e=0;void*r=m?invoke(m,obj,0,&e):0;return e?0:r;}
static void *get(void*obj,const char*name){void*v=0;if(obj){void*f=field_from(object_class(obj),name);if(f)field_get(obj,f,&v);}return v;}
static int num(void*obj,const char*name,int d){void*v=call(obj,name);return v?*(int*)unbox(v):d;}
static int boolean(void*obj,const char*name){void*v=call(obj,name);return v?*(unsigned char*)unbox(v):0;}
static void add(uint16_t*out,int*p,uint16_t c){if(*p<1023)out[(*p)++]=c;}
static void ascii(uint16_t*out,int*p,const char*s){while(*s)add(out,p,(unsigned char)*s++);}
static void number(uint16_t*out,int*p,long long v){char b[32];int n=0;if(v<0){add(out,p,'-');v=-v;}do{b[n++]=(char)('0'+v%10);v/=10;}while(v&&n<31);while(n)add(out,p,b[--n]);}
static int text(uint16_t*out,int*p,void*s){if(!s)return 0;/* Must be a real System.String, not an integer ID. */

 int n=string_length(s);if(n<1||n>256)return 0;uint16_t*c=string_chars(s);for(int i=0;i<n;i++)add(out,p,c[i]=='\t'||c[i]=='\n'||c[i]=='\r'?' ':c[i]);return n;}
static void *string_class;
static int safe_text(uint16_t*out,int*p,void*s){return s&&object_class(s)==string_class?text(out,p,s):0;}
static int setup(void){size_t n=0;void*d=domain_get();if(!d)return 0;void**a=assemblies(d,&n);for(size_t i=0;i<n;i++){
 void*im=image_get(a[i]);if(eq(image_name(im),"Assembly-CSharp.dll"))game_class=class_from(im,"","GameManager");
 void*sc=class_from(im,"System","String");if(sc)string_class=sc;
 }if(!game_class||!string_class)return 0;instance_field=field_from(game_class,"Inst");life_field=field_from(game_class,"Life");return instance_field&&life_field;}
static void capture(void){if(!game_class&&!setup())return;void*gm=0,*life=0;static_get(instance_field,&gm);if(gm)field_get(gm,life_field,&life);uint16_t s[1024];int p=0;
 void*hero=call(life,"get_Hero");void*id=call(life,"get_MetaHeroID");if(!hero||!id||!safe_text(s,&p,id)){pthread_mutex_lock(mutex);snapshot_len=0;pthread_mutex_unlock(mutex);return;}
 add(s,&p,'\t');number(s,&p,num(hero,"get_Age",-1));add(s,&p,'\t');
 int flags=boolean(hero,"CurrentlyInSchool")|boolean(hero,"CurrentlyHasAJob")*2|boolean(hero,"CurrentlyInPrison")*4|boolean(hero,"get_Alive")*8;
 number(s,&p,flags);add(s,&p,'\t');void*fin=call(life,"get_Finances");void*b=call(fin,"get_BankBalance");double money=b?*(double*)unbox(b):0;
 /* Snapshot money is informational; expansion credits are a separate ledger. */
 if(money>9000000000000000.0)money=9000000000000000.0;if(money< -9000000000000000.0)money= -9000000000000000.0;
 number(s,&p,(long long)money);add(s,&p,'\t');safe_text(s,&p,call(hero,"FullName"));add(s,&p,'\t');safe_text(s,&p,call(hero,"CareerName"));
 pthread_mutex_lock(mutex);for(int i=0;i<p;i++)snapshot[i]=s[i];snapshot_len=p;pthread_mutex_unlock(mutex);
}
static void frame_hook(void*self,void*method){((void(*)(void*,void*))(base+TRAMP_VA))(self,method);if(++frame%30==0)capture();}
#define SYM(var,name) do{*(void**)(&var)=dlsym(handle,name);if(!var)return 0;}while(0)
EXPORT int Java_com_chance_bitlifediag_ExpansionBridge_connect(void*env,void*cls){(void)env;(void)cls;if(installed)return 1;
 handle=dlopen("libil2cpp.so",6);if(!handle)return 0;
 SYM(domain_get,"il2cpp_domain_get");SYM(assemblies,"il2cpp_domain_get_assemblies");SYM(image_get,"il2cpp_assembly_get_image");SYM(image_name,"il2cpp_image_get_name");SYM(class_from,"il2cpp_class_from_name");SYM(field_from,"il2cpp_class_get_field_from_name");SYM(static_get,"il2cpp_field_static_get_value");SYM(field_get,"il2cpp_field_get_value");SYM(object_class,"il2cpp_object_get_class");SYM(method_from,"il2cpp_class_get_method_from_name");SYM(invoke,"il2cpp_runtime_invoke");SYM(unbox,"il2cpp_object_unbox");SYM(string_length,"il2cpp_string_length");SYM(string_chars,"il2cpp_string_chars");
 /* Stable export RVA verified against exact baseline. No /proc guessing. */
 base=(uintptr_t)domain_get-0x223e48cUL;
 uint64_t*slot=(uint64_t*)(base+SLOT_VA);if(slot[1]!=0x4348414e434534UL)return 0;if(*slot!=0&&*slot!=(uintptr_t)frame_hook)return 0;
 __atomic_store_n(slot,(uintptr_t)frame_hook,__ATOMIC_RELEASE);/* Data page separate from RX trampoline. */
 installed=1;return 1;
}
EXPORT void *Java_com_chance_bitlifediag_ExpansionBridge_snapshot(void*env,void*cls){(void)cls;uint16_t out[1024];int n;
 pthread_mutex_lock(mutex);n=snapshot_len;for(int i=0;i<n;i++)out[i]=snapshot[i];pthread_mutex_unlock(mutex);
 void**table=*(void***)env;return ((void*(*)(void*,const uint16_t*,int))table[163])(env,out,n);
}
