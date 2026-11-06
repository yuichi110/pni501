# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tests for Java 2nd-language support across project inspection, AST analysis, actions, and workflows."""

from __future__ import annotations

import json
from pathlib import Path

from ast_grep_py import SgRoot

from pni._actions import (
    CategoryScores,
    PrimitiveType,
    ScoreResult,
    list_actions,
    load_composite_action,
    run_ast_analyze,
    run_project_inspect,
)
from pni._actions.ast_analyze import BaseDependencyChecker, ParsedUnit
from pni._actions.ast_analyze.java import JavaTypingChecker
from pni._actions.ast_analyze.python import PythonTypingChecker
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


def test_java_maven_project_inspect(tmp_path: Path) -> None:
    """Test Maven pom.xml inspection including property interpolation, test scope, and unpinned versions."""
    (tmp_path / "pom.xml").write_text(
        """<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.3.2</version>
  </parent>
  <groupId>com.example</groupId>
  <artifactId>order-service</artifactId>
  <version>2.1.0</version>
  <properties>
    <guava.version>33.2.1-jre</guava.version>
  </properties>
  <dependencies>
    <dependency>
      <groupId>com.google.guava</groupId>
      <artifactId>guava</artifactId>
      <version>${guava.version}</version>
    </dependency>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
      <groupId>commons-io</groupId>
      <artifactId>commons-io</artifactId>
      <version>LATEST</version>
    </dependency>
    <dependency>
      <groupId>org.junit.jupiter</groupId>
      <artifactId>junit-jupiter</artifactId>
      <version>5.10.3</version>
      <scope>test</scope>
    </dependency>
  </dependencies>
</project>
""",
        encoding="utf-8",
    )
    (tmp_path / "mvnw").write_text("#!/bin/sh\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Order Service\n\nJava Maven microservice.\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("target/\n", encoding="utf-8")

    src_dir = tmp_path / "src" / "main" / "java" / "com" / "example"
    test_dir = tmp_path / "src" / "test" / "java" / "com" / "example"
    src_dir.mkdir(parents=True)
    test_dir.mkdir(parents=True)
    (src_dir / "OrderService.java").write_text("package com.example;\npublic class OrderService {}\n", encoding="utf-8")
    (test_dir / "OrderServiceTest.java").write_text(
        "package com.example;\nclass OrderServiceTest {}\n",
        encoding="utf-8",
    )

    facts = run_project_inspect(tmp_path)
    assert facts.language == "java"
    assert facts.build_system == "maven"
    assert facts.project_name == "order-service"
    assert facts.version == "2.1.0"
    assert "pom.xml" in facts.manifest_files
    assert "mvnw" in facts.lockfiles_found
    assert "com.google.guava:guava:33.2.1-jre" in facts.dependencies
    # Managed by parent BOM -> treated as pinned
    assert "org.springframework.boot:spring-boot-starter-web" in facts.dependencies
    # Dynamic LATEST -> flagged as unpinned
    assert "commons-io:commons-io:LATEST" in facts.unpinned_dependencies
    assert "org.junit.jupiter:junit-jupiter:5.10.3" in facts.dev_dependencies
    assert facts.source_files_count == 1
    assert facts.test_files_count == 1
    assert facts.has_readme is True
    assert facts.has_gitignore is True


def test_java_gradle_project_inspect(tmp_path: Path) -> None:
    """Test Gradle Kotlin DSL inspection including settings.gradle.kts, catalog refs, and dynamic '+' versions."""
    (tmp_path / "settings.gradle.kts").write_text('rootProject.name = "payment-engine"\n', encoding="utf-8")
    (tmp_path / "build.gradle.kts").write_text(
        """plugins {
    java
}
group = "io.acme"
version = "0.9.0"

dependencies {
    implementation("org.slf4j:slf4j-api:2.0.13")
    implementation("com.zaxxer:HikariCP:5.+")
    implementation(libs.jackson.databind)
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
}
""",
        encoding="utf-8",
    )
    (tmp_path / "gradlew").write_text("#!/bin/sh\n", encoding="utf-8")
    (tmp_path / "gradle.lockfile").write_text("", encoding="utf-8")

    facts = run_project_inspect(tmp_path)
    assert facts.language == "java"
    assert facts.build_system == "gradle"
    assert facts.project_name == "payment-engine"
    assert facts.version == "0.9.0"
    assert "build.gradle.kts" in facts.manifest_files
    assert "settings.gradle.kts" in facts.manifest_files
    assert "gradle.lockfile" in facts.lockfiles_found
    assert "org.slf4j:slf4j-api:2.0.13" in facts.dependencies
    assert "libs.jackson.databind" in facts.dependencies
    assert "com.zaxxer:HikariCP:5.+" in facts.unpinned_dependencies
    assert "org.junit.jupiter:junit-jupiter:5.10.2" in facts.dev_dependencies


def test_java_ast_analyze_javadoc_generics_complexity_and_cycles(tmp_path: Path) -> None:
    """Test deterministic Java AST analysis for Javadoc, raw generics, weak types, static state, and cycles."""
    base_pkg = tmp_path / "src" / "main" / "java" / "com" / "acme"
    sub_pkg = base_pkg / "cycle"
    base_pkg.mkdir(parents=True)
    sub_pkg.mkdir(parents=True)

    # Clean, well-documented, generic-safe class with @Override method
    (base_pkg / "CleanService.java").write_text(
        """package com.acme;

import java.util.List;

/**
 * Clean service handling domain items.
 */
public class CleanService {
    private static final int MAX_ITEMS = 100;

    /**
     * Format item names cleanly.
     */
    public List<String> formatItems(List<String> items) {
        return items;
    }

    @Override
    public String toString() {
        return "CleanService:" + MAX_ITEMS;
    }
}
""",
        encoding="utf-8",
    )

    # Messy class: missing Javadoc, raw List & nested Map<String, List>, Object param,
    # @SuppressWarnings("unchecked"), mutable static field, and high branch complexity
    (base_pkg / "LegacyProcessor.java").write_text(
        """package com.acme;

import java.util.List;
import java.util.Map;

public class LegacyProcessor {
    public static int mutableCounter = 0;

    @SuppressWarnings("unchecked")
    public List processAll(Map<String, List> rawNested, Object payload, int mode) {
        if (mode == 1) {
            mutableCounter++;
        } else if (mode == 2) {
            mutableCounter += 2;
        } else if (mode == 3) {
            mutableCounter += 3;
        } else if (mode == 4) {
            mutableCounter += 4;
        } else if (mode == 5) {
            mutableCounter += 5;
        } else if (mode == 6) {
            mutableCounter += 6;
        } else if (mode == 7) {
            mutableCounter += 7;
        } else if (mode == 8) {
            mutableCounter += 8;
        }
        return null;
    }
}
""",
        encoding="utf-8",
    )

    # Same-package cyclic dependency between NodeA and NodeB
    (sub_pkg / "NodeA.java").write_text(
        """package com.acme.cycle;

/** Node A. */
public class NodeA {
    private NodeB partner;

    /** Link partner. */
    public NodeB getPartner() {
        return partner;
    }
}
""",
        encoding="utf-8",
    )
    (sub_pkg / "NodeB.java").write_text(
        """package com.acme.cycle;

/** Node B. */
public class NodeB {
    private NodeA owner;

    /** Link owner. */
    public NodeA getOwner() {
        return owner;
    }
}
""",
        encoding="utf-8",
    )

    facts = run_ast_analyze(tmp_path, targets=["src/main/java"])
    assert facts.language == "java"
    assert facts.total_files == 4
    assert facts.total_classes == 4
    assert facts.total_functions == 5

    # Only processAll has raw generic types -> 4/5 = 80.0%
    assert facts.type_safety_coverage_pct == 80.0
    assert len(facts.type_safety_issues) == 1
    issue = facts.type_safety_issues[0]
    assert issue.symbol == "processAll"
    assert "List" in issue.detail

    # Weak types: @SuppressWarnings("unchecked") + untyped Object parameter
    weak_symbols = {w.symbol for w in facts.weak_type_usages}
    assert "processAll" in weak_symbols
    assert len(facts.weak_type_usages) >= 2

    # Missing Javadocs: LegacyProcessor + processAll (CleanService.toString has @Override so exempted!)
    missing_doc_symbols = {m.symbol for m in facts.missing_docstrings}
    assert "LegacyProcessor" in missing_doc_symbols
    assert "processAll" in missing_doc_symbols
    assert "toString" not in missing_doc_symbols

    # Complexity: processAll has 8 if-branches (> MAX_BRANCH_COUNT=7)
    assert any(c.symbol == "processAll" for c in facts.complex_functions)

    # Mutable static non-final state: mutableCounter flagged, MAX_ITEMS (static final) NOT flagged
    global_symbols = {g.symbol for g in facts.global_state_usages}
    assert "mutableCounter" in global_symbols
    assert "MAX_ITEMS" not in global_symbols

    # Cyclic dependency detected between com.acme.cycle.NodeA and com.acme.cycle.NodeB
    assert "com.acme.cycle.NodeB" in facts.internal_import_graph.get("com.acme.cycle.NodeA", [])
    assert "com.acme.cycle.NodeA" in facts.internal_import_graph.get("com.acme.cycle.NodeB", [])
    assert len(facts.circular_dependencies) >= 1


def test_java_workflow_normalization_and_stateful_execution(tmp_path: Path) -> None:
    """Test initializing a Java project, normalizing Java actions, and running quick_check end-to-end."""
    (tmp_path / "pom.xml").write_text(
        "<project><groupId>com.demo</groupId><artifactId>app</artifactId><version>1.0.0</version></project>\n",
        encoding="utf-8",
    )
    src_pkg = tmp_path / "src" / "main" / "java" / "com" / "demo"
    src_pkg.mkdir(parents=True)
    (src_pkg / "Greeter.java").write_text(
        """package com.demo;

/** Greeter service. */
public class Greeter {
    /** Greet user. */
    public String greet(String name) {
        return "Hi " + name;
    }
}
""",
        encoding="utf-8",
    )

    init_project(tmp_path)  # Auto-detects Java from pom.xml
    actions = list_actions(tmp_path)
    action_ids = {a.id for a in actions}
    assert "java_ast_audit" in action_ids
    assert "java_test_audit" in action_ids
    assert "repo_structure_audit" in action_ids
    assert "emit_score" in action_ids

    java_comp = load_composite_action("java/repo_structure_audit", tmp_path)
    assert java_comp is not None
    assert "java/dependencies" in java_comp.rules

    loaded = load_workflow("quick_check", tmp_path)
    assert loaded is not None
    _, wf_def = loaded
    prims = normalize_workflow_steps(wf_def, tmp_path)
    assert [p.type for p in prims] == [
        PrimitiveType.PROJECT_INSPECT,
        PrimitiveType.AI_INTERPRET,
        PrimitiveType.AST_ANALYZE,
        PrimitiveType.AI_INTERPRET,
        PrimitiveType.EMIT_SCORE,
    ]

    run = start_workflow_run("quick_check", tmp_path)
    assert run is not None

    # Step 1: project_inspect (Java Maven)
    _, act1, guide1 = get_workflow_action(run.run_id, tmp_path)
    assert act1 is not None
    assert "build_system: `maven`" in guide1
    ok1, _ = push_workflow_action(run.run_id, act1.action_id, '{"acknowledged": true}', tmp_path)
    assert ok1 is True

    # Step 2: ai_interpret (repo_structure_audit -> includes java/dependencies rule)
    _, act2, guide2 = get_workflow_action(run.run_id, tmp_path)
    assert act2 is not None
    assert "Rule `java/dependencies`" in guide2
    interp1 = json.dumps({"summary": "Maven structure clean.", "findings": []})
    ok2, _ = push_workflow_action(run.run_id, act2.action_id, interp1, tmp_path)
    assert ok2 is True

    # Step 3: ast_analyze (Java AST)
    _, act3, guide3 = get_workflow_action(run.run_id, tmp_path)
    assert act3 is not None
    assert "language=`java`" in guide3
    assert "Type Safety Coverage**: `100.0%`" in guide3
    ok3, _ = push_workflow_action(run.run_id, act3.action_id, '{"acknowledged": true}', tmp_path)
    assert ok3 is True

    # Step 4: ai_interpret (java_ast_audit -> includes java/typing & java/code_quality)
    _, act4, guide4 = get_workflow_action(run.run_id, tmp_path)
    assert act4 is not None
    assert "Rule `java/typing`" in guide4
    interp2 = json.dumps({"summary": "Javadoc and generics clean.", "findings": []})
    ok4, _ = push_workflow_action(run.run_id, act4.action_id, interp2, tmp_path)
    assert ok4 is True

    # Step 5: emit_score
    _, act5, _ = get_workflow_action(run.run_id, tmp_path)
    assert act5 is not None
    score_json = ScoreResult(
        project_name="com.demo:app",
        workflow_id="quick_check",
        language="java",
        overall_score=94,
        category_scores=CategoryScores(
            architecture=95,
            code_quality=96,
            typing=100,
            testing=85,
            dependencies=94,
            documentation=94,
        ),
        findings=[],
        summary="Clean Java service.",
    ).model_dump_json()
    ok5, msg5 = push_workflow_action(run.run_id, act5.action_id, score_json, tmp_path)
    assert ok5 is True
    assert "COMPLETED" in msg5

    emitted = json.loads((tmp_path / "reports" / "quick_check_score.json").read_text(encoding="utf-8"))
    assert emitted["language"] == "java"
    assert emitted["metrics_snapshot"]["build_system"] == "maven"
    assert emitted["metrics_snapshot"]["type_safety_coverage_pct"] == 100.0

    db = WorkflowStateDB(tmp_path)
    final_run = db.get_run(run.run_id)
    assert final_run is not None
    assert final_run.status == RunStatus.COMPLETED


def test_isolated_checker_subclasses_on_parsed_unit() -> None:
    """Verify individual Python and Java checker subclasses operate cleanly on in-memory ParsedUnits."""
    java_src = "public class Demo { public java.util.List run(Object x) { return null; } }\n"
    java_unit = ParsedUnit(
        file_path=Path("Demo.java"),
        rel_path="Demo.java",
        source=java_src,
        root=SgRoot(java_src, "java").root(),
    )
    java_typing = JavaTypingChecker().check([java_unit])
    assert java_typing.type_safety_coverage_pct == 0.0
    assert len(java_typing.type_safety_issues) == 1
    assert len(java_typing.weak_type_usages) == 1

    py_src = "from typing import Any\ndef fn(x, y: Any):\n    return x\n"
    py_unit = ParsedUnit(
        file_path=Path("demo.py"),
        rel_path="demo.py",
        source=py_src,
        root=SgRoot(py_src, "python").root(),
    )
    py_typing = PythonTypingChecker().check([py_unit])
    assert py_typing.type_safety_coverage_pct == 0.0
    assert len(py_typing.type_safety_issues) == 1
    assert len(py_typing.weak_type_usages) == 1

    cycles = BaseDependencyChecker.detect_cycles({"a": ["b"], "b": ["c"], "c": ["a"]})
    assert ["a", "b", "c", "a"] in cycles
