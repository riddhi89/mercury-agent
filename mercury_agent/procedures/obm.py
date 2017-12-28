# class BMCMethod(object):
#     name = ''
#
#     def __init__(self, handler):
#         self.handler = handler
#
#     def __call__(self, *args, **kwargs):
#         method = getattr(self.handler, self.name)
#         return method(*args, **kwargs)
#
#
#
# class OBMReset(BMCMethod):
#     name = 'reset_hard'
#
#
#
# obm_reset = OBMReset(handler)
# add_capability
# handler = get_bmc_handler(global_device_info['dmi']['sys_vendor'])
