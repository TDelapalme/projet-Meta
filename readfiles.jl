using DelimitedFiles

global r, c, b, m, t;

function readfile(fname, id)    #id=le numÃ©ro d'instance, de 0 Ã  nbInst-1
    all = readdlm(fname);
    nbInst   = all[1,1];
    @assert(id<nbInst);
    deb = 2;                #instance 0 commence Ã  ligne deb
    global m = all[2,1];
    global t = all[2,2];
    for i in 1:id
        deb += 2m+2;        #sauter instance i (2m+2 lignes)
        global m = all[deb,1];    
        global t = all[deb,2];    
    end
    global c = all[deb+1:deb+m,   1:t];
    global r = all[deb+m+1:deb+2m,1:t];
    global b = all[deb+2m+1,      1:m];
    return;
end

#Attention: cette lecture ne fonctionne pas si le ficher n'est pas alignÃ© sous format matriciel
#des instances disponibles Ã  cedric.cnam.fr/~porumbed/
readfile("gapd.txt",5);