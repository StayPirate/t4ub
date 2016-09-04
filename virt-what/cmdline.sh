#!/bin/sh
<<Comment
Stop Booting if run into a virtual machine

This is an example script, it uses what-virt to detect if it's run eigther on a virtual
machine or not.
It should be puts as early_hook in the iso-scam's initramfs, hence to
avoid booting in an not host machines.
Comment

checkVMs() {
    local vm
    vm=" $(cat /proc/cmdline) "
    vm="${value##* vm=}"
    vm="${value%% *}"
    if [ "$vm" != "false" ]; then
      return 0
    fi
    return 1
}

if checkVMs; then
  # No kernel parameters to disable check found. Continue with check...
  vm_value="$(bin/virt-what)"
  if [ "$vm_value" != "" ]; then
    # VM detected. Stop booting
    echo "MACCHINA VIRTUALE"
  fi
fi
