# WordPress Plugin & Theme Security Standards (PHP)

Apply when `wordpress` is present in `ProjectFacts.detected_frameworks`. Mark `not_applicable` when the project is not a WordPress plugin, theme, or site.

## Core Principles
1. **Direct-Access Guard (`ABSPATH`)**: Every plugin or theme PHP file must guard against direct web invocation at file entry (`if (!defined('ABSPATH')) { exit; }`).
2. **CSRF Nonces & Capability Checks**: Every state-mutating hook (`admin_post_*`, `wp_ajax_*`, `save_post`, settings forms) must verify both a cryptographic Nonce (`wp_verify_nonce()` / `check_admin_referer()` / `check_ajax_referer()`) AND user authorization (`current_user_can(...)`).
3. **REST API & Admin-AJAX Hardening**: Every `register_rest_route()` must supply an explicit `permission_callback` (never use `'__return_true'` on privileged or data-exporting routes), and `wp_ajax_nopriv_*` must never expose administrative or PII-mutating operations.
4. **Prepared `$wpdb` SQL & Late Escaping**: Sanitize inputs early (`wp_unslash()` + `sanitize_text_field()` / `absint()`), parameterize every custom `$wpdb` SQL statement via `$wpdb->prepare(...)`, escape all output late (`esc_html()`, `esc_attr()`, `esc_url()`, `wp_kses_post()`), and register assets via `wp_enqueue_script()` / `wp_enqueue_style()`.
