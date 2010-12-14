slang : Simple Language
=======================

Slang is going to be a very simple functional language to be used to teach the
basics of interpretation and complilation.

Intermediate Lanaguage
----------------------
At the moment the only thing implemented is the intermediate language. I wrote
an interpreter for this simple language to allow me to test it easier.

Here is the langauge spec, note all operands go CMD to <- from

    LOAD  to_reg  MEM[from_reg]     # load address in from_reg into to_reg
    SAVE  MEM[to_reg]  from_reg     # save reg into address in to_reg
    IMM   to_reg  CONST[32 bits]    # load constant into the reg
    J     reg                       # jump to address stored in the reg
    PC    reg                       # load pc+2 into the reg
    ADD   a, b                      # regs[a] = regs[a] + regs[b]
    SUB   a, b                      # regs[a] = regs[a] - regs[b]
    MUL   a, b                      # regs[a] = regs[a] * regs[b]
    DIV   a, b                      # regs[a] = regs[a] / regs[b]
    EXIT                            # exit program
    PRIN  reg                       # print register a

language spec to come
