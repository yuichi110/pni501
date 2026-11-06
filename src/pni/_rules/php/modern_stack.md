# Modern PHP Stack & Secure Idioms (PHP 8.2+)

## Core Principles
1. **Modern PHP 8.2–8.4 Idioms**: Leverage constructor property promotion, `readonly` classes, `match` expressions, nullsafe operator (`?->`), and PHP Attributes (`#[...]`) instead of verbose legacy boilerplate.
2. **Zero Removed / Deprecated Legacy Functions**: Eliminate legacy `mysql_*` functions, `create_function()`, `each()`, `extract($_REQUEST)`, `utf8_encode()`/`utf8_decode()`, and `preg_replace` `/e` modifiers.
3. **Strict Identity & Modern Cryptography**: Always use strict comparison (`===` / `!==`), `password_hash()` + `password_verify()` for passwords, `hash_equals()` for MAC/token verification (preventing `0e...` magic-hash type juggling), and `random_bytes()` / `random_int()` instead of `md5()`, `sha1()`, `rand()`, or `mt_rand()`.
4. **Operational Resilience**: Configure explicit connection/request timeouts on all `curl_setopt`, Guzzle, or Laravel `Http` client calls, centralize environment variables in config files, and log structured JSON via PSR-3 (`Psr\Log\LoggerInterface`) rather than `var_dump` / `print_r` / `echo`.
