from immunity_firmware_upgrader.admin import (  # noqa
    BatchUpgradeOperationAdmin,
    BuildAdmin,
    CategoryAdmin,
    DeviceUpgradeOperationInline,
    UpgradeOperationForm,
)

BatchUpgradeOperationAdmin.fields.append('details')
UpgradeOperationForm.Meta.fields.append('details')
DeviceUpgradeOperationInline.fields.append('details')
