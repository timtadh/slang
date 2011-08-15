# Find the max of a pre-entered list.
# copied/inspired by Page 31 (bottom) from
#   Programming from the Ground Up.

.section .data

data_items:
 .long 3,67,34,15,45,75,54,34,44,33,22,11,66,0

.section .text

.global _start
_start:
  
  movl $0, %edi                       # move 0 into %edi (index)
  movl data_items(,%edi,4), %eax      # move &data_items + 0*4 --> %eax
  movl %eax, %ebx                     # cp eax --> %ebx (ebx holds max)

  start_loop:
    cmpl $0, %eax                     # compare 0 to %eax, result stored in
                                      # %eflags
    je   loop_exit                    # jump to loop_exit if 0 == %eax
    incl %edi                         # increment %edi (index)
    movl data_items(, %edi, 4), %eax  # move &data_items + %edi*4 --> %eax
    cmpl %ebx, %eax                   # compare max to cur
    jle  start_loop                   # jump to start_loop if max <= cur
    movl %eax, %ebx                   # else: mov cur to max
    jmp  start_loop

  loop_exit:
    # %ebx is the is the argument which holds the exit status code for the 
    # exit system call no need, so the max value is already in the right
    # place.
    movl $1, %eax                     # 1 is the exit system call number
    int  $0x80                        # interupt 0x80, make a system call

