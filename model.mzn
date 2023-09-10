var 1..5: X_0;
var 1..5: X_1;
var 1..5: X_2;
var 1..5: X_3;
var 1..5: X_4;
constraint 0 + X_0 + X_1 + X_2 + X_3 + X_4 = 5;
constraint X_0 > X_1;
solve satisfy;
