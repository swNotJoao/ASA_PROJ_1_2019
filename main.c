/*
  ASA - 1º Projeto

  char* aluno1 = "João Lopes"
  int numAluno1 = 90732
  char* aluno2 = "Tomás Gomes"
  int numAluno2 = 90782
*/
#include <stdlib.h>
#include <stdio.h>
#define MIN(a,b) (((a)<(b))?(a):(b))

typedef struct fakeNode{
    int id;
    struct fakeNode *next;
}fakeNode;

typedef struct node{
    int tempo_d;
    int low;
    int pai;
    char p_art;
    struct fakeNode *next;
}node;

node **Graph;
int numeroRouters;
int numeroSubredes = 0;
int *maxSubrede;
int time;
int tamanhoMaiorSRede = 1, treeSize = 0;
int global_nligacoes = 0;
void lerGrafo();
void criaLigacao(int, int);
void addRouter(int);
void addLigacao(int, int);
fakeNode *criaRouter(int);
void DFS();
void visit(int);
void resetVisits();

int main(){
    int i;
    int n = 0;
    lerGrafo();
    DFS();
    printf("%d\n", numeroSubredes);
    for(i = numeroSubredes -1; i >= 0; i--){
      if(i == 0){
        printf("%d", maxSubrede[i]);
      }
      else{
        printf("%d ", maxSubrede[i]);
      }
    }
    printf("\n");
    for(i=0;i<numeroRouters;i++) if(Graph[i]->p_art) n++;
    printf("%d\n", n);

    if(global_nligacoes == 0){
      printf("1\n");
    }
    else{
      resetVisits();
      tamanhoMaiorSRede = 0;
      treeSize = 0;
      DFS();
      printf("%d\n", tamanhoMaiorSRede);
      return 0;
    }
    return 0;
}
void lerGrafo(){
  int i, r1, r2, numeroLigacoes;
	scanf("%d",&numeroRouters);
	Graph = malloc(sizeof(node) * numeroRouters);
  maxSubrede = malloc(sizeof(int) * numeroRouters);
	for(i = 0; i < numeroRouters; i++) addRouter(i+1);
  scanf("%d",&numeroLigacoes);
  global_nligacoes = numeroLigacoes;
	for(i = 0; i < numeroLigacoes; i++){
	scanf("%d %d", &r1, &r2);
	criaLigacao(r1, r2);
	}
}
void addRouter(int id){
	node *r;
	r = (node*)malloc(sizeof(node));
  r->tempo_d = 0;
  r->pai = -1;
  r->p_art = 0;
	r->next = NULL;
	Graph[id-1] = r;
}
void criaLigacao(int r1,int r2){
  fakeNode *r;
  r = Graph[r1-1]->next;
  if(r != NULL){
    while(r->next != NULL) r = r->next;
    r->next = criaRouter(r2);
  }
  else{
    Graph[r1-1]->next = criaRouter(r2);
  }
  r = Graph[r2-1]->next;
  if(r != NULL){
    while(r->next != NULL) r = r->next;
    r->next = criaRouter(r1);
  }
  else{
    Graph[r2-1]->next = criaRouter(r1);
  }
}
fakeNode *criaRouter(int id){
	fakeNode *r = (fakeNode*)malloc(sizeof(fakeNode));
  r->id = id;
  r->next = NULL;
  return r;
}
void DFS(){
	int i;
  node *p;
  time = 1;
  for(i = numeroRouters-1; i >= 0; i--) {
    p = Graph[i];
    if(p->tempo_d == 0){
      visit(i+1);
      treeSize = 0;
      maxSubrede[numeroSubredes] = i+1;
      numeroSubredes++;
    }
  }
}
void visit(int id){
  node *p = Graph[id-1];
  if(p->p_art != 1){
    treeSize++;
    fakeNode *aux = p->next;
    node *filho;
    p->tempo_d = time;
    p->low = time++;
    int filhos = 0;
    while(1){
      if(aux == NULL) break;
      filho = Graph[aux->id-1];
      if(filho->tempo_d == 0){
        filho->pai = id;
        filhos++;
        visit(aux->id);
        p->low = MIN(p->low, filho->low);
        if(p->pai == -1 && filhos > 1) p->p_art = 1;
        if(p->pai != -1 && filho->low >= p->tempo_d) p->p_art = 1;
      }
      else if (p->pai != aux->id) p->low = MIN(p->low, filho->tempo_d);
      aux = aux->next;
    }
    if(treeSize > tamanhoMaiorSRede){
      tamanhoMaiorSRede = treeSize;
    }
  }

}

void resetVisits(){
  int i;
  for(i = 0; i < numeroRouters ; i++) Graph[i]->tempo_d = 0;
}
