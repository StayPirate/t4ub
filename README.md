# Thanks For Your Box

**t4ub** is a framework which let you easy modify the beavior of an **initiramfs**.
For instance you can:
> * keylog luks's key of a root partition
> * wait for rebuild the real filesystem then deploy a backdoor
>  * send luks's key to your C2S
>  * reverse a rootshell

## Initramfs
It's not mandatory to boot GNU/Linux withit, but since the configuration of OSes became much costumizable, every distro uses it.
*Linux, the kernel, needs *userspace tools to make stuff**. So if the real filesystem (your OS) rely in a logical volume (LVM, RAID) or root partition is reachable over networks (NFS) or just encrypted (LUKS) then the kernel needs tools to rebuild, decrypt or configure a network interface before access the real OS.

*In other words initramfs is a little OS used for boot the real OS.*

####Bootchain is something like this:

Bootloader->Load kernel and decompressed initramfs in RAM->Kernel use tools inside initramfs for rebuild and mount the real filesystem->Kernel chroot on real filesystem

#### Where initramfs can be found?
Initramfs usualy reside in the boot partition togheter with the kernel. The boot partition needs to be not encrypted to allow the bootloader boots the OS.
Some EFI bootloader permit to encrypt also the boot partition, but they require kernel and initramfs in the ESP (Efi System Partition) that, again, must not be encrypted. Hence you still able to modify the initramfs.

#### What it seems?
```bash
$file /boot/initramfs-linux.img
/boot/initramfs-linux.img: gzip compressed data
```
It use to be a compressed archive, cpio or tar.
Each distribution use it prefered form.

#### How and when it's built?
There are different tools used to do that, and again it depend of a distro.
More known tools are *mkinitcpio* and *dracut*.
They  run automaticaly when you update the kernel.
They generate the initramfs putting inside everything is needed for rebuild and mount the real filesystem.

>For instance they can put inside the cpio some firmware needed from the kernel to use a wifi card or the cryptsetup static binary for decrypting the root partition.

## Why t4ub?
t4ub is able to quikly search one or more initramfs: uncompress it, patch it following rules that you give, then rebuild and replace it. *Everything in a few seconds.*

#### Rules
It's easy to interact with this framework, you just have to write your rules into a YMAL file, in the config directory.

For instance this is a rule that copy an executable called *easteregg* into /bin directory of the initramfs
```ymal
- rule_name: "copy backdoor"
  copy:
    - /bin/easteregg
  dest: /easteregg
```
More information of how to write rules can be found [here](config).

## Attack's vector
If you have physical access to the (offline) disk, the boot partition or the ESP is not encrypted and you are able run t4ub letting it do the bad stuff.

But if you want run it **remotely**, you have to use *social engineering* component.

I thought to realize a custom GNU/Linux live distro.

When you run a live on your PC you let it have access to entire your hard drive. Maybe you can think that is not a problem because your disk use encryption, but t4ub attacks the boot and the esp partition.

So mainwhile you are trying the live, t4ub in background mount and analyze your partitions in search of initramfs, everytime it find one, it's gonna decompress, patch (infect) and rebuilt it.

### Virt-what
> *And what if the victim run the live in a **VM** instead in **their own machine**?*

Virt-what is a script manteined by **Red-Hat** that is able to understand if it is run under a virualized environment or not.

Then i use it into the live's *bootchain* for make a simple check: if we are in an VM we stop the boot printing an error like:
> Virtual machine module error.

If we made a good job with *social engineering*, the victim is going to run the iso (the live) without any hypervisor. And we'll have access to their boot/esp partition <3.
