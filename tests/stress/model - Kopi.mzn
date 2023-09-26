include "decreasing.mzn";

int: n;                    % number of things to pack
array[1..n] of int: stuff; % the value/weight of the things to pack
int: cap;                 % all bins have the same capacity

var 0..n: bins_used;

array[1..n] of var 0..cap: bin_loads;
array[1..n, 1..n] of var bool: bins;

constraint decreasing(bin_loads);
constraint bin_loads[1] > 0;

constraint forall (i in 1..n) (bin_loads[i] == sum([bins[i, j] * stuff[j] | j in 1..n]));
constraint forall (j in 1..n) (1 == sum([bins[i, j] | i in 1..n]));

constraint bins_used == sum([bin_loads[i] > 0 | i in 1..n]);

solve minimize bins_used;

output [show(bins_used)];