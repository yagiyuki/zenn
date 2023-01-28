---
title: "GO言語の公式チュートリアルのExercise回答"
emoji: "💨"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Go"]
published: false
---


## Exercise: Loops and Functions
https://go-tour-jp.appspot.com/flowcontrol/8

```go
package main

import (
	"fmt"
)

func Sqrt(x float64) float64 {
	z := 1.0
	for i := 0; i < 10; i++ {
		z -= (z*z - x) / (2*z)
		// ループごとのzの変化
		//fmt.Println("i=", i, "ret=", z)
	}
	return z
}

func main() {
	fmt.Println(Sqrt(2))
}
```

## Exercise: Slices
https://go-tour-jp.appspot.com/moretypes/18
```go
package main

import "golang.org/x/tour/pic"

func Pic(dx, dy int) [][]uint8 {
    pic := make([][]uint8, dy)
    for y := range pic {
        pic[y] = make([]uint8, dx)
        for x := range pic[y] {
            pic[y][x] = uint8((x+y)/2)
        }
    }
    return pic
}

func main() {
	pic.Show(Pic)
}
```
