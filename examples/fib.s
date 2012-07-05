.section .data
printf_msg:
  .ascii "%d\n\0"
push_msg:
  .ascii "push 0x%x\n\0"
pop1_msg:
  .ascii "pop1 0x%x\n\0"
pop2_msg:
  .ascii "pop2 0x%x\n\0"
display:
  .long 0, 0

.section .text
.global _start
_start:
  movl   %esp,      %ebp      
  movl   %ebp,      0(%ebp)   
main:
  subl   $0x24,     %esp      
b1:
  movl   $0xa,      -36(%ebp) 
  movl   -36(%ebp), %eax      
  movl   %eax,      -8(%esp)  
  call   f2        
  movl   -8(%esp),  %eax      
  movl   %eax,      -32(%ebp) 
  pushl  -32(%ebp) 
  pushl  $printf_msg
  call   printf    
  addl   $0x8,      %esp      
  push   $0        
  call   exit      
f2:
  movl   %ebp,      -8(%esp)  
  movl   %esp,      %ebp      
  movl   %ebx,      -12(%ebp) 
  movl   %edi,      -16(%ebp) 
  movl   %esi,      -20(%ebp) 
  movl   %ecx,      -24(%ebp) 
  movl   %edx,      -28(%ebp) 
  movl   $0x4,      %ebx      
  movl   display(%ebx), %eax      
  movl   %eax,      -32(%ebp) 
  movl   $0x4,      %ebx      
  movl   %ebp,      display(%ebx)

  subl   $0x5c,     %esp      
b2:
  movl   -4(%ebp),  %eax      
  movl   %eax,      -92(%ebp) 
  movl   $0x1,      -36(%ebp) 
  movl   -92(%ebp), %eax      
  cmpl   -36(%ebp), %eax      
  jg     b3        
  jmp    b5        
b3:
  nop    
  movl   $0x1,      -88(%ebp) 
  movl   -92(%ebp), %eax      
  subl   -88(%ebp), %eax      
  movl   %eax,      -56(%ebp) 
  movl   -56(%ebp), %eax      
  movl   %eax,      -8(%esp)  
  call   f2        
  movl   -8(%esp),  %eax      
  movl   %eax,      -84(%ebp) 
  movl   $0x2,      -52(%ebp) 
  movl   -92(%ebp), %eax      
  subl   -52(%ebp), %eax      
  movl   %eax,      -68(%ebp) 
  movl   -68(%ebp), %eax      
  movl   %eax,      -8(%esp)  
  call   f2        
  movl   -8(%esp),  %eax      
  movl   %eax,      -40(%ebp) 
  movl   -84(%ebp), %eax      
  addl   -40(%ebp), %eax      
  movl   %eax,      -64(%ebp) 
  jmp    b4        
b5:
  nop    
  movl   $0x1,      -80(%ebp) 
  movl   -92(%ebp), %eax      
  cmpl   -80(%ebp), %eax      
  je     b6        
  jmp    b8        
b6:
  nop    
  movl   $0x1,      -64(%ebp) 
  jmp    b7        
b7:
  nop    
  jmp    b4        
b8:
  nop    
  movl   $0x0,      -64(%ebp) 
  jmp    b7        
b4:
  nop    

  movl   $0x4,      %ebx      
  movl   -32(%ebp), %eax      
  movl   %eax,      display(%ebx)
  movl   -28(%ebp), %edx      
  movl   -24(%ebp), %ecx      
  movl   -20(%ebp), %esi      
  movl   -16(%ebp), %edi      
  movl   -12(%ebp), %ebx      
  movl   %ebp,      %esp      
  movl   -8(%esp),  %ebp      
  movl   -64(%esp), %eax      
  movl   %eax,      -4(%esp)  
  addl   $0x4,      %esp      
  jmp    *-4(%esp) 
