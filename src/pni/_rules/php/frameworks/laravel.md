# Laravel Architecture & Security Standards (PHP)

Apply when `laravel` is present in `ProjectFacts.detected_frameworks`. Mark `not_applicable` when the project does not use Laravel / Illuminate components.

## Core Principles
1. **Mass-Assignment Protection**: Explicitly define `protected $fillable = [...]` on Eloquent models and prohibit `protected $guarded = [];` or passing `$request->all()` directly into `Model::create()` / `update()`.
2. **Configuration Cache Safety**: Never call `env('...')` outside `config/*.php` files (use `config('...')` in application classes so `php artisan config:cache` does not silently return `null` in production).
3. **Thin Controllers & Validated Requests**: Validate inputs via dedicated `FormRequest` classes or `$request->validate([...])` DTOs, enforce `auth:sanctum` / Policy authorization middleware on routes, and delegate persistence/business rules to Service/Action classes rather than writing `DB::table` or `DB::raw` inside Controllers.
4. **Parameterized Query Builder & Blade Escaping**: Use Eloquent / Query Builder parameter bindings instead of interpolated `DB::raw()` / `whereRaw()`, and avoid unescaped Blade `{!! ... !!}` output on user-supplied strings.
