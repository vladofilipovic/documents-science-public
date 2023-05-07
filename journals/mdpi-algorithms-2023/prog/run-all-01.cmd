REM python ./src/use_libraries/anytree/main.py
REM python ./src/use_libraries/bitstring/main.py
REM python ./src/use_libraries/deap/main_one_max_bin.py
REM python ./src/ea_node/main_compact_horizontal.py
REM python ./src/ea_node/main_compact_vertical.py
REM python ./src/ea_node/main_is_equal.py
REM python ./src/ea_node/main_random_init.py
REM python ./src/ea_node/main_rearrange_by_label.py
REM python ./src/ea_node/main_rearrange.py
REM python ./src/genetic_programming_ea_node/main_random_init.py
REM python ./src/genetic_programming_ea_node/main_01.py
REM python ./src/genetic_programming_ea_node/main_02.py
REM python ./src/genetic_programming_ea_node/main_03.py
REM python ./src/genetic_programming_dollo_k/main_random_init.py
REM python ./src/genetic_programming_dollo_k/main_gp_infer.py
REM python ./src/genetic_programming_dollo_k/main_gp_direct.py InputFile=inputs/example_01.txt InputFormat=in RandomSeed=7334885245554769134 PopulationSize=50 MaxNumberGenerations=20 --debug
REM python ./src/genetic_programming_dollo_k/main_gp_direct.py InputFile=inputs/example_02.txt InputFormat=in RandomSeed=0 PopulationSize=50 MaxNumberGenerations=20 --debug
REM
set loop=0
:loop
python ./src/genetic_programming_dollo_k/main_gp.py  EvaluationType=likelihood-012 InputFile=inputs/example_01.txt MaxFillFactor=6 InputFormat=012 RandomSeed=0 PopulationSize=200 MaxTimeForExecutionInSeconds=300 MaxNumberGenerations=0
python ./src/genetic_programming_dollo_k/main_gp.py  EvaluationType=likelihood-012 InputFile=inputs/example_02.txt MaxFillFactor=6 InputFormat=012 RandomSeed=0 PopulationSize=200 MaxTimeForExecutionInSeconds=300 MaxNumberGenerations=0
python ./src/genetic_programming_dollo_k/main_gp.py  EvaluationType=likelihood-012 InputFile=inputs/example_03.txt MaxFillFactor=6 InputFormat=012 RandomSeed=0 PopulationSize=200 MaxTimeForExecutionInSeconds=1500 MaxNumberGenerations=0
python ./src/genetic_programming_dollo_k/main_gp.py  EvaluationType=likelihood-012 InputFile=inputs/example_04.txt MaxFillFactor=6 InputFormat=012 RandomSeed=0 PopulationSize=200 MaxTimeForExecutionInSeconds=1500 MaxNumberGenerations=0
python ./src/vns_dollo_k/main_vns.py  EvaluationType=likelihood-012 InputFile=inputs/example_01.txt MaxFillFactor=6 InputFormat=012 RandomSeed=0 MaxTimeForExecutionInSeconds=300 MaxNumberIterations=0
python ./src/vns_dollo_k/main_vns.py  EvaluationType=likelihood-012 InputFile=inputs/example_02.txt MaxFillFactor=6 InputFormat=012 RandomSeed=0 MaxTimeForExecutionInSeconds=300 MaxNumberIterations=0
python ./src/vns_dollo_k/main_vns.py  EvaluationType=likelihood-012 InputFile=inputs/example_03.txt MaxFillFactor=6 InputFormat=012 RandomSeed=0 MaxTimeForExecutionInSeconds=1500 MaxNumberIterations=0
python ./src/vns_dollo_k/main_vns.py  EvaluationType=likelihood-012 InputFile=inputs/example_04.txt MaxFillFactor=6 InputFormat=012 RandomSeed=0 MaxTimeForExecutionInSeconds=1500 MaxNumberIterations=0
set /a loop=%loop%+1 
if "%loop%"=="3" goto next
goto loop
:next