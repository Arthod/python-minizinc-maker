include "among.mzn";
var 1..99999999: x;
var 1..99999999: y;
constraint x * y = 54074903;
constraint among(1, [x, y], {6907});
constraint y > 1;
constraint x > y;
solve satisfy;
