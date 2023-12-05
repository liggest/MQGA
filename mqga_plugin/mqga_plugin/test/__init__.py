from mqga.log import log
log.debug("Test！ Test！")

from mqga.plugin import plugin_info

plugin_info(
    name="测试",
    author="liggest",
    version="0.0.1",
    description="真的测试"
)