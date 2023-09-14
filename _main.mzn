var 0..5: q_0;
var 0..5: q_1;
var 0..5: q_2;
var 0..5: q_3;
var 0..5: q_4;
constraint not((q_2 == (q_0 + 1)));
solve satisfy;
