/*
  cc ibcfuncts.c -lpbc -lgmp -lcrytpo
  '-lcrypto' used for SHA1
  ./a.out pairing
*/

#include<stdio.h>
#include<pbc/pbc.h>
#include<pbc/pbc_test.h>
#include<openssl/sha.h>
#include<string.h>

char ident[100], param[1024];
int nm, dm;
char hash[20];
unsigned char hid[130], h4bl[20];
element_t h, g, share, pks, pk ,pk_temp;

element_t h1, h2gt, h3zr;
int sys_n = 0, sys_t = 0, sys_f = 0, ct = 0, q;
pairing_t pairing;

void hash1(char * b){
  /* Mathematically
   * H1 : {0,1}* -> G2*
   * This function will take an input as char, hash it and
   * convert it into a element h1 in G2.
   */
  unsigned char h[20];
  SHA1(b, sizeof(b), h);
  element_from_hash(h1, h, 20);
}

void hash2(unsigned char *b){
  /* Mathematically,
   * H2 : GT -> {0,1}^l, l = 20
   * This function will take a GT value stored in an element h2gt
   * and store a 20 byte hash in the unsigned char b
   */
  unsigned char temp[128];
  element_to_bytes(temp, h2gt);
  SHA1(temp, sizeof(temp), b);
}

void hash3(unsigned char * b1, unsigned char * b2){
  /* Mathematically,
   * H3 : {0,1}^l X {0,1}^l -> Zp
   * This function will take two binary strings and generate an element
   * of Zr and store it in h3zr
   */
  int i;
  unsigned char rnd[20];
  for(i=0; i<20; i++){
    rnd[i] = b1[i] ^ b2[i];
  }
  element_from_bytes(h3zr, rnd);
}

void hash4(unsigned char * b){
  /* Mathematically,
   * H4 : {0,1}^l -> {0,1}^l
   * This function will take a 20 byte string, and return its hash in a 
   * global variable h4bl.
   */
  SHA1(b, sizeof(b), h4bl);
}

void init_hashes(){
  element_init_G2(h1, pairing);
  element_init_GT(h2gt, pairing);
  element_init_Zr(h3zr, pairing);
}

void encrypt20(unsigned char * message){
  unsigned char u[128], v[20], w[20];
  unsigned char sig[20], r[20];
  
  element_random(h2gt);
  hash2(sig);  //sig now has a random number 
  
  
  
}

int init_pairing(int n, int t, int f){
  /*This function will open the pairing file and initialize the pairing.*/
  FILE *fp;
  int k, lk;
  sys_n = n;
  sys_t = t;
  sys_f = f;
  q = 2 * sys_t + 1;
  fp = fopen("../files/pairing", "r");
  size_t count = fread(param, 1, 1024, fp);
  fclose(fp);
  if(!count){
    pbc_die("input error\n");
    return -1;
  }
  pairing_init_set_buf(pairing, param, count);
  printf("Initialized pairing in ibc.c\n");
  element_init_G2(h1, pairing);
  return 0;
}

int read_share(){
  /*This function will open secrets and read the binary data into unsigned char
  and store it in element share*/
  FILE *fp;
  unsigned char str[20];
  fp = fopen("../files/secrets","rb");
  if(!fp)
    return -1;
  printf("About to read from secrets\n");
  size_t count = fread(str, 20, 1, fp);
  fclose(fp);
  if(!count)
    printf("Could not read from secrets\n");
  element_init_Zr(share, pairing);
  element_from_bytes(share, str);
}

void hash_id_s(char *str){
  /*This function will read the string, hash it and then map to an element in G2.
  It will then compute hash^share*/
  SHA1(str, strlen(str), hash);
  hash1(hash);
  element_pow_zn(pks, h1, share);
  element_to_bytes(hid, pks);
}

void gen_privatekey(unsigned char *str, int nodeID, int senderID){
  /*This will compute the private key from all the IBC_REPLY's received
  */
  int i, j;
  float l;
  if(ct > sys_t){
    printf("Done\n");
    element_printf("The key is %B\n", pk);
    return;
  }
  else if(ct <= sys_t)
    ct++;
  printf("Value of sys_t and ct is %d and %d\n", sys_t, ct);
  i = nodeID;
  j = senderID;
  lambdal(i, q);
  element_t b, c, ci, keyshare;
  
  element_init_G2(keyshare, pairing);
  element_init_G2(pk_temp, pairing);
  element_init_G2(pk, pairing);
  element_init_Zr(b, pairing);
  element_init_Zr(c, pairing);
  element_init_Zr(ci, pairing);

  element_set_si(b, nm);
  element_set_si(c, dm);
  printf("nm is %d\ndm is %d\n", nm, dm);
  element_from_bytes(keyshare, str);
  element_pow_zn(pk_temp, keyshare, b);
  element_invert(ci, c);
  element_pow_zn(pk_temp, pk_temp, ci);
  element_mul(pk, pk, pk_temp);
}

int lambdal(int i, int ei){
  /*
  */
  int j;
  nm = 1;
  dm = 1;
  for(j = 1; j <= ei; j++){
    if(j==i)
      continue;
    nm *= j;
    dm *= j - i;
  }
  return 1;
}

int main(){
  char asd[20];
  int d;
  //unsigned char key[100];
  printf("Please enter a hex string to hash using H1 : ");
  gets(asd);
  init_pairing(5, 1, 0);
  init_hashes();
  hash1(asd);
  element_printf("The H1 of %d the string is : %B\n", element_length_in_bytes(h1), h1);

    
  unsigned char qwe[20];
  
  element_random(h2gt);
  hash2(qwe);
  element_printf("\n\nThe H2 of\n%B is\n%s\n", h2gt, qwe);
  
  hash3(qwe, asd);
  element_printf("\n\nThe H3 of \n%s\nand\n%s\nis\n%B\n", qwe, asd, h3zr);

  hash3(qwe, asd);
  element_printf("\n\nThe H3 of \n%s\nand\n%s\nis\n%B\n", qwe, asd, h3zr);

  hash4(qwe);
  printf("The hash of\n%s\nis\n\t%s\n", qwe, h4bl);
  
  hash4(qwe);
  printf("The hash of\n%s\nis\n\t%s\n", qwe, h4bl);
  return 0;
}