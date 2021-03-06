from behave import *
import celestial_tools.client.rootfs
from features import utils
import filecmp
import celestial_tools
from celestial_tools.strings import Filesystems


@given(u'a rootfs file formatted with {rootfs_format}')
def step_impl(context, rootfs_format):
    # Generate a small ext3 formatted file
    context.rootfs_format = rootfs_format
    if rootfs_format == Filesystems.EXT2:
        context.rootfs_file = utils.make_ext2()
    elif rootfs_format == Filesystems.EXT3:
        context.rootfs_file = utils.make_ext3()
    elif rootfs_format == Filesystems.EXT4:
        context.rootfs_file = utils.make_ext4()
    else:
        raise ValueError("Unsupported rootfs type")


@given(u'a target device node')
def step_impl(context):
    # Generate a device node, the same size as the ext4_file above
    context.target_device_node = utils.make_device_node()


@given(u'we expect rootfs format {rootfs_format}')
def step_impl(context, rootfs_format):
    context.expected_rootfs_format = rootfs_format


@when(u'we invoke celestial_rootfs_install')
def step_impl(context):
    node = getattr(context, 'target_device_node', '/dev/null')
    expected_rootfs_format = getattr(context, 'expected_rootfs_format', None)
    try:
        context.celestial_rootfs_install_result = celestial_tools.client.rootfs.install(
            rootfs_file=context.rootfs_file,
            device_node=node,
            expected_fs=expected_rootfs_format
            )
    except ValueError as e:
        context.celestial_rootfs_install_result = e


@then("the rootfs file is burned into {expected_device_node}")
def step_impl(context, expected_device_node):
    if expected_device_node == "the target device node":
        expected_device_node = context.target_device_node
    else:
        expected_device_node = utils.prepend_temp_dir(expected_device_node)
    assert filecmp.cmp(context.rootfs_file, expected_device_node)


@then(u'{name} fails with {exception}')
def step_impl(context, name, exception):
    result = getattr(context, "{}_result".format(name))
    assert isinstance(result, eval(exception))
