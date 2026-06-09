from __future__ import annotations

import json
import unittest

from scripts.route_tasks import DEFAULT_CONFIG, route_task


def config_copy() -> dict:
    return json.loads(json.dumps(DEFAULT_CONFIG))


class RouteTasksTest(unittest.TestCase):
    def test_trivial_readme_routes_quick(self) -> None:
        route = route_task("Fix typo in README", "implementer", None, config_copy())
        self.assertEqual(route.tier, "T1")
        self.assertEqual(route.agent_type, "spc_quick")
        self.assertEqual(route.sandbox_mode, "workspace-write")
        self.assertEqual(route.hard_flags, [])

    def test_unknown_files_routes_explorer(self) -> None:
        route = route_task("Find relevant files; affected files unknown", "implementer", None, config_copy())
        self.assertEqual(route.tier, "T0")
        self.assertEqual(route.agent_type, "spc_explorer")
        self.assertEqual(route.sandbox_mode, "read-only")

    def test_security_data_forces_deep(self) -> None:
        route = route_task(
            "Add authentication migration with rollback and concurrency-safe token rotation",
            "implementer",
            None,
            config_copy(),
        )
        self.assertEqual(route.tier, "T4")
        self.assertEqual(route.agent_type, "spc_deep")
        self.assertEqual(sorted(route.hard_flags), ["data", "security"])

    def test_review_roles_are_read_only(self) -> None:
        spec = route_task("Check spec compliance for docs update", "spec-reviewer", None, config_copy())
        quality = route_task("Review security-sensitive data migration", "quality-reviewer", None, config_copy())
        final = route_task("Final branch review before release", "final-verifier", None, config_copy())
        self.assertEqual(spec.sandbox_mode, "read-only")
        self.assertEqual(quality.sandbox_mode, "read-only")
        self.assertEqual(final.sandbox_mode, "read-only")
        self.assertEqual(final.tier, "R3")

    def test_multi_file_api_integration_routes_standard(self) -> None:
        route = route_task(
            "Implement dashboard filter across frontend and backend API, multi-file integration around 700 lines, behavior inferred from existing UI tests",
            "implementer",
            None,
            config_copy(),
        )
        self.assertEqual(route.tier, "T3")
        self.assertEqual(route.agent_type, "spc_standard")

    def test_queue_idempotency_is_treated_as_data_risk(self) -> None:
        route = route_task(
            "Previously failed tests after weaker model changed queue idempotency",
            "implementer",
            None,
            config_copy(),
        )
        self.assertEqual(route.tier, "T4")
        self.assertEqual(sorted(route.hard_flags), ["data", "prior_failure"])

    def test_fallback_semantics_are_distinct(self) -> None:
        quick = route_task("Fix typo in README", "implementer", None, config_copy())
        quality = route_task("Review behavior change", "quality-reviewer", None, config_copy())
        final = route_task("Final branch review before release", "final-verifier", None, config_copy())

        self.assertEqual(quick.implementation_fallback_agent_type, "spc_spark")
        self.assertIsNone(quick.review_fallback_agent_type)
        self.assertEqual(quick.final_verification_policy, "not-required")
        self.assertEqual(quick.fallback_agent_type, "spc_spark")

        self.assertIsNone(quality.implementation_fallback_agent_type)
        self.assertEqual(quality.review_fallback_agent_type, "spc_final_verifier")
        self.assertEqual(quality.final_verification_policy, "recommended-for-hard-flags")

        self.assertIsNone(final.implementation_fallback_agent_type)
        self.assertIsNone(final.review_fallback_agent_type)
        self.assertEqual(final.final_verification_policy, "required-final-gate")


if __name__ == "__main__":
    unittest.main()
