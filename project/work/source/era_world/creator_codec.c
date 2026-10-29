/* Portable, bounded share format. No script evaluation, files or network calls. */
typedef unsigned short u16;
static int digit(unsigned c) { return c>='0'&&c<='9'?c-'0':c>='A'&&c<='F'?c-'A'+10:c>='a'&&c<='f'?c-'a'+10:-1; }
static int good(const u16 *p,int n,int title) {
 if(n<1||n>(title?80:600))return 0;
 for(int i=0;i<n;i++) {
  unsigned c=p[i];if(!c||c==127||(c<32&&(title||(c!=10&&c!=9))))return 0;
  if(c>=0xd800&&c<=0xdbff){if(++i>=n||p[i]<0xdc00||p[i]>0xdfff)return 0;}
  else if(c>=0xdc00&&c<=0xdfff)return 0;
 }
 return 1;
}
static int validmeta(const int *m){return m[0]>=0&&m[0]<=m[1]&&m[1]<=130&&m[2]>=1&&m[2]<=m[3]&&m[3]<=3999&&m[4]>=0&&m[4]<=4&&m[5]>=0&&m[5]<=4;}
int creator_encode(const u16 **p,const int *length,const int *m,char *out,int capacity) {
 if(capacity<32||!validmeta(m))return 0;
 int n=4;out[0]='M';out[1]='M';out[2]='1';out[3]='|';
 for(int f=0;f<6;f++){
  int k=length[f];if(!good(p[f],k,f==0||f==2||f==4)||n+k*4+2>=capacity)return 0;
  for(int j=0;j<k;j++)for(int shift=12;shift>=0;shift-=4){int v=(p[f][j]>>shift)&15;out[n++]=(char)(v<10?'0'+v:'A'+v-10);}
  out[n++]='|';
 }
 for(int f=0;f<6;f++){
  int v=m[f],div=1000;if(n+6>=capacity)return 0;
  while(div>1&&v<div)div/=10;
  do{out[n++]='0'+v/div;v%=div;div/=10;}while(div);
  if(f<5)out[n++]='|';
 }
 out[n]=0;return n;
}
int creator_decode(const u16 *in,int count,u16 *out,int *length,int *m) {
 if(count<22||count>18000||in[0]!='M'||in[1]!='M'||in[2]!='1'||in[3]!='|')return 0;
 int n=4;
 for(int f=0;f<6;f++){
  int k=0;
  while(n<count&&in[n]!='|'){
   if(k>=600||n+4>count)return 0;unsigned c=0;
   for(int j=0;j<4;j++){int d=digit(in[n++]);if(d<0)return 0;c=(c<<4)|(unsigned)d;}
   out[f*601+k++]=(u16)(c=='<'?0x2039:c=='>'?0x203a:c=='['?0xff3b:c==']'?0xff3d:c);
  }
  if(n>=count||in[n++]!='|'||!good(out+f*601,k,f==0||f==2||f==4))return 0;
  out[f*601+k]=0;length[f]=k;
 }
 for(int f=0;f<6;f++){
  int v=0,k=0;
  while(n<count&&in[n]!='|'){unsigned c=in[n++];if(c<'0'||c>'9'||++k>4)return 0;v=v*10+(int)c-'0';}
  if(!k)return 0;m[f]=v;
  if(f<5){if(n>=count||in[n++]!='|')return 0;}else if(n!=count)return 0;
 }
 return validmeta(m);
}
/* Neutralize rich-text/reference delimiters, while keeping normal Unicode. */
int creator_clean(const u16 *in,int count,u16 *out,int capacity){
 if(count<0||count>=capacity)return -1;
 for(int i=0;i<count;i++){u16 c=in[i];if(!c)return -1;out[i]=c=='<'?0x2039:c=='>'?0x203a:c=='['?0xff3b:c==']'?0xff3d:c;}
 out[count]=0;return count;
}
