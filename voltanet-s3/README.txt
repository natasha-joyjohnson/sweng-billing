VoltaNet · your subsystem · team S3
Software Engineering I · Monday 5 October 2026

What each file is, and where it comes from. The steps are on the slides.

  my_subsystem.py         FROM US, YOU COMPLETE IT IN STEP 1, THEN KEEP IT AS IT IS.
                          The edge of your subsystem: the methods the rest of VoltaNet
                          calls, each answering a fixed value. Each docstring says who
                          calls it and which of YOUR modules will answer it.
  my_subsystem_with_modules.py
                          YOURS, STEP 4: a copy of my_subsystem.py in which each method
                          hands its request to your modules. Run it with
                          python run.py my_subsystem_with_modules.py
                          (python run.py still runs the original).
  interfaces-S3-pairA.txt, interfaces-S3-pairB.txt
                          FROM YOUR CARDS OF 28 SEPTEMBER, EACH PAIR COMPLETES ITS OWN.
                          Each pair's modules and every line of their cards, one block
                          per method.
  prompt-stubs.txt        FROM US. Step 3: the prompt that makes a stub from one module.
  prompt-module.txt       FROM US. Step 5: the prompt that makes a first real version
                          of one module, from its blocks and three criteria.
  modules/                YOURS. One stub file per module, made with the prompt; in step 5
                          the stub of the module you make real is kept as <name>_stub.py.
  run.py                  FROM US. Plays your use case (#12) row by row, calling
                          my_subsystem.py. Do not change it.
  standins.py, scenarios.py
                          FROM US. The other three subsystems, and your use case.
                          Do not change them.

Run: python run.py   (or python3 run.py; Python 3.8 or later, nothing to install)
No Python? Colab: upload all the files, then run   !python run.py

Each pair works in its own copy of this folder. Before handing in, put both pairs'
files together in the folder of the pair with the coordinator: the other pair copies
its interfaces file and its files in modules/ into it.

Hand in: that folder, zipped.
