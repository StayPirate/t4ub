# Thanks For Your Box

**t4ub** is a framework which let you easy modify the beavior of an **initiramfs**[^initramfs].
For instance you can:
> * keylog luks's key of a root partition
> * wait for rebuild the real filesystem then deploy a backdoor
>  * send luks's key to your C2S
>  * reverse a rootshell

## [^initramfs]: Initramfs
It's not mandatory to boot GNU/Linux withit, but since the configuration of OSes became much costumizable, every distro uses it.
*Linux, the kernel, needs **userspace tools to make stuff***. So if the real filesystem (your OS) relay in a logical volume (LVM, RAID) or root partition is reacable over networks (NFS) or just encrypted (LUKS) then the kernel needs tools to rebuild, decrypt or configure a network interface before access the real OS.

*In other words initramfs is a little OS used for boot the real OS.*

####Bootchain is something like this:

Bootloader->Load kernel and decompressed initramfs in RAM->Kernel use tools inside initramfs for rebuild and mount the real filesystem->Kernel chroot on real filesystem

#### Where initramfs can be found?
Initramfs usualy reside in the boot partition togheter with the kernel. The boot partition needs to be not encrypted to allow the bootloader boots the OS.
Some EFI bootloader permit to encrypt also the boot partition, but they require kernel and initramfs in the ESP (efi system partition) that, again, it must be not encrypted. Hence you still able to modify the initramfs.

#### What it seem?
```bash
$file /boot/initramfs-linux.img
/boot/initramfs-linux.img: gzip compressed data
```
It's use to be a compressed archive, cpio or tar.
Each distribution use a prefered form.

#### How and when it's built?
There are different tools used to do that, and again it depend of a distro.
More known tools are *mkinitcpio* and *drucut*.
They  run automaticaly when you update the kernel.
They generate the initramfs within everything is needed to rebuild and mount the real filesystem.

>For instance they can put inside the cpio some firmware needed from the kernel to use a wifi card or the cryptsetup static binary for decrypting the root partition.

## Why t4ub?
t4ub is able to quikly search one or more initramfs: uncompress it, patch it following rules that you give, then rebuild and replace it. *Everything in few seconds.*

#### Rules
It's easy to interact with this framework, you just have to write your rules into a file, written in YAML, in the config directory.
For instance this is a rules that copy an executable called *easteregg* into the /bin of the initramfs
```ymal
- rule_name: "copy backdoor"
  copy:
    - /bin/easteregg
  dest: /easteregg
```
More information of how to write rules can be found [here](config).

# Attack's vector
If you have physical access to the (offline) disk, the boot partition or the ESP is not encrypted and you can run t4ub and let it do the bad stuff.
But if you want to run remotely, you have to use a social engineering component.
I thought to realize a custom live GNU/Linux distro. When you run a live on your PC you let it have access to entire your hard drive. Maybe you can think that is not a problem because you disk use encryption, but t4ub attacks the boot and the esp partition. So mainwhile you are trying the live, t4ub in background mount and analyze your disk in search of initramfs, everytime it find one, it gonna decompress, patch (infect) and rebuilt it.

### Virt-what
> *And what if the victim run the live in a **VM** instead in **their own machine**?*

Virt-what is a script manteined by **Red-Hat** that is able to understand if it is run under a virualized environment or not.
It's easy, in the live's *bootchain* we can make a check: if we are in an VM we stop the boot printing an error like:
> Virtual machine module error.

If we made a good job with social engineering, the victim is going to run the iso (the live) without any hypervisor. And we'll have access to their boot/esp partition <3.
