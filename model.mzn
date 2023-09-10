var 1..9: x;
var 1..9: y;
constraint pow(abs(x), 2) / y = 2;
constraint y > 1;
constraint x > y;
solve satisfy;
