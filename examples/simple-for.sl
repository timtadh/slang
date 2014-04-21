var f = func(x) {
    var c = 1
    for var i = 1; i < x; i = i + 1 {
        c = c * (c + i)
    }
    return c
}
print f(5)

