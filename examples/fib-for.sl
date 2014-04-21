var fib = func(x) {
    var prev = 0
    var cur = 1
    if x <= 0 {
        cur = 0
    } else {
        for var i = 1; i < x; i = i + 1 {
            var next = prev + cur
            prev = cur
            cur = next
        }
    }
    return cur
}
print fib(10)

