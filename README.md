# T4UB

<p align="center">
  <img src="https://i.ibb.co/sJ0dvyf/Skullbox.png"  height="150" width="150" alt="t4ub logo"/>
</p>
This framework detects and edits [initramfs](#initramfs) archives from different kinds of partition.

For instance you could:
> * Deploy a keylogger to grab the input password to unlock a LUKS root partition.
> * Wait for the root filesystem to be rebuilt, then copy a backdoor in it. Just right before the boot-chain goes on with the chroot.
>  * As soon as an internet connection is going to be available, you'll be able to phone home and send back the grabbed key along with a copy of the LUKS header.
>  * Get root access through a reverse-shell.

## Initramfs

This is something quite common to find in nowadays OSes boot-chain. As the complexity of today's OSes grows so does the complexity of the mini-systems required to setup of the formers during their boot process.

*The Linux kernel cannot do much without the right tools.* 

Think about the kernel like a naked man, and of the root filesystem (or in this case the initramfs) like clothes and as tools of your daily routine.  
In the beginning, the kernel is mapped to the central memory and executed, but in order to use the tools installed on the operative system, which resides into the root filesystem, it requires addittional tools to mount the root filesystem. This is where the initramfs finds its usefulness, it's a small temporary filesytem containing all the tools and modules needed to decrypt/rebuild/connect or just mount the root filesystem. Once this last partition is mounted the kernel executes a chroot command (change root) and finally switches to the main root filesystem, where all your software resides. Following the first example, think of the chroot as the aforementioned man wearing a pajmas (temporary clothes), then in order to get ready for work he puts on a suit and a tie. 

#### Where is initramfs usually located?

You can find it in the same partition where the kernel is stored, usually the boot partition or the [ESP](https://en.wikipedia.org/wiki/EFI_system_partition). These partitions need to not be encrypted to allow the bootloader to boot the OS.

Even if some EFI bootloaders allow encrypted boot partitions, they still require the kernel and the initramfs to be stored in plaintext on the ESP. Meaning that 
you'll still be able to tamper the initramfs.

#### What does the initramf looklike?

```bash
$file /boot/initramfs-linux.img
/boot/initramfs-linux.img: gzip compressed data
```
It's mostly a compressed archive, cpio or tar. Each distribution uses its own design.

#### When and how it is built?

There are many different tools to generate an initramfs, and still, it depends which GNU/Linux distribution you are using. The most known automated tools are *mkinitcpio* and *dracut*. For instance, these are automatically triggered when you update your kernel.  
The creation of the initramfs is as easy as creating a file system directory, copying in it just the tools needed to mount the root partition in the early stages of the boot process, along with their dependencies (libraries, modules, firmware, or even other tools).

## Why t4ub?

t4ub can quickly look for one or more initramfs': extract them, patch them according to the [rules](#rules) you specify inside the framework, then rebuild andput them in place of the original ones.

#### Rules

The Rules are stored in a YAML, and you can easily add new ones to the [config](/config) directory.

For instance, the following rule copies an executable called *malicious* into the /usr/bin directory of a found initramfs:
```ymal
- rule_name: "copy backdoor"
  copy:
    - /usr/bin/malicious
  dest: /malicious
```
More information about how to write rules can be found [here](config).

## Attack Scenario

If you already gained physical access to the (offline) disk, you can just run t4ub from a live USB stick and let it to do all the dirty work for you. 
But if you want to run it on a remote target, then you'll need to cme up with a *social engineering* scheme.  
If you're already running a live system on your computer, You're not safe **the live system would still have access to your entire hard drive**. You might be fooled in to thinking that since your hard disk is encrypted t4ub wouldn-t pose any threat for you, but t4ub actually works by infecting the boot or the ESP unencrypted partition. After your first successful boot, your root filesystem will be infected as well.  
Let's say you've just built your own custom GNU\Linux live distribution, now you just beed to convince your victim to download and try it out on his asset. Distracted by discovering all the features of your new freashly built "great live" distro, t4ub mounting all the unencrypted partitions looking for initramfs images in the background. For each match, it decompresses it, infects it and replaces it.

### Virt-what

> *What if the victim runs the live distro inside a VM, instead of running it on his physical machine?*

You won't be able to infect the host boot partition.

[Virt-what](https://people.redhat.com/rjones/virt-what/) is a **Red Hat** maintained script, it is able to figure out if the running environment is virtualized or not.

I employ it during the boot-chain of the live distro, and runs a simple check: if the distro is running in a VM, it stops booting and prints out an error like: ```Virtual machine module error```. If we did a good job with our *social engineering* skills, the victim then may run the distro directly on his machine, and we finally gain access to the host's boot/esp partition.
