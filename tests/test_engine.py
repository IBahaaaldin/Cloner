import os
import shutil
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
        self.assertTrue(os.path.exists(os.path.join(clone_app_path, "Contents", "MacOS", "launcher")))

        # Check listing
        clones = self.engine.list_active_clones()
        self.assertEqual(len(clones), 1)
        self.assertEqual(clones[0]['profile_name'], "TestProfile")
        self.assertEqual(clones[0]['base_app_name'], target_app['name'])

        # Check deletion
        del_res = self.engine.delete_app_clone(clone_app_path, remove_data=True)
        self.assertTrue(del_res)
        self.assertFalse(os.path.exists(clone_app_path))

if __name__ == '__main__':
    unittest.main()
