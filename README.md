# T4UB

<p align="center">
  <img src="http://wiki.staypirate.org/images/Skullbox.png"  height="150" width="150" alt="t4ub logo"/>
</p>
This framework detects and edits [initramfs](#initramfs) archives from different kinds of partition.

For instance you could:
> * Deploy a keylogger to grab the input password to unlock a LUKS root partition.
> * Wait until the root filesystem has been rebuilt, hence copy a backdoor in it. Just before the boot-chain continue with the chroot.
>  * As soon as internet will be available, you can phone home and send back the grabbed key along with a copy of the LUKS header.
>  * Get root access via a reverse-shell.

## Initramfs

This is something quite common to find in today boot-chains. As more OSes configuration become complex, as more needing of a complete mini-system is needed during the boot process.

*The kernel Linux cannot do much without the right tools.* 

Think about the kernel like a naked man, and to the root filesystem (or in this case the initramfs) like clothes and daily tools.  
In the beginning, the kernel is mapped to the central memory and it starts to run, but in order to use the tools installed in the operative system, which reside into the root filesystem, he needs other tools to help hime to mount the root filesystem. This is where the initramfs finds its usefulness, it is a small temporary filesytem containing all the tools and modules needed to decrypt/rebuild/connect or just mount the root filesystem where the OS is located. Once this last partition is mounted the kernel executes a chroot (change root) and finally starts to use the main root filesystem, where all your software reside. Following the first example, think about the chroot as that man wearing the temporary clothes and tools, hence he removes them and he wears the ultimate clothes and tools. 

#### Where usually initramfs is located?

It's easy to find it in the partition where the kernel is stored, usually the boot partition or the [ESP](https://en.wikipedia.org/wiki/EFI_system_partition). These partitions need to not be encrypted to allow the bootloader boots the OS.

Even if some EFI bootloaders allows encryption of boot partition, they still require the kernel and the initramfs to be stored in plaintext into the ESP. Then you will still be able to tamper the initramfs.

#### What does the initramf looklike?

```bash
$file /boot/initramfs-linux.img
/boot/initramfs-linux.img: gzip compressed data
```
It's mostly a compressed archive, cpio or tar. Each distribution uses its own favorite design.

#### When and how it is built?

There are many different tools to generate an initramfs, and still, it depends which GNU/Linux distribution you are using. The more known automated tools are *mkinitcpio* and *dracut*. For instance, these are automatically triggered when you update your kernel.  
The creation of the initramfs is as easy as creating a file system directory, copying in it just the tools needed to mount the root partition early in the boot, along with their dependencies (libraries, modules, firmware, or even other tools).

## Why t4ub?

t4ub can quickly search one or more initramfs: uncompress them, patch them according to the [rules](#rules) you specify inside the framework, then rebuild and replace them in place of the original ones.

#### Rules

Rules are in YAML, and you can easily create new ones by adding them to the [config](/config) directory.

For instance, the following rule copies an executable called *malicious* into the /usr/bin directory of a found initramfs:
```ymal
- rule_name: "copy backdoor"
  copy:
    - /usr/bin/malicious
  dest: /malicious
```
More information about how to write rules can be found [here](config).

## Attack Scenario

If you already have physical access to the (offline) disk, you can just run t4ub from a a live USB stick and leave it to do the dirty work. 
But if you want to run it on a remote target, then you need to think about a *social engineering* scheme.  
If you run a live operative system on your computer, **you are actually leaving it access to your entire hard drive**. You may think there is not a problem since your hard disk is encrypted, but t4ub infects the boot or the ESP unencrypted partition. After your first successful boot, your root filesystem will be infected as well.  
Let say you have realized your custom GNU\Linux live distribution, you can now convince your victim to download and try it out on his asset. While he is discovering all the features of your new great live distro, in background t4ub is mounting all the unencrypted partitions looking for initramfses. For each match, it decompresses it, infects it and overrides it.

### Virt-what

> *What if the victim runs the live distro inside a VM, instead of run it on his physical machine?*

You won't be able to infect the host boot partition.

[Virt-what](https://people.redhat.com/rjones/virt-what/) is a **Red Hat** maintained script, it is able to figure out if the running environment is virtualized or not.

I use it during the boot-chain of the live distro I've made, and it makes a simple check: if the distro is running in a VM, it stops booting and prints out an error like: ```Virtual machine module error```. If we did a good job with our *social engineering* skills, the victim then may run the distro directly on his machine, and we finally get access to the host's boot/esp partition.
