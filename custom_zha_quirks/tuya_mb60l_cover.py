"""Custom ZHA quirk for Tuya TS0601 chain blind motor.

Device:
  Model: TS0601
  Manufacturer: _TZE284_2gi1hy8s
  Manual model: MB60L-ZIG-AT-TY
"""

from zigpy.profiles import zha
from zigpy.zcl.clusters.general import Basic, Groups, Ota, Scenes, Time

from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
)

from zhaquirks.tuya import (
    TuyaManufacturerWindowCover,
    TuyaManufCluster,
    TuyaWindowCover,
    TuyaWindowCoverControl,
)

TUYA_CLUSTER_ED00_ID = 0xED00


class TuyaMb60lZigAtTyCover(TuyaWindowCover):
    """Tuya MB60L-ZIG-AT-TY / TS0601 chain blind motor."""

    signature = {
        MODELS_INFO: [
            ("_TZE284_2gi1hy8s", "TS0601"),
        ],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.SMART_PLUG,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TUYA_CLUSTER_ED00_ID,
                    TuyaManufCluster.cluster_id,
                ],
                OUTPUT_CLUSTERS: [
                    Time.cluster_id,
                    Ota.cluster_id,
                ],
            },
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                DEVICE_TYPE: zha.DeviceType.WINDOW_COVERING_DEVICE,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TuyaManufacturerWindowCover,
                    TuyaWindowCoverControl,
                ],
                OUTPUT_CLUSTERS: [
                    Time.cluster_id,
                    Ota.cluster_id,
                ],
            },
        },
    }