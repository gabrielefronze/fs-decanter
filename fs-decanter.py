#!/usr/bin/env python3

import argparse
import os
import shutil
from distutils.dir_util import copy_tree
from subprocess import check_call
from os.path import expanduser

def is_mounted(mount_point: str) -> bool:
    return os.path.ismount(mount_point)


def remount_if_fstab(mount_point: str) -> bool:

  check_call(['mount', expanduser(mount_point)])

  return is_mounted(mount_point)


def decant(source_path: str, dest_path: str) -> bool:
  
  for file_name in os.listdir(source_path):

    full_file_name = os.path.join(source_path, file_name)
    dest_file_name = os.path.join(dest_path, file_name)

    if os.path.isdir(full_file_name):
      print("\tCopying full directory: {}".format(full_file_name))
      copy_tree(full_file_name, dest_file_name)
    else:
      print("\tCopying file: {}".format(full_file_name))
      shutil.copy(full_file_name, dest_file_name)

    if os.path.exists(dest_file_name):
      if os.path.isdir(dest_file_name):
        shutil.rmtree(full_file_name)
      else:
        os.remove(full_file_name)
      print("\tDone!")
    else:
      raise Exception("An error occurred when copying {}. Aborting.".format(full_file_name))
      return False
  
  return True


def run_decanter(buffer_path: str, mount_path: str) -> bool:
  if is_mounted(mount_path):
    print("Decanting from {} to {}:".format(buffer_path, mount_path))
    return decant(buffer_path, mount_path)
  else:
    print("Remote not mounted locally. Aborting.")
    return False


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Decant files and directories from a source path to an SSHFS endpoint.')
  parser.add_argument('buffer_path', help='Source path for the files to be decanted')
  parser.add_argument('dest_mount_path', help='Network filesystem local mountpoint')
  parser.add_argument('-a', '--auto', help='Automatically trigger a "mount --all" before proceeding')

  args = parser.parse_args()
  
  if not os.path.exists(args.buffer_path):
    raise Exception("Buffer path not found. Aborting.")

  if not os.path.exists(args.dest_mount_path):
    raise Exception("Local mountpoint not found. Aborting.")

  if args.auto:
    if not remount_if_fstab(args.dest_mount_path):
      raise Exception("Unable to mount. Aborting.")

  run_decanter(buffer_path=args.buffer_path, mount_path=args.dest_mount_path)