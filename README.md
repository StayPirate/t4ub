<p align="center">
  <img src="https://wiki.staypirate.org/images/Skullbox.png"  height="150" width="150" alt="t4ub logo"/>
</p>
# Thanks For Your Box

**t4ub** is a framework which lets you easy modify the behavior of an [**initiramfs**](#initramfs).
For instance you can:
> * keylog luks's key of a root partition
> * wait for rebuild the real filesystem then deploy a backdoor just before the chroot
>  * send luks's key to your C2S
>  * reverse a rootshell

## Initramfs
It's not mandatory booting GNU/Linux with it, but since the configuration of OSes became much customizable, every distro uses it.
*Linux, the kernel, needs *userspace tools to make stuff**.

If the real filesystem (your OS) rely into logical volume (LVM, RAID) or root partition is reachable over network (NFS) or just encrypted (LUKS) then the kernel needs tools to rebuild, decrypt or configure a network interface before access the real OS.

*In other words initramfs is a little OS used for boot the real OS.*

####Bootchain is something like this:

Bootloader->Load kernel and decompressed initramfs in RAM->Kernel uses tools inside initramfs for rebuild and mount the real filesystem->Kernel chroot into the real filesystem

#### Where initramfs can be found?
Initramfs usually resides in the boot partition together with the kernel. The boot partition needs to be **not** encrypted to allow the bootloader boots the OS.

Some EFI bootloaders permit encryption of boot partition, but they require kernel and initramfs into ESP (Efi System Partition) that, again, must not be encrypted. Hence you'll still be able to modify the initramfs.

#### What does it seems?
```bash
$file /boot/initramfs-linux.img
/boot/initramfs-linux.img: gzip compressed data
```
It use to be a compressed archive, cpio or tar. Each distribution uses its prefered form.

#### How and when it's built?
There are different tools used to do that, and again it depend on the distro.
More known tools are *mkinitcpio* and *dracut*.
They  run automatically when you update kernel, generating the initramfs putting inside everything is needed for rebuild and mount the real filesystem.

> For instance those tools can puts inside the cpio some firmware needed from the kernel to use a wifi card or the cryptsetup static binary for decrypting the root partition.

## Why t4ub?
t4ub is able to quikly search one or more initramfs: uncompress it, patch it following [rules](#rules) that you give, then rebuild and replace it. *Everything in a few seconds.*

#### Rules
It's easy to interact with this framework, you just have to write rules into a YMAL file, in the config directory.

For instance this is a rule that copies an executable called *easteregg* into /bin directory of initramfs
```ymal
- rule_name: "copy backdoor"
  copy:
    - /bin/easteregg
  dest: /easteregg
```
More information of how to write rules can be found [here](config).

## Attack's vector
If you already have physical access to the (offline) disk, the boot partition or the ESP are not encrypted and you are able run t4ub letting it do the bad stuff to it.

But if you want run it **remotely**, you need to use some *social engineering*.

I thought to realize a customized GNU/Linux live distro.

When you run a live on your PC, **you let it access to entire your hard drive**.

Maybe you can think that is not a problem because your disk use encryption, but t4ub attacks the boot and the esp partition.

So meanwhile you are using the live, in background t4ub is mounting and analyzing your partitions looking for initramfs, everytime it find one it decompress, patch (infect) and rebuilt it.

### Virt-what
> *And what if the victim run the live in a *VM* instead of *their own machine*?*

Virt-what is a script maintained by **Red-Hat** that is able to understand if it is run under a virtualized environment or not.

I use it into the *live's bootchain* to make a simple check: if we are running in an VM, then we stop booting printing out an error like
> Virtual machine module error.

If we made a good job with *social engineering*, the victim is gonna run the iso (the live) without any hypervisor. And we'll have access to their boot/esp partition <3.
