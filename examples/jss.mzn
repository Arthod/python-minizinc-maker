enum JOB = anon_enum(5);
enum TASK = anon_enum(5);
TASK: last = max(TASK); %
array [JOB,TASK] of int: d = [| 1, 4, 5, 3, 6| 3, 2, 7, 1, 2| 4, 4, 4, 4, 4| 1, 1, 1, 6, 8| 7, 3, 2, 2, 1 |]; %
int: total = sum(i in JOB, j in TASK)(d[i,j]);%
int: digs = ceil(log(10.0,int2float(total))); %
array [JOB,TASK] of var 0..total: s;
var 0..total: end;
constraint %% ensure the tasks occur in sequence
forall(i in JOB) (
forall(j in TASK where j < last)
(s[i,j] + d[i,j] <= s[i,enum_next(TASK,j)]) /\
s[i,last] + d[i,last] <= end
);
constraint %% ensure no overlap of tasks
forall(j in TASK) (
forall(i,k in JOB where i < k) (
s[i,j] + d[i,j] <= s[k,j] \/
s[k,j] + d[k,j] <= s[i,j]
)
);