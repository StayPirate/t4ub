# Thanks For Your Box

*t4ub* is divided in subdirectories each for a part of the toolchain

## injector

deve cercare la partizione di boot e tutti gli initramfs, decomprimerli aggiungere il lancio dell'eseguibile prima di switch_root e copiare l'eseguibile all'interno dello stesso.

## backdoor

La backdoor dovrebbe occuparsi di dumpare gli header delle partizioni cifrate e inserirle dentro /etc/sysdata.
Dovrebbe essere in grado di comprendere quando un header viene modificato e di dumpare gli header di nuovo.
Ad ogni aggiornamento di /etc/sysdata uploadare verso il nostro C2S.
È importante che renda permanente l'initramfs **patchato** andando ad avvelenare anche i file che vengono usati per generare un nuovo initramfs durante un aggiornamento. Ad esempio su Archlinux `/usr/lib/initcpio/`.
Deve accedere a cryptab e parsarlo per vedere dove sono salvate altre chiavi di decodifica o prendere le altre password degli altri device.
Dovrebbe inoltre cifrare i dati con una chiave pubblica... farlo nell'initramfs potrebbe essere pesante.

## TODO

Salvare tutte queste informazioni (header e chiavi) in un file, salvarlo (magari cifrandolo) in maniera nascosta all'interno della root decifrata e poi recuperarlo attraverso la backdoor, oppure farselo inviare non appena il pc infetto è connesso.
È importante copiare i dati nella root montata attraverso un run_latehook() in quanto prima devono essere partiti tutti gli altri hook, ad esempio LVM... una volta decifrato un disco potrebbe esserci LVM sopra e quindi deve prima essere ricostruito il volume logico e solo ad allora montare la vera root.
La cosa migliore è far montare la new_root nel giusto momento in cui viene fatta, ma prima dello switch_root inserire i comandi per copiare passw e iniettare il malware.

?? Si potrebbe portare nell'initramfs gpg ed importare una chiave copiandola in armour (base64)... forse è troppo ingombrate gpg, oppure implementare la crittografia asimmetrica all'interno del mw scritto in go.

Realizzare i test per le rules in yamal, un test deve creare un file con il codice da cercare nella regola e poi applicare la regola. Successivamente si riapre il file in sola lettura e si controlla che la regola sia stata applicata nel modo giusto.
Vedere prima un esempio di test, per capire come impostarli.
