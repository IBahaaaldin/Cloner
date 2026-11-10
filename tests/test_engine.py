import os
import plistlib
import shutil
import subprocess
import unittest
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import cloner_engine

class TestClonerEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_sandbox'))
        os.makedirs(self.test_dir, exist_ok=True)
        self.engine = cloner_engine.ClonerEngine(cloner_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_scan_installed_apps(self):
        apps = self.engine.scan_installed_apps()
        self.assertIsInstance(apps, list)
        app_names = [a['name'] for a in apps]
        # At least one of our target apps should be detected on this Mac
        target_found = any(k in app_names for k in ['ChatGPT', 'Claude', 'AntiGravity', 'AntiGravity IDE'])
        self.assertTrue(target_found, f"None of target apps found in {app_names}")

    def test_create_app_clone_and_list(self):
        apps = self.engine.scan_installed_apps()
        self.assertGreater(len(apps), 0)
        target_app = apps[0]
        
        result = self.engine.create_app_clone(
            app_path=target_app['path'],
            profile_name="TestProfile",
            badge_color="#3B82F6"
        )
        self.assertTrue(result['success'], result.get('error'))
        clone_app_path = result['clone_path']
        self.assertTrue(os.path.exists(clone_app_path))
        self.assertTrue(os.path.exists(os.path.join(clone_app_path, "Contents", "Info.plist")))
        self.assertTrue(os.path.exists(os.path.join(clone_app_path, "Contents", "MacOS", target_app['executable_name'])))

        # Check listing
        clones = self.engine.list_active_clones()
        self.assertEqual(len(clones), 1)
        self.assertEqual(clones[0]['profile_name'], "TestProfile")
        self.assertEqual(clones[0]['base_app_name'], target_app['name'])

        # Check deletion
        del_res = self.engine.delete_app_clone(clone_app_path, remove_data=True)
        self.assertTrue(del_res)
        self.assertFalse(os.path.exists(clone_app_path))

    def test_sync_app_clone_updates_outdated_bundle(self):
        data_root = os.path.join(self.test_dir, "data_root")
        engine = cloner_engine.ClonerEngine(cloner_dir=self.test_dir, data_root=data_root)
        apps = engine.scan_installed_apps()
        target_app = apps[0]

        result = engine.create_app_clone(
            app_path=target_app['path'],
            profile_name="SyncTest",
            badge_color="#F59E0B"
        )
        self.assertTrue(result['success'], result.get('error'))
        clone_path = result['clone_path']
        data_dir = result['data_dir']

        # Put sentinel user file inside isolated data dir to verify zero data loss
        sentinel_file = os.path.join(data_dir, "data", "session_sentinel.json")
        os.makedirs(os.path.dirname(sentinel_file), exist_ok=True)
        with open(sentinel_file, "w") as f:
            f.write('{"account":"user_b"}')

        # Simulate older cloned bundle version & remove CLONER_SYNC_ATTEMPTED marker
        plist_path = os.path.join(clone_path, "Contents", "Info.plist")
        with open(plist_path, "rb") as f:
            plist = plistlib.load(f)
        real_version = plist.get("CFBundleShortVersionString", "")
        plist["CFBundleShortVersionString"] = "0.0.1-old"
        with open(plist_path, "wb") as f:
            plistlib.dump(plist, f)

        launcher_path = os.path.join(clone_path, "Contents", "MacOS", target_app['executable_name'])
        with open(launcher_path, "w") as f:
            f.write("#!/bin/bash\n# legacy wrapper without sync\n")

        clones = engine.list_active_clones()
        self.assertEqual(len(clones), 1)
        self.assertTrue(clones[0]['needs_update'])
        self.assertFalse(clones[0]['has_auto_sync'])

        sync_res = engine.sync_app_clone(clone_path)
        self.assertTrue(sync_res['success'], sync_res.get('error'))
        self.assertTrue(sync_res['updated'])
        self.assertEqual(sync_res['old_version'], "0.0.1-old")
        self.assertEqual(sync_res['new_version'], real_version)

        # Verify restored version, auto-sync launcher, sentinel data, and codesign
        clones_after = engine.list_active_clones()
        self.assertEqual(len(clones_after), 1)
        self.assertFalse(clones_after[0]['needs_update'])
        self.assertTrue(clones_after[0]['has_auto_sync'])
        self.assertTrue(os.path.exists(sentinel_file))
        cs_res = subprocess.run(["codesign", "--verify", "--deep", clone_path], capture_output=True, text=True)
        self.assertEqual(cs_res.returncode, 0, cs_res.stderr)

        shutil.rmtree(clone_path, ignore_errors=True)

if __name__ == '__main__':
    unittest.main()
