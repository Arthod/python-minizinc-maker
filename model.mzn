include "alldifferent.mzn";
var 1..5: q_1;
var 1..5: q_2;
var 1..5: q_3;
var 1..5: q_4;
var 1..5: q_5;
constraint alldifferent([q_1, q_2, q_3, q_4, q_5]);
solve satisfy;
