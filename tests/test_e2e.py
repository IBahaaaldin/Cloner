import os
import sys
import unittest
import plistlib
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import cloner_engine

class TestClonerE2E(unittest.TestCase):
    def setUp(self):
        self.cloner_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.engine = cloner_engine.ClonerEngine(cloner_dir=self.cloner_dir)

    def test_e2e_full_workflow(self):
        # 1. Scan installed apps
        apps = self.engine.scan_installed_apps()
        # Case-insensitive lookup
        app_by_name = {a['name'].lower(): a for a in apps}

        print("\n--- Detected Applications ---")
        for name, a in app_by_name.items():
            if a.get('is_featured'):
                print(f"  • {a['name']} [{a['type']}] -> {a['path']}")

        self.assertIn("chatgpt", app_by_name)
        self.assertIn("claude", app_by_name)
        self.assertTrue("antigravity" in app_by_name or "antigravity ide" in app_by_name)

        # 2. Test AntiGravity clone
        target_ag = app_by_name.get("antigravity") or app_by_name.get("antigravity ide")
        res_ag = self.engine.create_app_clone(
            app_path=target_ag['path'],
            profile_name="E2E Work",
            badge_color="#3B82F6"
        )
        self.assertTrue(res_ag['success'])
        ag_clone_path = res_ag['clone_path']
        self.assertTrue(os.path.exists(ag_clone_path))

        # Check plist
        with open(os.path.join(ag_clone_path, "Contents", "Info.plist"), "rb") as f:
            plist = plistlib.load(f)
        self.assertEqual(plist["ClonerProfileName"], "E2E Work")
        self.assertTrue(plist["CFBundleIdentifier"].startswith("com.cloner."))
        self.assertTrue(os.path.exists(plist["ClonerDataDir"]))
        # Verify secure 0700 permissions
        data_stat = os.stat(plist["ClonerDataDir"])
        self.assertEqual(oct(data_stat.st_mode)[-3:], "700", f"Insecure permissions: {oct(data_stat.st_mode)}")

        # Check launcher script
        launcher_path = os.path.join(ag_clone_path, "Contents", "MacOS", "launcher")
        self.assertTrue(os.path.exists(launcher_path))
        with open(launcher_path, "r") as f:
            launcher_content = f.read()
        self.assertIn("--user-data-dir", launcher_content)

        # Check ad-hoc codesign
        cs_res = subprocess.run(["codesign", "--verify", "--deep", ag_clone_path], capture_output=True, text=True)
        self.assertEqual(cs_res.returncode, 0, f"Codesign verification failed: {cs_res.stderr}")

        # 3. Test Claude clone
        claude_app = app_by_name["claude"]
        res_claude = self.engine.create_app_clone(
            app_path=claude_app['path'],
            profile_name="E2E Research",
            badge_color="#10B981"
        )
        self.assertTrue(res_claude['success'])
        claude_clone_path = res_claude['clone_path']
        self.assertTrue(os.path.exists(claude_clone_path))

        # 4. Test ChatGPT clone
        chatgpt_app = app_by_name["chatgpt"]
        res_chatgpt = self.engine.create_app_clone(
            app_path=chatgpt_app['path'],
            profile_name="E2E Personal",
            badge_color="#8B5CF6"
        )
        self.assertTrue(res_chatgpt['success'])
        chatgpt_clone_path = res_chatgpt['clone_path']
        self.assertTrue(os.path.exists(chatgpt_clone_path))

        # 5. List clones
        clones = self.engine.list_active_clones()
        clone_profiles = [c['profile_name'] for c in clones]
        self.assertIn("E2E Work", clone_profiles)
        self.assertIn("E2E Research", clone_profiles)
        self.assertIn("E2E Personal", clone_profiles)

        print(f"\n--- Verified {len(clones)} Active Clones in Desktop/Cloner ---")
        for c in clones:
            print(f"  ✓ {c['name']} (ID: {c['bundle_id']})")

        # 6. Clean up the E2E test clones
        self.engine.delete_app_clone(ag_clone_path, remove_data=True)
        self.engine.delete_app_clone(claude_clone_path, remove_data=True)
        self.engine.delete_app_clone(chatgpt_clone_path, remove_data=True)

        self.assertFalse(os.path.exists(ag_clone_path))
        self.assertFalse(os.path.exists(claude_clone_path))
        self.assertFalse(os.path.exists(chatgpt_clone_path))
        print("  ✓ Cleanup of test clones completed successfully.")

if __name__ == '__main__':
    unittest.main()
