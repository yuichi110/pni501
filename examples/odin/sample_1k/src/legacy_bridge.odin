package legacy
import "core:fmt"
legacy_cast :: proc(p: rawptr) -> int {
    fmt.println(p)
    return 0
}
