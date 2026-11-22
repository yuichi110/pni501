# Typing, Precision Kinds & Array Interface Standards (Fortran)

## Core Principles
1. **Portable Precision Kinds (`iso_fortran_env` / `iso_c_binding`)**: Declare numeric kinds via `use, intrinsic :: iso_fortran_env, only: real64, int32, int64` (or `selected_real_kind`) instead of non-standard `real*8`, `double precision`, or bare `real` literals without kind suffix (`1.0_real64`; `AstFacts.type_safety_coverage_pct`, `AstFacts.modernization_hints`).
2. **Assumed-Shape Arrays & Explicit Interfaces**: Always place procedures inside `module`s so compilers check explicit interfaces, and pass assumed-shape arrays (`real(real64), intent(in) :: a(:,:)`) instead of unsafe assumed-size (`a(*)`) or explicit-size legacy arrays (`AstFacts.type_safety_issues`).
3. **Explicit `allocatable` & `optional` Guards**: Prefer `allocatable` over raw Fortran `pointer` (prevents leaks and aliasing), check `present(arg)` before accessing `optional` parameters, and check `stat=` on `allocate` / `iostat=` on `open`/`read`/`write`.
4. **C-Interop Safety (`iso_c_binding`)**: Use `bind(C)` and `c_double`/`c_int`/`c_ptr` explicitly at C/Python FFI seams.

## Evaluation Thresholds
- **`PASS`**: `iso_fortran_env` precision kinds, assumed-shape module interfaces, `allocatable` over raw `pointer`, and checked `iostat=`/`stat=` statuses.
- **`WARN`**: Isolated bare floating-point literals lacking `_wp` kind suffix or legacy `double precision`.
- **`FAIL`**: Implicit external procedures without interfaces, raw `pointer` leaks/aliasing, or non-standard `real*8`/`EQUIVALENCE` type punning.
