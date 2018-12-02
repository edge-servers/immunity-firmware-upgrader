import mock
from django.core.exceptions import ValidationError
from django.test import TestCase

from .. import settings as app_settings
from ..hardware import FIRMWARE_IMAGE_MAP
from ..models import Build, Category, DeviceFirmware, FirmwareImage, UpgradeOperation
from .base import TestUpgraderMixin


class TestModels(TestUpgraderMixin, TestCase):
    def test_category_str(self):
        c = Category(name='WiFi Hotspot')
        self.assertEqual(str(c), c.name)

    def test_build_str(self):
        c = self._create_category()
        b = Build(category=c, version='0.1')
        self.assertIn(c.name, str(b))
        self.assertIn(b.version, str(b))

    def test_build_str_no_category(self):
        b = Build()
        self.assertIsNotNone(str(b))

    def test_fw_str(self):
        fw = self._create_firmware_image()
        self.assertIn(str(fw.build), str(fw))
        self.assertIn(fw.file.name, str(fw))

    def test_fw_str_new(self):
        fw = FirmwareImage()
        self.assertIsNotNone(str(fw))

    def test_device_firmware_image_invalid_org(self):
        device_fw = self._create_device_firmware()
        self._create_org(name='org2')
        img2 = self._create_firmware_image()
        device_fw.image = img2
        try:
            device_fw.full_clean()
        except ValidationError as e:
            self.assertIn('image', e.message_dict)
        else:
            self.fail('ValidationError not raised')

    @mock.patch('openwisp_firmware_upgrader.models.UpgradeOperation.upgrade', return_value=None)
    def test_device_fw_image_changed(self, *args):
        device_fw = DeviceFirmware()
        self.assertIsNone(device_fw._old_image)
        # save
        device_fw = self._create_device_firmware(upgrade=False)
        self.assertEqual(device_fw._old_image, device_fw.image)
        self.assertEqual(UpgradeOperation.objects.count(), 0)
        # init
        device_fw = DeviceFirmware.objects.first()
        self.assertEqual(device_fw._old_image, device_fw.image)
        # change
        build2 = self._create_build(category=device_fw.image.build.category,
                                    version='0.2')
        fw2 = self._create_firmware_image(build=build2, type=device_fw.image.type)
        old_image = device_fw.image
        device_fw.image = fw2
        self.assertNotEqual(device_fw._old_image, device_fw.image)
        self.assertEqual(device_fw._old_image, old_image)
        device_fw.full_clean()
        device_fw.save()
        self.assertEqual(UpgradeOperation.objects.count(), 1)

    @mock.patch('openwisp_firmware_upgrader.models.UpgradeOperation.upgrade', return_value=None)
    def test_device_fw_created(self, *args):
        self._create_device_firmware(upgrade=True)
        self.assertEqual(UpgradeOperation.objects.count(), 1)

    def test_device_fw_no_connection(self):
        try:
            self._create_device_firmware(device_connection=False)
        except ValidationError as e:
            self.assertIn('related connection', str(e))
        else:
            self.fail('ValidationError not raised')

    def test_invalid_board(self):
        image = FIRMWARE_IMAGE_MAP['ar71xx-generic-tl-wdr4300-v1-squashfs-sysupgrade.bin']
        boards = image['boards']
        del image['boards']
        err = None
        try:
            self._create_firmware_image()
        except ValidationError as e:
            err = e
        image['boards'] = boards
        if err:
            self.assertIn('type', err.message_dict)
            self.assertIn('not find boards', str(err))
        else:
            self.fail('ValidationError not raised')

    def test_custom_image_type_present(self):
        t = FirmwareImage._meta.get_field('type')
        custom_images = app_settings.CUSTOM_OPENWRT_IMAGES
        self.assertEqual(t.choices[0][0], custom_images[0][0])

    def test_device_firmware_image_invalid_model(self):
        device_fw = self._create_device_firmware()
        different_img = self._create_firmware_image(
            build=device_fw.image.build,
            type=self.TPLINK_4300_IL_IMAGE
        )
        try:
            device_fw.image = different_img
            device_fw.full_clean()
        except ValidationError as e:
            self.assertIn('model do not match', str(e))
        else:
            self.fail('ValidationError not raised')

    def test_upgrade_related_devices(self):
        env = self._create_upgrade_env()
        # check everything is as expected
        self.assertEqual(UpgradeOperation.objects.count(), 0)
        self.assertEqual(env['d1'].devicefirmware.image, env['image1a'])
        self.assertEqual(env['d2'].devicefirmware.image, env['image1b'])
        # upgrade all related
        env['build2'].upgrade_related_devices()
        # ensure image is changed
        env['d1'].devicefirmware.refresh_from_db()
        env['d2'].devicefirmware.refresh_from_db()
        self.assertEqual(env['d1'].devicefirmware.image, env['image2a'])
        self.assertEqual(env['d2'].devicefirmware.image, env['image2b'])
        # ensure upgrade operation objects have been created
        self.assertEqual(UpgradeOperation.objects.count(), 2)

    def test_upgrade_firmwareless_devices(self):
        env = self._create_upgrade_env(device_firmware=False)
        # check everything is as expected
        self.assertEqual(UpgradeOperation.objects.count(), 0)
        self.assertFalse(hasattr(env['d1'], 'devicefirmware'))
        self.assertFalse(hasattr(env['d2'], 'devicefirmware'))
        # upgrade all related
        env['build2'].upgrade_firmwareless_devices()
        env['d1'].refresh_from_db()
        env['d2'].refresh_from_db()
        self.assertEqual(env['d1'].devicefirmware.image, env['image2a'])
        self.assertEqual(env['d2'].devicefirmware.image, env['image2b'])
        # ensure upgrade operation objects have been created
        self.assertEqual(UpgradeOperation.objects.count(), 2)
