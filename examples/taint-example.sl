var taint_source = func() {
    return 0
}

var add = func(a, b, c) {
    return a + b + c
}

var fac = func(x) {
    var r = 1
    if x > 1 {
        for var i = 2; i <= x; i = i + 1 {
            r = r * i
        }
    }
    return r
}

var control = 7
var tofac = 7
if control > 8 {
    tofac = add(0-7, taint_source(), 9)
} else {
    tofac = 7
}
print fac(tofac)

