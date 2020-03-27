
per modificare la directory data ho creato il file:
    /etc/default/mongodb
        # Default defaults.  /etc/default/$NAME
        CONF=/etc/Ln_mongodb.conf

lo script /etc/init.d/mongodb verifica la presenza del file
/etc/default/$NAME per cercare variabili utente per fare override
di quelle previste.
con la riga di sopra modifico il file di configurazione dove all'interno
ho modificato il percorso del data_base

    dbpath=/mnt/k/Filu/LnDisk/GIT-REPO/Mongo/DBdata


L'alternativa sarebbe quella di creare un link simbolico ma potrebbero essere device diversi
https://tecadmin.net/change-mongodb-default-data-path/


COME NON DETTO
In questo modo mongodb non parte. Forse perché non ha gli attributi necessari
quindoi l'unico modo che ho è quello di fare il backup dei dati.