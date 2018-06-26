/* Read input from STDIN. Print your output to STDOUT*/
#include<iostream.h>

int main(int argc, char *a[])
{
	int N,C;
	cin >> N >> C;
	int tx[N],ty[N],tm[N],ti[N];
	vector<int> g[N];
	for(int i = 0 i < N;i++){
cin >> tx[i] >> ty[i] >> tm[i] >> ti[i];
	}
	for(int i = 0 i < N;i++){
	    for(int j = 0 ; j < N ;j++){
	        if(j != i){
	            int ed = ((tx[j]-tx[i])*2) + ((ty[j]-ty[i])*2);
	            if(ed <= C){
	                g[i].push_back(j);
	            }
	        }
	    }
	}
	for(int 
}

