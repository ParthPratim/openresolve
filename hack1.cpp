#include <bits/stdc++.h>

using namespace std;

int main()
{
int T;
cin >> T;
for(int i = 0 ; i < T ;i++)
{
int N;
cin >> N;
vector<int> A;
for(int j = 0 ; j < N ;j++)
{
int tmp;
cin >> tmp;
A.push_back(tmp);
}
sort(A.begin(),A.end());
int maxm = 0 , h = N-1 , l = 0;
while(l<=h)
{

int count = 1;
while(count * A[h] < 50)
count++;

if(count <= h-l+1)
maxm++;

l+=count-1;
h--;

}

cout  << "Case #" << (i+1) <<": " << maxm << endl;
}
return 0;
}
