var fib = func(x) {
    var c
    if (x > 1) {
        c = fib(x-1) + fib(x-2)
    } else {
        if (x == 1) {
            c = 1
        } else {
            c = 0
        }
    }
    return c
}
print fib(10)
