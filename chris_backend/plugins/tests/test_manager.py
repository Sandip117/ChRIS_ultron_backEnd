
import os, shutil

from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings

from plugins.models import Plugin, PluginParameter, PluginInstance
from plugins.services.manager import PluginManager

import time

import pudb

class PluginManagerTests(TestCase):
    
    def setUp(self):
        self.plugin_fs_docker_image_name = "fnndsc/pl-simplefsapp"
        self.plugin_fs_name = "simplefsapp"
        self.plugin_fs_parameters = {'dir': {'type': 'string', 'optional': False}}
        self.plugin_ds_name = "simpledsapp"
        self.plugin_ds_docker_image_name = "fnndsc/pl-simpledsapp"
        self.username = 'foo'
        self.password = 'foo-pass'
        self.pl_manager = PluginManager()

        # create a plugin
        (plugin_fs, tf) = Plugin.objects.get_or_create( name        = self.plugin_fs_name,
                                                        dock_image  = self.plugin_fs_docker_image_name,
                                                        type        = 'fs')
        # add plugin's parameters
        PluginParameter.objects.get_or_create(
            plugin=plugin_fs,
            name='dir',
            type=self.plugin_fs_parameters['dir']['type'],
            optional=self.plugin_fs_parameters['dir']['optional'])

        # create user
        user = User.objects.create_user(username=self.username,
                                        password=self.password)

    def test_mananger_can_get_plugin_app_representation(self):
        """
        Test whether the manager can return a plugin's app representation given the
        plugin's name.
        """
        plugin = Plugin.objects.get(name=self.plugin_fs_name)
        app_repr = self.pl_manager.get_plugin_app_representation(self.plugin_fs_docker_image_name)
        self.assertEquals(plugin.type, app_repr['type'])
        self.assertIn('parameters', app_repr)

    def test_mananger_can_get_plugin(self):
        """
        Test whether the manager can return a plugin object.
        """
        plugin = Plugin.objects.get(name=self.plugin_fs_name)
        self.assertEquals(plugin, self.pl_manager.get_plugin(self.plugin_fs_name))
        
    def test_mananger_can_add_plugin(self):
        """
        Test whether the manager can add a new plugin app to the system.
        """
        self.pl_manager.run(['--add', self.plugin_ds_docker_image_name])
        self.assertEquals(Plugin.objects.count(), 2)
        self.assertTrue(PluginParameter.objects.count() > 1)

    def test_mananger_can_remove_plugin(self):
        """
        Test whether the manager can remove an existing plugin app from the system.
        """
        self.pl_manager.run(['--remove', self.plugin_fs_name])
        self.assertEquals(Plugin.objects.count(), 0)
        self.assertEquals(PluginParameter.objects.count(), 0)

    def test_mananger_can_register_plugin_app_modification_date(self):
        """
        Test whether the manager can register a new modification date for an
        existing plugin app.
        """
        plugin = Plugin.objects.get(name=self.plugin_fs_name)
        initial_modification_date = plugin.modification_date
        time.sleep(2)
        self.pl_manager.run(['--modify', self.plugin_fs_docker_image_name])
        plugin = Plugin.objects.get(name=self.plugin_fs_name)
        self.assertTrue(plugin.modification_date > initial_modification_date)

    def test_mananger_can_run_registered_plugin_app(self):
        """
        Test whether the manager can run an already registered plugin app.

        NB: Note the directory overrides on input and output dirs! This
            is file system space in the plugin container, and thus by hardcoding
            this here we are relying on totally out-of-band knowledge! 

            This must be fixed in later versions!
        """
         # create test directory where files are created
        test_dir = settings.MEDIA_ROOT + '/test'
        settings.MEDIA_ROOT = test_dir
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)

        user = User.objects.get(username=self.username)
        plugin = Plugin.objects.get(name=self.plugin_fs_name)
        pl_inst = PluginInstance.objects.create(plugin=plugin, owner=user)
        parameter_dict = {'dir': './'}

        # pudb.set_trace()
        self.pl_manager.check_apps_exec_server(     clearDB             = True,
                                                    service             = 'pfcon',
                                                    IOPhost             = 'pangea')
        self.pl_manager.run_plugin_app(             pl_inst,
                                                    parameter_dict,
                                                    service             = 'pfcon',
                                                    inputDirOverride    = '/share/incoming',
                                                    outputDirOverride   = '/share/outgoing',
                                                    IOPhost             = 'pangea'
        )
        time.sleep(10)
        # self.assertTrue(os.path.isfile(os.path.join(pl_inst.get_output_path(), 'out.txt')))

        # remove test directory 
        shutil.rmtree(test_dir)
        # and shutdown apps_exec_server -- not necessary in new design.
        # self.pl_manager.shutdown_apps_exec_server()
        settings.MEDIA_ROOT = os.path.dirname(test_dir)

    def test_mananger_can_check_plugin_app_exec_status(self):
        """
        Test whether the manager can check a plugin's app execution status.

        NB: Note the directory overrides on input and output dirs! This
            is file system space in the plugin container, and thus by hardcoding
            this here we are relying on totally out-of-band knowledge! 

            This must be fixed in later versions!
        """
        # create test directory where files are created
        test_dir = settings.MEDIA_ROOT + '/test'
        settings.MEDIA_ROOT = test_dir
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)

        user = User.objects.get(username=self.username)
        plugin = Plugin.objects.get(name=self.plugin_fs_name)
        pl_inst = PluginInstance.objects.create(plugin=plugin, owner=user)
        parameter_dict = {'dir': './'}

        # pudb.set_trace()
        self.pl_manager.check_apps_exec_server(     clearDB             = True,
                                                    service             = 'pfcon',
                                                    IOPhost             = 'pangea')
        self.pl_manager.run_plugin_app(             pl_inst, 
                                                    parameter_dict,
                                                    service             = 'pfcon',
                                                    inputDirOverride    = '/share/incoming',
                                                    outputDirOverride   = '/share/outgoing',
                                                    IOPhost             = 'pangea'
        )
        time.sleep(10)
        self.pl_manager.check_plugin_app_exec_status(pl_inst)
        possibleStatus =  ['started', 'finishedSuccessfully']
        self.assertTrue(pl_inst.status in possibleStatus)

        # remove test directory 
        shutil.rmtree(test_dir)
        # and shutdown apps_exec_server -- not necessary in new design.
        # self.pl_manager.shutdown_apps_exec_server()
        settings.MEDIA_ROOT = os.path.dirname(test_dir)


