# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tests for PHP dual-mode support (Modern Composer/Laravel & Legacy Raw-PHP/WordPress)."""

from __future__ import annotations

import json
from pathlib import Path

from pni._actions import (
    CategoryScores,
    ScoreResult,
    list_actions,
    load_composite_action,
    run_ast_analyze,
    run_project_inspect,
)
from pni._actions.ast_analyze.php._helpers import normalize_php_source_for_cst
from pni._actions.runtime_check.parsers import parse_clover_xml
from pni._actions.runtime_check.selector import (
    build_test_and_coverage_command,
    compute_harness_build_args,
    select_harness_tool,
    select_php_image_version,
)
from pni._actions.runtime_check.smoke import build_smoke_plan, classify_boot_failure
from pni._dockerfiles import ensure_target_dockerfile
from pni._rules.manager import detect_active_language
from pni._workflows import (
    RunStatus,
    WorkflowStateDB,
    get_workflow_action,
    load_workflow,
    normalize_workflow_steps,
    push_workflow_action,
    start_workflow_run,
)
from pni.cli import init_project


def test_php_composer_laravel_project_inspect(tmp_path: Path) -> None:
    """Inspect a Composer/Laravel PHP project, verifying lockfile, PSR-4, frameworks, and vendor exclusion."""
    (tmp_path / "composer.json").write_text(
        json.dumps(
            {
                "name": "acme/order-api",
                "version": "1.2.0",
                "require": {
                    "php": "^8.3",
                    "laravel/framework": "^11.0",
                    "guzzlehttp/guzzle": "dev-main",
                },
                "require-dev": {
                    "phpunit/phpunit": "^11.2",
                    "phpstan/phpstan": "^1.11",
                },
                "autoload": {"psr-4": {"App\\": "app/"}},
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "composer.lock").write_text('{"packages": []}\n', encoding="utf-8")
    (tmp_path / "artisan").write_text("#!/usr/bin/env php\n<?php\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Order API\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("/vendor/\n.env\n", encoding="utf-8")

    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "OrderService.php").write_text(
        "<?php\nnamespace App;\nclass OrderService {}\n",
        encoding="utf-8",
    )
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "index.php").write_text("<?php\necho 'ok';\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "OrderServiceTest.php").write_text("<?php\nclass OrderServiceTest {}\n", encoding="utf-8")

    # Vendor files must never be counted as application source or test files
    vendor_dir = tmp_path / "vendor" / "laravel" / "framework"
    vendor_dir.mkdir(parents=True)
    (vendor_dir / "Kernel.php").write_text("<?php\nclass Kernel {}\n", encoding="utf-8")
    (vendor_dir / "KernelTest.php").write_text("<?php\nclass KernelTest {}\n", encoding="utf-8")

    assert detect_active_language(tmp_path) == "php"
    facts = run_project_inspect(tmp_path)
    assert facts.language == "php"
    assert facts.build_system == "composer"
    assert facts.project_name == "acme/order-api"
    assert facts.version == "1.2.0"
    assert facts.language_version_constraint == "^8.3"
    assert "composer.lock" in facts.lockfiles_found
    assert "laravel" in facts.detected_frameworks
    assert "phpstan" in facts.detected_frameworks
    assert "phpunit" in facts.detected_frameworks
    assert "guzzlehttp/guzzle:dev-main" in facts.unpinned_dependencies
    assert facts.source_files_count == 2
    assert facts.test_files_count == 1
    assert facts.tooling_modernization_issues == []
    assert facts.runtime_types == ["web_api"]


def test_php_raw_and_wordpress_project_inspect(tmp_path: Path) -> None:
    """Inspect Composer-less Raw PHP and WordPress plugin repositories, including EOL PHP warnings."""
    raw_dir = tmp_path / "legacy_shop"
    raw_dir.mkdir()
    (raw_dir / "index.php").write_text("<?php echo 'shop'; ?>\n", encoding="utf-8")
    (raw_dir / "login.php").write_text("<?php echo 'login'; ?>\n", encoding="utf-8")

    assert detect_active_language(raw_dir) == "php"
    raw_facts = run_project_inspect(raw_dir)
    assert raw_facts.language == "php"
    assert raw_facts.build_system == "raw_php"
    assert raw_facts.source_files_count == 2
    assert raw_facts.test_files_count == 0
    assert raw_facts.runtime_types == ["web_api"]
    assert any("Missing composer.json" in msg for msg in raw_facts.tooling_modernization_issues)

    wp_dir = tmp_path / "wp_plugin"
    wp_dir.mkdir()
    (wp_dir / "member-portal.php").write_text(
        """<?php
/**
 * Plugin Name: Member Analytics Portal
 * Version: 2.4.1
 * Requires PHP: 7.4
 */
add_action('init', 'map_boot');
""",
        encoding="utf-8",
    )
    wp_facts = run_project_inspect(wp_dir)
    assert wp_facts.language == "php"
    assert wp_facts.build_system == "raw_php"
    assert wp_facts.version == "2.4.1"
    assert wp_facts.language_version_constraint == ">=7.4"
    assert "wordpress" in wp_facts.detected_frameworks
    assert any("EOL PHP version constraint" in msg for msg in wp_facts.tooling_modernization_issues)


def test_php_ast_clean_strict_service_and_tests(tmp_path: Path) -> None:
    """Verify strict modern PHP 8.3 classes and PHPUnit/Pest suites achieve 100% typing/doc scores."""
    (tmp_path / "composer.json").write_text(
        json.dumps(
            {
                "name": "acme/clean-php",
                "require": {"php": "^8.3"},
                "autoload": {"psr-4": {"App\\": "app/"}},
            }
        ),
        encoding="utf-8",
    )
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "OrderDto.php").write_text(
        """<?php

declare(strict_types=1);

namespace App;

/**
 * Immutable input payload for creating an order.
 */
final readonly class OrderDto
{
    /**
     * Construct a validated order payload.
     *
     * @param string $sku Product SKU identifier.
     * @param int $quantity Positive unit count.
     */
    public function __construct(
        public string $sku,
        public int $quantity,
    ) {
    }
}
""",
        encoding="utf-8",
    )
    (app_dir / "OrderService.php").write_text(
        """<?php

declare(strict_types=1);

namespace App;

/**
 * Domain service calculating totals and verifying HMAC signatures.
 */
final class OrderService
{
    /**
     * Compute line total in cents.
     *
     * @param OrderDto $dto Validated order input.
     * @param int $unitPriceCents Unit price in cents.
     */
    public function calculateTotal(OrderDto $dto, int $unitPriceCents): int
    {
        return $dto->quantity * $unitPriceCents;
    }
}
""",
        encoding="utf-8",
    )

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "OrderServiceTest.php").write_text(
        """<?php

declare(strict_types=1);

namespace Tests;

use App\\OrderDto;
use App\\OrderService;
use PHPUnit\\Framework\\Attributes\\Test;
use PHPUnit\\Framework\\TestCase;

final class OrderServiceTest extends TestCase
{
    public function testCalculateTotal(): void
    {
        $svc = new OrderService();
        $this->assertSame(600, $svc->calculateTotal(new OrderDto('SKU-1', 3), 200));
    }

    #[Test]
    public function emptySmokeWithoutAssert(): void
    {
        $dto = new OrderDto('SKU-2', 1);
    }
}

it('supports pest expectations', function (): void {
    expect(1 + 1)->toBe(2);
});
""",
        encoding="utf-8",
    )

    facts = run_ast_analyze(tmp_path, targets=["app"], test_targets=["tests"], lang="php")
    assert facts.total_files == 2
    assert facts.type_safety_coverage_pct == 100.0
    assert facts.type_safety_issues == []
    assert facts.weak_type_usages == []
    assert facts.docstring_coverage_pct == 100.0
    assert facts.doc_signature_mismatches == []
    assert facts.dangerous_sinks == []
    assert facts.test_functions_count == 3
    assert len(facts.assertion_free_tests) == 1
    assert facts.assertion_free_tests[0].symbol == "OrderServiceTest::emptySmokeWithoutAssert"
    assert facts.module_test_coverage_pct == 100.0


def test_php_ast_mixed_html_and_legacy_spaghetti_sinks(tmp_path: Path) -> None:
    """Verify mixed HTML+PHP CST normalization and legacy Raw-PHP CWE sink & endpoint detection."""
    mixed_src = """<!DOCTYPE html>
<html>
<body>
<h1>Search: <?= $_GET['q'] ?></h1>
<?php
define('DB_PASSWORD', 'SuperSecretProdPass!2026');
$conn = @mysqli_connect('localhost', 'root', DB_PASSWORD, 'shop');
$id = $_GET['id'];
$res = mysqli_query($conn, "SELECT * FROM products WHERE id = " . $id);
$cart = unserialize($_COOKIE['cart']);
$pw_hash = md5($_POST['password']);
if ($pw_hash == $expected_hash) {
    echo $_POST['welcome_banner'];
}
if (isset($_GET['page'])) {
    include $_GET['page'] . '.php';
}
$diag = shell_exec("ping -c 1 " . $_GET['host']);
eval($_POST['hook']);
?>
</body>
</html>
"""
    norm = normalize_php_source_for_cst(mixed_src)
    assert norm.count("\n") == mixed_src.count("\n")

    (tmp_path / "product.php").write_text(mixed_src, encoding="utf-8")
    facts = run_ast_analyze(tmp_path, targets=["."], lang="php")
    assert facts.total_files == 1
    assert facts.type_safety_coverage_pct == 0.0

    cwes = {s.cwe_id for s in facts.dangerous_sinks}
    assert "CWE-79" in cwes  # <?= $_GET['q'] ?> and echo $_POST[...]
    assert "CWE-89" in cwes  # mysqli_query concatenation
    assert "CWE-502" in cwes  # unserialize($_COOKIE['cart'])
    assert "CWE-327" in cwes  # md5($_POST['password'])
    assert "CWE-697" in cwes  # loose == on $pw_hash
    assert "CWE-98" in cwes  # dynamic include $_GET['page']
    assert "CWE-78" in cwes  # shell_exec
    assert "CWE-94" in cwes  # eval

    # Verify 1:1 line preservation on short echo tag `<?= $_GET['q'] ?>` (line 4)
    xss_lines = {s.line for s in facts.dangerous_sinks if s.cwe_id == "CWE-79"}
    assert 4 in xss_lines

    assert any(sec.symbol == "DB_PASSWORD" for sec in facts.hardcoded_secrets)
    assert any("@mysqli_connect" in b.detail for b in facts.bug_risk_idioms)
    assert any("Spaghetti script mixes inline HTML" in b.detail for b in facts.bug_risk_idioms)
    assert any(g.detail.startswith("Direct superglobal") for g in facts.global_state_usages)

    # Raw PHP web entry endpoint extraction
    assert len(facts.api_endpoints) == 1
    ep = facts.api_endpoints[0]
    assert ep.path == "/product.php"
    assert ep.http_method == "ANY"
    assert ep.has_auth_hint is False


def test_php_ast_laravel_symfony_and_wordpress_checkers(tmp_path: Path) -> None:
    """Verify Laravel, Symfony Attribute, and WordPress framework & endpoint analyzers."""
    laravel_dir = tmp_path / "laravel_app"
    (laravel_dir / "app" / "Http" / "Controllers").mkdir(parents=True)
    (laravel_dir / "routes").mkdir(parents=True)
    (laravel_dir / "artisan").write_text("#!/usr/bin/env php\n", encoding="utf-8")

    (laravel_dir / "app" / "User.php").write_text(
        """<?php
namespace App;
class User {
    protected $guarded = [];
    public function getFullNameAttribute() { return 'x'; }
}
""",
        encoding="utf-8",
    )
    (laravel_dir / "app" / "Http" / "Controllers" / "OrderController.php").write_text(
        """<?php
namespace App\\Http\\Controllers;
use Symfony\\Component\\Routing\\Attribute\\Route;
use Symfony\\Component\\Security\\Http\\Attribute\\IsGranted;

#[Route('/v1/orders')]
class OrderController {
    #[Route('/export', methods: ['GET'])]
    #[IsGranted('ROLE_ADMIN')]
    public function store($request) {
        $key = env('STRIPE_SECRET');
        \\DB::table('orders')->get();
        return $this->repo->create($request->all());
    }
}
""",
        encoding="utf-8",
    )
    (laravel_dir / "routes" / "api.php").write_text(
        """<?php
Route::get('/orders', [OrderController::class, 'index'])->middleware('auth:sanctum');
Route::post('/webhooks/stripe', [WebhookController::class, 'handle']);
""",
        encoding="utf-8",
    )

    l_facts = run_ast_analyze(
        laravel_dir,
        targets=["app", "routes"],
        lang="php",
        detected_frameworks=["laravel"],
    )
    fw_details = "\n".join(loc.detail for loc in l_facts.framework_issues)
    assert "$guarded = []" in fw_details
    assert "DB::table" in fw_details
    assert "$request->all()" in fw_details
    assert "Direct 'env()'" in fw_details
    assert any("getFullNameAttribute" in h.symbol for h in l_facts.modernization_hints)

    by_path = {ep.path: ep for ep in l_facts.api_endpoints}
    assert by_path["/api/orders"].has_auth_hint is True
    assert by_path["/api/webhooks/stripe"].has_auth_hint is False
    assert by_path["/v1/orders/export"].has_auth_hint is True

    # WordPress plugin checks
    wp_dir = tmp_path / "wp_plugin"
    wp_dir.mkdir()
    (wp_dir / "plugin-ajax.php").write_text(
        """<?php
register_rest_route('analytics/v1', '/export', [
    'methods' => 'GET',
    'callback' => 'map_export_rows',
    'permission_callback' => '__return_true',
]);

add_action('wp_ajax_nopriv_search_members', 'map_search_members');

function map_search_members() {
    global $wpdb;
    $term = $_POST['term'];
    $rows = $wpdb->get_results("SELECT * FROM wp_users WHERE display_name LIKE '%" . $term . "%'");
    echo $_GET['callback'];
}
?>
<script src="/wp-content/plugins/map/raw.js"></script>
""",
        encoding="utf-8",
    )

    wp_facts = run_ast_analyze(
        wp_dir,
        targets=["."],
        lang="php",
        detected_frameworks=["wordpress"],
    )
    wp_fw = "\n".join(loc.detail for loc in wp_facts.framework_issues)
    assert "ABSPATH" in wp_fw
    assert "wp_verify_nonce()" in wp_fw
    assert "current_user_can" in wp_fw
    assert "Unsanitized superglobal" in wp_fw
    assert any("wp_enqueue_script" in h.symbol for h in wp_facts.modernization_hints)

    wp_cwes = {s.cwe_id for s in wp_facts.dangerous_sinks}
    assert "CWE-89" in wp_cwes
    assert "CWE-79" in wp_cwes

    wp_eps = {ep.path: ep for ep in wp_facts.api_endpoints}
    assert wp_eps["/wp-json/analytics/v1/export"].has_auth_hint is False
    assert wp_eps["/wp-admin/admin-ajax.php?action=search_members"].has_auth_hint is False


def test_php_runtime_check_helpers_and_clover_parser(tmp_path: Path) -> None:
    """Test PHP version/harness selection, Clover XML parsing, boot error classification, and smoke plans."""
    assert select_php_image_version(None) == "8.3"
    assert select_php_image_version("~8.1") == "8.1"
    assert select_php_image_version("~8.2") == "8.2"
    assert select_php_image_version("^8.2") == "8.3"
    assert select_php_image_version(">=8.4") == "8.4"
    assert select_php_image_version("^7.4") == "8.2"

    # Composer web project
    comp_dir = tmp_path / "composer_web"
    (comp_dir / "public").mkdir(parents=True)
    (comp_dir / "composer.json").write_text('{"name":"x/y","require":{"php":"^8.3"}}', encoding="utf-8")
    (comp_dir / "public" / "index.php").write_text("<?php echo 'ok';", encoding="utf-8")
    comp_pf = run_project_inspect(comp_dir)
    assert select_harness_tool(comp_pf) == "composer"
    assert compute_harness_build_args(comp_pf) == {"PHP_VERSION": "8.3"}

    df_path, _ = ensure_target_dockerfile(tmp_path, "composer_web", "php", "composer")
    assert df_path == tmp_path / ".pni" / "dockerfiles" / "composer_web" / "Dockerfile"
    assert df_path.is_file()
    assert "composer:2" in df_path.read_text(encoding="utf-8")

    cmd = build_test_and_coverage_command(comp_pf, "composer", ["app"], ["tests"])
    assert cmd[0] == "sh"
    assert "php -l" in cmd[2]
    assert "coverage-clover" in cmd[2]

    arch, smoke_cmd = build_smoke_plan(comp_dir, comp_pf, ["app"])
    assert arch == "web_api"
    assert smoke_cmd is not None and "php -S" in smoke_cmd[2]
    assert "public/index.php" in smoke_cmd[2]
    assert "'$paths = " in smoke_cmd[2]

    # WordPress plugin smoke plan
    wp_dir = tmp_path / "wp_plug"
    wp_dir.mkdir()
    (wp_dir / "plug.php").write_text("<?php\n/*\nPlugin Name: Demo\n*/\n", encoding="utf-8")
    wp_pf = run_project_inspect(wp_dir)
    assert select_harness_tool(wp_pf) == "raw"
    _, wp_smoke = build_smoke_plan(wp_dir, wp_pf, ["."])
    assert wp_smoke is not None and wp_smoke[:2] == ["php", "-r"]
    assert "ABSPATH" in wp_smoke[2]

    # Clover XML parser
    clover_file = tmp_path / "clover.xml"
    clover_file.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<coverage generated="1729750000">
  <project timestamp="1729750000">
    <file name="/workspace/app/OrderService.php">
      <line num="10" type="stmt" count="3"/>
      <line num="11" type="stmt" count="3"/>
      <line num="14" type="stmt" count="0"/>
      <metrics statements="3" coveredstatements="2" conditionals="2" coveredconditionals="1"/>
    </file>
  </project>
</coverage>
""",
        encoding="utf-8",
    )
    cov = parse_clover_xml(clover_file, workspace_prefix="/workspace/")
    assert cov.measured is True
    assert cov.tool == "phpunit-pcov"
    assert cov.line_coverage_pct == 66.7
    assert cov.branch_coverage_pct == 50.0
    assert len(cov.lowest_covered_modules) == 1
    assert cov.lowest_covered_modules[0].file_path == "app/OrderService.php"
    assert cov.lowest_covered_modules[0].missing_lines_preview == [14]

    # PHP boot failure classification
    parse_err = "PHP Parse error: syntax error, unexpected token '}' in /workspace/a.php"
    assert classify_boot_failure(parse_err, timed_out=False) == "import_or_di_error"
    assert (
        classify_boot_failure(
            "PHP Fatal error: Uncaught Error: Class 'App\\Foo' not found",
            timed_out=False,
        )
        == "import_or_di_error"
    )
    assert (
        classify_boot_failure("SQLSTATE[HY000] [2002] Connection refused", timed_out=False)
        == "external_service_unreachable"
    )


def test_php_init_actions_and_stateful_workflow(tmp_path: Path) -> None:
    """Verify `pni init --lang php` scaffolds valid PHP actions and runs `quick_check` end-to-end."""
    (tmp_path / "composer.json").write_text(
        '{"name":"demo/php-svc","version":"1.0.0","require":{"php":"^8.3"},'
        '"autoload":{"psr-4":{"App\\\\":"app/"}}}\n',
        encoding="utf-8",
    )
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "Greeter.php").write_text(
        """<?php

declare(strict_types=1);

namespace App;

/** Greeter service. */
final class Greeter
{
    /**
     * Greet a user.
     *
     * @param string $name User display name.
     */
    public function greet(string $name): string
    {
        return 'Hello ' . $name;
    }
}
""",
        encoding="utf-8",
    )

    init_project(tmp_path, lang="php")
    loaded = load_workflow("quick_check", tmp_path)
    assert loaded is not None
    _, wf_def = loaded
    steps = normalize_workflow_steps(wf_def, tmp_path)
    assert len(steps) == 5

    actions = list_actions(tmp_path)
    action_ids = {a.id for a in actions}
    assert "php_ast_audit" in action_ids
    assert "php_test_audit" in action_ids
    php_ast = load_composite_action("php_ast_audit", tmp_path)
    assert php_ast is not None
    assert "php/code_quality" in php_ast.rules
    assert "php/frameworks/wordpress" in php_ast.rules

    run = start_workflow_run("quick_check", tmp_path)
    assert run is not None

    # Step 1: project_inspect
    _, act1, guide1 = get_workflow_action(run.run_id, tmp_path)
    assert act1 is not None and "build_system: `composer`" in guide1
    assert push_workflow_action(run.run_id, act1.action_id, '{"acknowledged": true}', tmp_path)[0] is True

    # Step 2: ai_interpret (repo_structure_audit)
    _, act2, guide2 = get_workflow_action(run.run_id, tmp_path)
    assert act2 is not None and "Rule `php/dependencies`" in guide2
    assert (
        push_workflow_action(
            run.run_id,
            act2.action_id,
            json.dumps({"summary": "Composer setup checked.", "findings": []}),
            tmp_path,
        )[0]
        is True
    )

    # Step 3: ast_analyze (PHP AST)
    _, act3, guide3 = get_workflow_action(run.run_id, tmp_path)
    assert act3 is not None and "language=`php`" in guide3
    assert "Type Safety Coverage**: `100.0%`" in guide3
    assert push_workflow_action(run.run_id, act3.action_id, '{"acknowledged": true}', tmp_path)[0] is True

    # Step 4: ai_interpret (php_ast_audit)
    _, act4, guide4 = get_workflow_action(run.run_id, tmp_path)
    assert act4 is not None and "Rule `php/typing`" in guide4
    assert (
        push_workflow_action(
            run.run_id,
            act4.action_id,
            json.dumps({"summary": "Strict types and PHPDoc clean.", "findings": []}),
            tmp_path,
        )[0]
        is True
    )

    # Step 5: emit_score
    _, act5, _ = get_workflow_action(run.run_id, tmp_path)
    assert act5 is not None
    score_json = ScoreResult(
        project_name="demo/php-svc",
        workflow_id="quick_check",
        language="php",
        overall_score=93,
        category_scores=CategoryScores(
            architecture=94,
            code_quality=95,
            typing=100,
            testing=80,
            dependencies=94,
            documentation=95,
        ),
        findings=[],
        summary="Clean PHP 8.3 service.",
    ).model_dump_json()
    ok5, msg5 = push_workflow_action(run.run_id, act5.action_id, score_json, tmp_path)
    assert ok5 is True and "COMPLETED" in msg5

    db = WorkflowStateDB(tmp_path)
    final_run = db.get_run(run.run_id)
    assert final_run is not None and final_run.status == RunStatus.COMPLETED


def test_php_imports_dependencies_and_operational_checkers(tmp_path: Path) -> None:
    """Verify PSR-12 import order, circular namespaces, Composer deps, boundaries, timeouts, env, and logging."""
    (tmp_path / "composer.json").write_text(
        json.dumps(
            {
                "name": "acme/dep-audit",
                "require": {
                    "php": "^8.3",
                    "monolog/monolog": "^3.7",
                },
                "autoload": {"psr-4": {"App\\": "app/"}},
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "app" / "Domain").mkdir(parents=True)
    (tmp_path / "app" / "Http" / "Controllers").mkdir(parents=True)

    # Alpha imports OrderController (boundary violation + cycle with OrderController) and unsorted `use` + UndeclaredPkg
    (tmp_path / "app" / "Domain" / "AlphaOrder.php").write_text(
        """<?php
namespace App\\Domain;

use Stripe\\StripeClient;
use App\\Http\\Controllers\\OrderController;

class AlphaOrder
{
    public function sync(): void
    {
        require_once 'legacy_helper.php';
        $ch = curl_init('https://api.example.com/orders');
        $raw = file_get_contents('https://api.example.com/status');
        $client = new \\GuzzleHttp\\Client();
        $apiKey = getenv('PAYMENT_API_KEY');
        $region = $_ENV['APP_REGION'];
        var_dump($ch, $raw, $client, $apiKey, $region);
    }
}
""",
        encoding="utf-8",
    )
    (tmp_path / "app" / "Http" / "Controllers" / "OrderController.php").write_text(
        """<?php
namespace App\\Http\\Controllers;

use App\\Domain\\AlphaOrder;

class OrderController
{
    public function handle(AlphaOrder $order): void
    {
        $order->sync();
    }
}
""",
        encoding="utf-8",
    )

    facts = run_ast_analyze(tmp_path, targets=["app"], lang="php")
    assert len(facts.unsorted_imports) >= 1
    assert len(facts.late_imports) >= 1
    assert len(facts.circular_dependencies) >= 1
    assert "monolog/monolog" in facts.unused_dependencies
    assert any(u.symbol == "Stripe\\StripeClient" for u in facts.undeclared_dependencies)
    assert len(facts.boundary_violations) == 1
    assert len(facts.missing_io_timeouts) == 3
    assert len(facts.scattered_env_access) == 2
    assert any("var_dump" in loc.detail for loc in facts.unstructured_logging)

