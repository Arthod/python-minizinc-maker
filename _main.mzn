var 0..5: q_0_0_0;
var 0..5: q_1_0_0;
constraint (abs((q_0_0_0 == 5)) + (q_0_0_0 == 3) >= 1);
solve satisfy;
