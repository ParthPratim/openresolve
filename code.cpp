#include <bits/stdc++.h>
using namespace std;
int main(){
int T;
cin >> T;
for(int i = 0 ; i< T;i++){
int D,len,charge=1,shot=0,swaps=0;
string h;
cin >> D >> h;
len = h.length();
for(int i=0;i<len-1;i++){
char p = h.at(i) , p2 = h.at(i+1);
if(p == 'C'){
if(p2 == 'S'){
if(charge*2 > D){
h[i+1] = 'C';
h[i] = 'S';
shot += charge;
swaps++;
}

}
else{
charge = charge * 2;
}

}
else{
shot += charge;
}

}
if(swaps > 0)
cout << swaps << endl;
else
cout << "IMPOSSIBLE" << endl;
}
return 0;
}

