include "all_equal.mzn";
var 0..5: q_0;
var 0..5: q_1;
constraint ((q_0 == (q_1 + 1)) \/ (q_0 >= q_1));
constraint all_equal([q_0, q_1]);
solve satisfy;
