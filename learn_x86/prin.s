## test printing

.section .data
hello_world:
  .ascii "Hello World! %d \n\0"

number:
  .long 123

.section .text
.global _start
_start:
  pushl number
  pushl $hello_world
  call  printf

  mov   $0, %ebx
  mov   $1, %eax
  int   $0x80

